#!/usr/bin/env python3
"""Independent read-only QA; uses pre-existing openpyxl solely to read source XLSX."""
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import openpyxl

BASE=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((BASE/"data/us_state_sector_co2_2000_2024.csv").open()))
assert len(rows)==1250 and len({(r["stateabbr"],r["year"]) for r in rows})==1250
assert {int(r["year"]) for r in rows}==set(range(2000,2025))
assert len({r["stateabbr"] for r in rows})==50
wb=openpyxl.load_workbook(BASE/"raw/eia_co2_sector_2024.xlsx",read_only=True,data_only=True)
qa={"rows":1250,"duplicate_keys":0,"read_only_XLSX_library":"openpyxl "+openpyxl.__version__}
for sheet,column in [("Electric power","electricity_co2_mmt"),("Industrial","industry_co2_mmt")]:
    cells=list(wb[sheet].values)
    years={int(y):i for i,y in enumerate(cells[2]) if i>0 and isinstance(y,(int,float))}
    states={r[0]:r for r in cells[3:] if r and isinstance(r[0],str) and len(r[0])==2}
    for r in rows:
        assert float(r[column])==float(states[r["stateabbr"]][years[int(r["year"])]]),(sheet,r["stateabbr"],r["year"])
    qa[column+"_exact_source_cells"]=len(rows)
wb.close()
pop={r["State"]:r for r in csv.DictReader((BASE/"raw/eia_energy_indicators_2024.csv").open(encoding="utf-8-sig")) if r["MSN"]=="TPOPP"}
for r in rows:
    assert Decimal(r["population_thousands"])==Decimal(pop[r["stateabbr"]][r["year"]])
qa["population_exact_source_cells"]=len(rows)
for sector in ["electricity","industry"]:
    errors=[]
    for r in rows:
        expected=Decimal(r[sector+"_co2_mmt"])*Decimal(1000)/Decimal(r["population_thousands"])
        errors.append(abs(expected-Decimal(r[sector+"_co2_tpc"])))
    assert max(errors)<Decimal("1e-12")
    qa[sector+"_max_percapita_decimal_error"]=str(max(errors))
expected=json.loads((BASE/"receipts/output_hashes.json").read_text())
with tempfile.TemporaryDirectory(prefix="us_carbon_panel_rebuild_") as td:
    subprocess.run([sys.executable,str(BASE/"scripts/build_panel.py"),"--output",td],check=True,capture_output=True,text=True)
    same=[]
    for item in expected:
        p=Path(td)/item["path"]
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual==item["sha256"]==hashlib.sha256((BASE/item["path"]).read_bytes()).hexdigest(),item["path"]
        same.append(item["path"])
    qa["byte_identical_offline_rebuild_files"]=same
    assert (Path(td)/"receipts/output_hashes.json").read_bytes()==(BASE/"receipts/output_hashes.json").read_bytes()
qa["all_checks_passed"]=True
qa["model_fitting_performed"]=False
(BASE/"audit/independent_verification.json").write_text(json.dumps(qa,indent=2)+"\n")
print(json.dumps(qa,indent=2))
