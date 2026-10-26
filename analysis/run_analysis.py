#!/usr/bin/env python3
"""Offline implementation of frozen common-cohort RGGI design. No fitting on import.
Reproduce the fixed scientific specification; importing this module fits no model.
"""
from pathlib import Path
import argparse, hashlib, json, platform, sys
import numpy as np
import pandas as pd
from scipy import stats
import scipy

ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/'design/frozen_design_v1.json'
EXPECTED_DESIGN_SHA='6b8ba766551f89fd0c63f74014a55da456bbd4f83ae520e5ca19c6c12d1bc1b3'
EXPECTED_INPUT_SHA='c247750b4efb04a9e1718c298a792f2bec840635ebfde8f42e2672bba4c62916'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def ols_difference(y, treated):
    """One or multiple outcomes in columns; ordinary [intercept,T] OLS and HC1."""
    y=np.asarray(y,float)
    if y.ndim==1:y=y[:,None]
    n=len(treated);nt=int(treated.sum());nc=n-nt
    mt=y[treated].mean(0);mc=y[~treated].mean(0)
    fitted=np.where(treated[:,None],mt[None,:],mc[None,:])
    e=y-fitted
    var=n/(n-2)*(np.sum(e[treated]**2,axis=0)/nt**2+np.sum(e[~treated]**2,axis=0)/nc**2)
    if np.any(var<=0) or not np.all(np.isfinite(var)):raise ValueError('Nonpositive/nonfinite original HC1 variance')
    return mt-mc,np.sqrt(var),fitted,e

def wild_t(raw_errors, treated, weights):
    """Rademacher wild errors. Exact group-mean OLS/HC1 algebra, all draws.
    Returns centered coefficient t*. In WCR the fitted treatment coefficient is 0;
    in WCU subtracting the original coefficient leaves this same error contrast.
    """
    e=np.asarray(raw_errors,float)
    if e.ndim==1:e=e[:,None]
    n=len(treated);nt=int(treated.sum());nc=n-nt
    mt=weights[:,treated]@e[treated]/nt
    mc=weights[:,~treated]@e[~treated]/nc
    # v_i^2=1, so within-group squared-error total is Q - n_g*mean(v_i e_i)^2.
    qt=np.sum(e[treated]**2,axis=0)[None,:]-nt*mt**2
    qc=np.sum(e[~treated]**2,axis=0)[None,:]-nc*mc**2
    var=n/(n-2)*(qt/nt**2+qc/nc**2)
    if np.any(var<=0) or not np.all(np.isfinite(var)):raise ValueError('Nonpositive/nonfinite bootstrap HC1 variance; no draw replacement permitted')
    return (mt-mc)/np.sqrt(var)

def endpoint(y,treated,weights):
    y=np.asarray(y,float).reshape(-1,1)
    beta,se,_,_=ols_difference(y,treated)
    boot=wild_t(y-y.mean(0),treated,weights)[:,0]
    t=float(beta[0]/se[0]);df=len(treated)-2;q=stats.t.ppf(.975,df)
    return {'estimate_tpc':float(beta[0]),'se_hc1':float(se[0]),'ci95_low_conventional':float(beta[0]-q*se[0]),'ci95_high_conventional':float(beta[0]+q*se[0]),'t_statistic':t,'df_conventional':df,'p_conventional':float(2*stats.t.sf(abs(t),df)),'p_wcr_raw':float((1+np.count_nonzero(np.abs(boot)>=abs(t)))/(len(weights)+1))}

