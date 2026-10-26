"""Plot fixed descriptive series and annual contrasts; fit no models.
Run with Python 3. Data provenance and displayed rows are exported.
The only derived series is a ratio of group means to its 2000–2004 group mean.
"""
from pathlib import Path
import hashlib, json, os, tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "us_carbon_mpl"))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/"analysis"/"results"
OUT=Path(__file__).resolve().parent
OUT.mkdir(exist_ok=True)
manifest=json.loads((RESULTS/"analysis_manifest.json").read_text())
inputs=["group_year_summary.csv","annual_contrasts.csv"]
for name in inputs:
    h=hashlib.sha256((RESULTS/name).read_bytes()).hexdigest()
    assert h == manifest["outputs"][name], (name,h)
SUPPORT=ROOT/"diagnostics"/"additive_support_diagnostic.csv"
support=pd.read_csv(SUPPORT).to_dict("records")
assert support[0]["counterfactual_is_negative"] and support[2]["counterfactual_is_negative"]

plt.rcParams.update({
    "font.family":"serif", "font.serif":["Times New Roman","Liberation Serif","DejaVu Serif"],
    "font.size":11, "axes.labelsize":11, "xtick.labelsize":10.5, "ytick.labelsize":10.5,
    "legend.fontsize":10.5, "text.color":"black", "axes.labelcolor":"black",
    "axes.edgecolor":"black", "xtick.color":"black", "ytick.color":"black",
    "axes.linewidth":0.7, "savefig.facecolor":"white", "figure.facecolor":"white",
    "svg.fonttype":"none", "svg.hashsalt":"us-carbon-rggi-fixed-v1", "mathtext.fontset":"stix",
})
COLORS={"treated":"#174A73","comparison":"#AC5428","power":"#174A73","industry":"#AC5428"}
TICKS=[2000,2004,2008,2012,2016,2020,2024]

def phase_context(ax, baseline=True):
    if baseline:
        ax.axvspan(1999.7,2004.5,color="#F0F0F0",zorder=0)
    ax.axvspan(2004.5,2008.5,color="#DADADA",alpha=0.68,zorder=0)
    ax.axvline(2009,color="#333333",lw=1,ls=(0,(4,3)),zorder=2)
    for x,txt in [(2002.1,"Baseline\n2000–2004"),(2006.5,"Anticipation\n2005–2008"),(2016.7,"Compliance from 2009")]:
        ax.text(x,1.025,txt,transform=ax.get_xaxis_transform(),ha="center",va="bottom",fontsize=9.5,color="black")
    ax.set_xlim(1999.7,2024.3); ax.set_xticks(TICKS)
    ax.grid(axis="y",color="#DDDDDD",linewidth=0.55,zorder=0)
    ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(axis="both",length=3.3,width=0.7)


def save(fig,name):
    fig.savefig(OUT/(name+".png"),dpi=450)
    fig.savefig(OUT/(name+".svg"), metadata={"Date": None})
    plt.close(fig)

groups=pd.read_csv(RESULTS/"group_year_summary.csv")
power=groups[(groups.outcome=="power")&groups.group.isin(["treated","comparison"])].copy()
assert len(power)==50
assert set(power[power.group=="treated"].n_states)=={9}
assert set(power[power.group=="comparison"].n_states)=={34}
baseline=power[power.year.between(2000,2004)].groupby("group").mean_state_tpc.mean()
power["group_2000_2004_mean_tpc"]=power.group.map(baseline)
power["index_group_baseline_100"]=100*power.mean_state_tpc/power.group_2000_2004_mean_tpc
power["index_definition"]="100 x annual equal-state group mean / 2000-2004 mean of annual equal-state group means"
power.to_csv(OUT/"figure1_plotdata.csv",index=False,float_format="%.12g",lineterminator="\n")
assert abs(baseline["treated"]-3.59390172616)<1e-9
assert abs(baseline["comparison"]-15.0983348728)<1e-9
fig,axes=plt.subplots(2,1,figsize=(6.6,6.4),sharex=True)
fig.subplots_adjust(left=.145,right=.975,bottom=.075,top=.86,hspace=.53)
for i,(ax,column,label) in enumerate(zip(axes,["mean_state_tpc","index_group_baseline_100"],["(a) Raw levels","(b) Group mean index"])):
    phase_context(ax)
    for group,style,marker in [("treated","-","o"),("comparison",(0,(5,2.5)),"s")]:
        d=power[power.group==group].sort_values("year")
        ax.plot(d.year,d[column],color=COLORS[group],lw=1.7,ls=style,marker=marker,markersize=3.0,
                markerfacecolor="white" if group=="comparison" else COLORS[group],markeredgewidth=.7,zorder=3)
    ax.text(.012,.95,label,transform=ax.transAxes,ha="left",va="top",fontsize=11,fontweight="bold",color="black")
    if i==0:
        ax.set_ylabel("Electricity CO₂\n(t per resident)")
        ax.set_ylim(0,18); ax.set_yticks([0,4,8,12,16])
    else:
        ax.set_ylabel("Index\n(group baseline = 100)")
        ax.set_ylim(0,120); ax.set_yticks([0,25,50,75,100])
        ax.axhline(100,color="#555555",lw=.6,ls=":",zorder=1)
