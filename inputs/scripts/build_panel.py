#!/usr/bin/env python3
"""Offline, deterministic input build. Python >=3.9 standard library only. No model fitting."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import xml.etree.ElementTree as ET
import zipfile

BASE = Path(__file__).resolve().parents[1]
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
STATES = dict(line.split("|", 1) for line in """AL|Alabama
AK|Alaska
AZ|Arizona
AR|Arkansas
CA|California
CO|Colorado
CT|Connecticut
DE|Delaware
FL|Florida
GA|Georgia
HI|Hawaii
ID|Idaho
IL|Illinois
IN|Indiana
IA|Iowa
KS|Kansas
KY|Kentucky
LA|Louisiana
ME|Maine
MD|Maryland
MA|Massachusetts
MI|Michigan
MN|Minnesota
MS|Mississippi
MO|Missouri
MT|Montana
NE|Nebraska
NV|Nevada
NH|New Hampshire
NJ|New Jersey
NM|New Mexico
NY|New York
NC|North Carolina
ND|North Dakota
OH|Ohio
OK|Oklahoma
OR|Oregon
PA|Pennsylvania
RI|Rhode Island
SC|South Carolina
SD|South Dakota
TN|Tennessee
TX|Texas
UT|Utah
VT|Vermont
VA|Virginia
WA|Washington
WV|West Virginia
WI|Wisconsin
WY|Wyoming""".splitlines())
PANEL_FIELDS = ["stateabbr", "state", "year", "population_thousands",
                "electricity_co2_mmt", "industry_co2_mmt", "electricity_co2_tpc", "industry_co2_tpc"]

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_csv(path, rows, fields=None):
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

def read_workbook(path):
    """Extract original OOXML stored values; no spreadsheet engine or recalculation needed."""
    with zipfile.ZipFile(path) as z:
        strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            strings = ["".join(s.itertext()) for s in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
        relationships = {x.attrib["Id"]: x.attrib["Target"] for x in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        result = {}
        for sheet in ET.fromstring(z.read("xl/workbook.xml")).findall("m:sheets/m:sheet", NS):
            target = relationships[sheet.attrib[REL]].lstrip("/")
            if not target.startswith("xl/"):
                target = "xl/" + target
            cells = {}
            for c in ET.fromstring(z.read(target)).findall(".//m:sheetData/m:row/m:c", NS):
                assert c.find("m:f", NS) is None, "Unexpected formula in source"
                value = c.find("m:v", NS)
                if value is not None:
                    cells[c.attrib["r"]] = strings[int(value.text)] if c.attrib.get("t") == "s" else value.text
                elif c.attrib.get("t") == "inlineStr":
                    cells[c.attrib["r"]] = "".join(c.find("m:is", NS).itertext())
            result[sheet.attrib["name"]] = cells
        return result

def read_sources():
    wb = read_workbook(BASE / "raw/eia_co2_sector_2024.xlsx")
    contents = wb["Contents"]
    assert contents["A4"] == "Release date: June 26, 2026"
    geo = set(STATES) | {"DC", "US"}
    sources, meta = {}, {"release_label": contents["A4"], "next_update_label": contents["A5"], "series": []}
    for sheet, series, field in [("Electric power", "TEEIE", "electricity_co2_mmt"), ("Industrial", "TEICE", "industry_co2_mmt")]:
        content_rows = [re.sub("[A-Z]", "", k) for k,v in contents.items() if re.fullmatch("A[0-9]+",k) and v==sheet]
        assert len(content_rows)==1
        rr = content_rows[0]
        assert contents["C"+rr]=="Million metric tons CO2" and contents["D"+rr]==series and contents["E"+rr]=="2024F"
        cells = wb[sheet]
        years = {int(v): re.sub("[0-9]", "", k) for k,v in cells.items() if re.fullmatch("[A-Z]+3",k) and k!="A3"}
        assert set(years)==set(range(1960,2025))
        georows = {v:int(k[1:]) for k,v in cells.items() if re.fullmatch("A[0-9]+",k) and v in geo}
        assert set(georows)==geo and len(georows)==52
        source = {}
        for abbr,row in georows.items():
            for year,col in years.items():
                value = float(cells[col+str(row)])
                assert math.isfinite(value) and value>=0
                source[(abbr,year)] = value
        sources[field] = source
        meta["series"].append({"field":field,"sheet":sheet,"msn":series,"source_unit":contents["C"+rr],"status":"2024F","first_year":1960,"last_year":2024,"geographic_units":52,"numeric_cells":len(source)})
    with (BASE / "raw/eia_energy_indicators_2024.csv").open(newline="",encoding="utf-8-sig") as f:
        populations = [r for r in csv.DictReader(f) if r["MSN"]=="TPOPP"]
    assert len(populations)==52 and {r["State"] for r in populations}==geo
    assert {r["Data_Status"] for r in populations}=={"2024F"}
    pop = {}
    for row in populations:
        for year in range(1960,2025):
            value = float(row[str(year)])
            assert math.isfinite(value) and value>0
            assert (row["State"],year) not in pop
            pop[(row["State"],year)] = value
    sources["population_thousands"] = pop
    meta["series"].append({"field":"population_thousands","msn":"TPOPP","source_unit":"thousand resident persons, including Armed Forces","reference_date":"July 1","status":"2024F","first_year":1960,"last_year":2024,"geographic_units":52,"numeric_cells":len(pop)})
    meta["status_meaning"] = "2024F: final historical estimates for the 2024 data cycle, not a forecast"
    meta["conversion"] = "metric tonnes per resident = million metric tonnes * 1000 / thousand residents"
    meta["source_precision"] = "Preserve all supplied values. Population thousand-person estimates and CO2 estimates retain source rounding; calculated per-capita digits do not imply additional measurement precision."
    return sources,meta

def build(output):
    for folder in ["data","audit","receipts"]:
        (output/folder).mkdir(parents=True,exist_ok=True)
    raw_manifest = json.loads((BASE/"receipts/raw_manifest.json").read_text())
    raw_checks = []
    for item in raw_manifest["files"]:
        path=BASE/item["path"]
        assert path.stat().st_size==item["bytes"] and sha256(path)==item["sha256"], f"Raw file changed: {path}"
        raw_checks.append({"path":item["path"],"sha256":sha256(path),"matches_manifest":True})
    write_json(output/"audit/raw_hash_verification.json",raw_checks)
    sources,meta=read_sources()
    write_json(output/"receipts/source_metadata.json",meta)
    rows=[]
    for abbr,name in sorted(STATES.items()):
        for year in range(2000,2025):
            p=sources["population_thousands"][(abbr,year)]
            e=sources["electricity_co2_mmt"][(abbr,year)]
            i=sources["industry_co2_mmt"][(abbr,year)]
            rows.append(dict(zip(PANEL_FIELDS,[abbr,name,year,p,e,i,e*1000/p,i*1000/p])))
    write_csv(output/"data/us_state_sector_co2_2000_2024.csv",rows,PANEL_FIELDS)
    checks=[]
    def check(name,actual,expected):
        passed=actual==expected
        checks.append({"check":name,"actual":actual,"expected":expected,"passed":passed})
        assert passed,f"{name}: actual={actual}, expected={expected}"
    check("rows",len(rows),1250)
    check("unique_state_year_keys",len({(r["stateabbr"],r["year"]) for r in rows}),1250)
    check("unique_states",len({r["stateabbr"] for r in rows}),50)
    check("unique_years",len({r["year"] for r in rows}),25)
    check("DC_US_aggregate_rows",sum(r["stateabbr"] in {"DC","US"} for r in rows),0)
    expected={(s,y) for s in STATES for y in range(2000,2025)}
    actual={(r["stateabbr"],r["year"]) for r in rows}
    missing=sorted(expected-actual)
    check("missing_state_year_keys",len(missing),0)
    write_csv(output/"audit/missing_state_years.csv",({"stateabbr":s,"year":y} for s,y in missing),["stateabbr","year"])
    for field in PANEL_FIELDS[3:]:
        check("missing_or_nonfinite_"+field,sum(not math.isfinite(r[field]) for r in rows),0)
        check("negative_"+field,sum(r[field]<0 for r in rows),0)
    check("zero_population",sum(r["population_thousands"]==0 for r in rows),0)
    for sector in ["electricity","industry"]:
        err=max(abs(r[sector+"_co2_tpc"]-r[sector+"_co2_mmt"]*1e6/(r["population_thousands"]*1000)) for r in rows)
        check("percapita_identity_"+sector,err<1e-12,True)
    write_csv(output/"audit/validation_checks.csv",checks)
    zeros=[{"stateabbr":r["stateabbr"],"state":r["state"],"year":r["year"],"outcome":s+"_co2_mmt","source_value":r[s+"_co2_mmt"],"treatment":"retained as observed zero; no log or offset"} for r in rows for s in ["electricity","industry"] if r[s+"_co2_mmt"]==0]
    write_csv(output/"audit/zero_outcomes.csv",zeros,["stateabbr","state","year","outcome","source_value","treatment"])
    write_csv(output/"audit/coverage_by_state.csv",[{"stateabbr":a,"state":n,"first_year":min(r["year"] for r in rows if r["stateabbr"]==a),"last_year":max(r["year"] for r in rows if r["stateabbr"]==a),"rows":sum(r["stateabbr"]==a for r in rows),"missing_outcome_cells":0,"missing_population_cells":0,"electricity_zero_count":sum(r["stateabbr"]==a and r["electricity_co2_mmt"]==0 for r in rows),"industry_zero_count":sum(r["stateabbr"]==a and r["industry_co2_mmt"]==0 for r in rows)} for a,n in sorted(STATES.items())])
    write_csv(output/"audit/coverage_by_year.csv",[{"year":y,"states":sum(r["year"]==y for r in rows),"missing_outcome_cells":0,"missing_population_cells":0} for y in range(2000,2025)])
    summary=[]
    for field in PANEL_FIELDS[3:]:
        v=[r[field] for r in rows]
        summary.append({"field":field,"n":len(v),"minimum":min(v),"median":statistics.median(v),"maximum":max(v),"zeros":sum(x==0 for x in v),"missing":0})
    write_csv(output/"audit/variable_profile.csv",summary)
    controls=[]
    for field,vals in sources.items():
        for y in range(2000,2025):
            total=sum(vals[(s,y)] for s in STATES)
            dc=vals[("DC",y)]; us=vals[("US",y)]
            note = "US industrial CO2 includes coal coke net imports not allocated to states; do not force state sums to national totals"
            if field != "industry_co2_mmt":
                note = "independently rounded source components and national totals; no forced reconciliation"
            controls.append({"year":y,"field":field,"fifty_states_sum":total,"dc":dc,"US_source":us,"fifty_plus_DC_minus_US":total+dc-us,"interpretation":note})
    write_csv(output/"audit/source_control_totals.csv",controls)
    changes=[]
    lookup={(r["stateabbr"],r["year"]):r for r in rows}
    for s in STATES:
        for y in range(2001,2025):
            for field in ["electricity_co2_mmt","industry_co2_mmt","population_thousands"]:
                prev=lookup[(s,y-1)][field];cur=lookup[(s,y)][field]
                changes.append({"stateabbr":s,"state":STATES[s],"year":y,"field":field,"previous":prev,"current":cur,"absolute_change":cur-prev,"percent_change":100*(cur-prev)/prev if prev else "","previous_is_zero":prev==0})
    ranked=sorted([x for x in changes if x["percent_change"]!=""],key=lambda x:abs(x["percent_change"]),reverse=True)
    write_csv(output/"audit/largest_relative_annual_changes.csv",ranked[:30])
    write_json(output/"audit/quality_summary.json",{
        "panel":"us_state_sector_co2_2000_2024.csv","grain":"state-year","states":50,"years":[2000,2024],"rows":1250,
        "duplicate_keys":0,"missing_keys":0,"missing_outcome_cells":0,"missing_population_cells":0,
        "zero_outcome_cells":len(zeros),"zero_observations":zeros,"validation_checks_passed":len(checks),
        "source_vintage":"EIA SEDS 2024F released 2026-06-26; complete historical vintage","no_interpolation":True,
        "no_forecasts":True,"no_regressions":True,"no_treatment_assignment":True,"no_logs":True,
        "main_panel_covariates":[],
        "measurement_limits":["Energy-related fossil CO2, not all GHG or all industrial process emissions", "Electricity emissions attributed to generation location, not electricity consumers", "Industrial sector includes manufacturing, agriculture, mining and construction", "US industrial total includes coal coke net imports not allocated to states, so state sums need not equal it", "Zero policy: source zeros would be retained; none occur in the selected 50-state 2000-2024 panel", "Full-vintage revised estimates are not real-time policy-era measurements", "Per-capita outcomes can respond through population as well as emissions", "No causal effect is estimated by this input package"]})
    generated = ["data/us_state_sector_co2_2000_2024.csv",
                 "audit/raw_hash_verification.json", "audit/missing_state_years.csv", "audit/validation_checks.csv",
                 "audit/zero_outcomes.csv", "audit/coverage_by_state.csv", "audit/coverage_by_year.csv",
                 "audit/variable_profile.csv", "audit/source_control_totals.csv", "audit/largest_relative_annual_changes.csv",
                 "audit/quality_summary.json", "receipts/source_metadata.json"]
    outputs=[]
    for rel in sorted(generated):
        p=output/rel
        outputs.append({"path":rel,"bytes":p.stat().st_size,"sha256":sha256(p)})
    write_json(output/"receipts/output_hashes.json",outputs)
    print(json.dumps({"status":"PASS","rows":len(rows),"states":50,"period":"2000-2024","zero_outcome_cells":len(zeros),"checks_passed":len(checks),"panel":str(output/"data/us_state_sector_co2_2000_2024.csv")}))

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=BASE,help="Output destination; sources always read from package raw/.")
    args=parser.parse_args()
    build(args.output.resolve())