def self_test():
    # Synthetic algebra verification only: no emissions file is opened.
    rg=np.random.default_rng(123);tr=np.array([True]*4+[False]*8);x=np.column_stack([np.ones(12),tr.astype(float)])
    y=rg.normal(size=(12,3));b,se,f,e=ols_difference(y,tr);xx=np.linalg.inv(x.T@x)
    for j in range(3):
        coef=xx@x.T@y[:,j];res=y[:,j]-x@coef
        vv=12/10*xx@(x.T@(res[:,None]**2*x))@xx
        assert np.allclose(b[j],coef[1]) and np.allclose(se[j],np.sqrt(vv[1,1]))
    w=rg.choice([-1.,1.],size=(20,12));bt=wild_t(e,tr,w)
    for k in range(20):
        bb,ss,_,_=ols_difference(f+w[k,:,None]*e,tr)
        assert np.allclose(bt[k],(bb-b)/ss,atol=1e-12)
    print('PASS: synthetic original and wild-bootstrap algebra vs direct matrix OLS/HC1.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--self-test',action='store_true');parser.add_argument('--reproduce',action='store_true');args=parser.parse_args()
    if args.self_test:self_test();return
    if not args.reproduce:parser.error('Use --self-test or --reproduce for the fixed analysis.')
    if sha(DESIGN)!=EXPECTED_DESIGN_SHA:raise ValueError('Frozen design hash changed; stop.')
    cfg=json.loads(DESIGN.read_text());inp=(DESIGN.parent/cfg['data']['path']).resolve()
    if sha(inp)!=EXPECTED_INPUT_SHA:raise ValueError('Audited input hash changed; stop.')
    data=pd.read_csv(inp);years=cfg['data']['years'];states=sorted(cfg['sample']['treated']+cfg['sample']['comparison']);allstates=sorted(states+cfg['sample']['excluded'])
    checks={'input_hash':sha(inp),'design_hash':sha(DESIGN),'exact_1250_rows':len(data)==1250,'unique_state_year':not data.duplicated(['stateabbr','year']).any(),'complete_grid':set(zip(data.stateabbr,data.year))==set((s,y) for s in allstates for y in years)}
    num=cfg['data']['required_columns'][2:];checks['finite_numeric']=bool(np.isfinite(data[num].to_numpy(float)).all());checks['positive_population']=bool((data.population_thousands>0).all());checks['nonnegative_emissions']=bool((data[['electricity_co2_mmt','industry_co2_mmt','electricity_co2_tpc','industry_co2_tpc']]>=0).all().all())
    for sector in ['electricity','industry']:checks[sector+'_conversion']=bool(np.allclose(data[sector+'_co2_tpc'],data[sector+'_co2_mmt']*1000/data.population_thousands,atol=1e-8,rtol=1e-8))
    if not all(v for k,v in checks.items() if k not in ['input_hash','design_hash']):raise ValueError('Input validation failed: '+str(checks))
    tr=np.array([s in cfg['sample']['treated'] for s in states]);n=len(states)
    rg=np.random.Generator(np.random.PCG64(cfg['inference']['seed']));w=rg.choice([-1.0,1.0],size=(cfg['inference']['bootstrap_draws'],n))
    mats={k:data.pivot(index='stateabbr',columns='year',values=v).loc[states,years] for k,v in cfg['data']['outcomes'].items()}
    baseyears=cfg['policy']['baseline_years'];endrows=[];staterows=[]
    def run_ep(ep,bys):
        mat=mats[ep['outcome']];base=mat[bys].mean(axis=1).to_numpy();post=mat[ep['post_years']].mean(axis=1).to_numpy();d=post-base;r=endpoint(d,tr,w)
        r.update({'endpoint':ep['id'],'role':ep.get('role','sensitivity'),'outcome':ep['outcome'],'baseline':f'{min(bys)}–{max(bys)}','post_window':f'{min(ep["post_years"])}–{max(ep["post_years"])}','n_treated':int(tr.sum()),'n_comparison':int((~tr).sum()),'treated_baseline_mean_tpc':float(base[tr].mean()),'treated_post_mean_tpc':float(post[tr].mean()),'comparison_baseline_mean_tpc':float(base[~tr].mean()),'comparison_post_mean_tpc':float(post[~tr].mean()),'percent_of_observed_treated_baseline':float(100*r['estimate_tpc']/base[tr].mean())})
        for s,tt,bb,pp,dd in zip(states,tr,base,post,d):staterows.append({'endpoint':ep['id'],'stateabbr':s,'treated':int(tt),'baseline_mean_tpc':bb,'post_mean_tpc':pp,'change_tpc':dd})
        return r
    for ep in cfg['endpoints']:endrows.append(run_ep(ep,baseyears))
    order=sorted(range(3),key=lambda i:(endrows[i]['p_wcr_raw'],endrows[i]['endpoint']));running=0.
    for j,i in enumerate(order):running=max(running,(3-j)*endrows[i]['p_wcr_raw']);endrows[i]['p_wcr_holm']=min(1.,running)
    sens=[run_ep(ep,ep['baseline_years']) for ep in cfg['sensitivity']]
    columns=[];ys=[]
    for outcome in cfg['annual_diagnostics']['outcomes']:
        mat=mats[outcome];b=mat[baseyears].mean(axis=1).to_numpy()
        for yr in years:columns.append((outcome,yr));ys.append(mat[yr].to_numpy()-b)
    annual=np.column_stack(ys);beta,se,fit,res=ols_difference(annual,tr);tstar=wild_t(res,tr,w);maxstats=np.max(np.abs(tstar),axis=1);crit=float(np.quantile(maxstats,.95,method='higher'));qpoint=float(stats.t.ppf(.975,n-2))
    annrows=[]
    for j,(outcome,yr) in enumerate(columns):annrows.append({'outcome':outcome,'year':yr,'event_time':yr-cfg['policy']['cohort_year'],'period':'baseline' if yr in baseyears else 'anticipation' if yr in cfg['policy']['anticipation_years'] else 'operating','estimate_tpc':float(beta[j]),'se_hc1':float(se[j]),'ci95_low_conventional':float(beta[j]-qpoint*se[j]),'ci95_high_conventional':float(beta[j]+qpoint*se[j]),'sim95_low_wcu':float(beta[j]-crit*se[j]),'sim95_high_wcu':float(beta[j]+crit*se[j]),'simultaneous_critical_value':crit,'simultaneous_family_size':len(columns)})
    pre=[]
    for outcome in cfg['annual_diagnostics']['outcomes']:
        jj=[j for j,c in enumerate(columns) if c[0]==outcome and c[1] in baseyears];yp=annual[:,jj];tt=np.max(np.abs(beta[jj]/se[jj]));bst=wild_t(yp-yp.mean(0),tr,w);bt=np.max(np.abs(bst),axis=1);p=(1+np.count_nonzero(bt>=tt))/(len(w)+1)
        pre.append({'outcome':outcome,'years':'2000–2004','joint_statistic_max_abs_t':float(tt),'p_wcr_joint_diagnostic':float(p),'n_coefficients':len(jj),'caution':'Low-powered diagnostic; nonrejection does not establish parallel trends; no model selection.'})
    summaries=[]
    for outcome,col in cfg['data']['outcomes'].items():
        mm='electricity_co2_mmt' if outcome=='power' else 'industry_co2_mmt'
        for group,ss in [('treated',cfg['sample']['treated']),('comparison',cfg['sample']['comparison']),('excluded',cfg['sample']['excluded'])]:
            for yr,dd in data[data.stateabbr.isin(ss)].groupby('year'):summaries.append({'outcome':outcome,'group':group,'year':int(yr),'n_states':len(dd),'mean_state_tpc':float(dd[col].mean()),'sum_co2_mmt':float(dd[mm].sum()),'sum_population_thousands':float(dd.population_thousands.sum())})
    # Numerical identities for the primary contrast and annual aggregation.
    pmain=endrows[0];jmain=[j for j,c in enumerate(columns) if c[0]=='power' and c[1]>=2009]
    checks['annual_primary_aggregation']=bool(np.isclose(pmain['estimate_tpc'],np.mean(beta[jmain]),atol=1e-12));checks['baseline_annual_sums_zero']=all(abs(sum(beta[j] for j,c in enumerate(columns) if c[0]==o and c[1] in baseyears))<1e-10 for o in ['power','industry'])
    if not checks['annual_primary_aggregation'] or not checks['baseline_annual_sums_zero']:raise AssertionError('Contrast identity failed')
    out=ROOT/'analysis/results';out.mkdir(parents=True,exist_ok=True)
    for name,rows in [('endpoint_results',endrows),('annual_contrasts',annrows),('pretrend_diagnostics',pre),('sensitivity_results',sens),('group_year_summary',summaries),('state_window_changes',staterows)]:pd.DataFrame(rows).to_csv(out/(name+'.csv'),index=False,float_format='%.12g',lineterminator='\n')
    (out/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
    manifest={'design_id':cfg['design_id'],'design_sha256':sha(DESIGN),'input_sha256':sha(inp),'implementation_sha256':sha(__file__),'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'seed':cfg['inference']['seed'],'draws':len(w),'ordered_states':states,'rademacher_matrix_raw_float64_sha256':hashlib.sha256(w.tobytes()).hexdigest(),'simultaneous_band_critical_value':crit,'inference_warning':cfg['inference']['conditioning'],'outputs':{p.name:sha(p) for p in sorted(out.glob('*.csv'))}}
    (out/'analysis_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(pd.DataFrame(endrows)[['endpoint','estimate_tpc','ci95_low_conventional','ci95_high_conventional','p_wcr_raw','p_wcr_holm']].to_string(index=False));print('\nPretrends:',pre);print('\nSensitivity:',sens);print('\nSaved to',out)

if __name__=='__main__':main()