axes[-1].set_xlabel("Year")
axes[0].tick_params(labelbottom=True)
fig.legend(handles=[
    Line2D([0],[0],color=COLORS["treated"],lw=1.7,marker="o",markersize=3.5,label="Fixed RGGI cohort (9 states)"),
    Line2D([0],[0],color=COLORS["comparison"],lw=1.7,ls=(0,(5,2.5)),marker="s",markerfacecolor="white",markersize=3.5,label="Comparison group (34 states)")
],loc="upper center",bbox_to_anchor=(.55,.992),ncol=1,frameon=False,handlelength=3,labelspacing=.35)
save(fig,"figure1_electricity_paths")

annual=pd.read_csv(RESULTS/"annual_contrasts.csv")
assert len(annual)==50 and set(annual.simultaneous_family_size)=={50}
assert set(annual.outcome)=={"power","industry"}
annual.to_csv(OUT/"figure2_plotdata.csv",index=False,float_format="%.12g",lineterminator="\n")
fig,axes=plt.subplots(2,1,figsize=(6.6,6.4),sharex=True)
fig.subplots_adjust(left=.145,right=.975,bottom=.075,top=.86,hspace=.53)
for i,(ax,outcome,label) in enumerate(zip(axes,["power","industry"],["(a) Electricity","(b) Industry"])):
    phase_context(ax)
    d=annual[annual.outcome==outcome].sort_values("year")
    ax.fill_between(d.year,d.sim95_low_wcu,d.sim95_high_wcu,color=COLORS[outcome],alpha=.18,linewidth=0,zorder=2)
    ax.plot(d.year,d.estimate_tpc,color=COLORS[outcome],lw=1.4,marker="o",markersize=3.0,zorder=4)
    ax.axhline(0,color="black",lw=.8,zorder=3)
    ax.set_ylabel("Annual contrast\n(t CO₂ per resident)")
    ax.text(.012,.95,label,transform=ax.transAxes,ha="left",va="top",fontsize=11,fontweight="bold",color="black")
    if outcome=="power":
        ax.set_ylim(-1.5,10.0); ax.set_yticks([0,2,4,6,8,10])
    else:
        ax.set_ylim(-1.7,1.7); ax.set_yticks([-1.5,-1, -.5,0,.5,1,1.5])
axes[-1].set_xlabel("Year")
axes[0].tick_params(labelbottom=True)
fig.legend(handles=[Line2D([0],[0],color="#333333",lw=1.4,marker="o",markersize=3.5,label="Annual level contrast"),
    Patch(facecolor="#B7C4CD",edgecolor="none",label="95% simultaneous band (50 coefficients)")],
    loc="upper center",bbox_to_anchor=(.55,.992),ncol=1,frameon=False,handlelength=3,labelspacing=.35)
save(fig,"figure2_annual_contrasts")

provenance={
    "source_design_id":manifest["design_id"],
    "source_files":{name:manifest["outputs"][name] for name in inputs},
    "support_diagnostic_sha256":hashlib.sha256(SUPPORT.read_bytes()).hexdigest(),
    "figure1_definition":"Frozen equal-state group means. Index is a descriptive ratio of each annual group mean to its group 2000-2004 mean times 100. It is not a mean of state percentage changes or an alternative fitted outcome.",
    "figure1_baselines_tpc":baseline.to_dict(),
    "figure2_definition":"Frozen annual contrasts and existing wild-unrestricted simultaneous 95% bands, one family of 50 coefficients across both sectors. Panel y-axis scales differ.",
    "inference_warning":manifest["inference_warning"],
    "no_new_models_fitted":True,
    "export_width_inches":6.6,
    "font_requested":"Times New Roman; Liberation Serif fallback",
    "files":{},
}
for path in sorted(OUT.glob("*")):
    if path.is_file() and path.suffix in [".png",".svg",".csv"]:
        provenance["files"][path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
(OUT/"figure_provenance.json").write_text(json.dumps(provenance,indent=2))
print(json.dumps(provenance,indent=2))
