"""带已有资产候选起点的求解；保存最优界和可行解，明确区别寻优精度。"""
import csv
import math
import time
import highspy
import numpy as np
from scipy.sparse import coo_matrix
from ..pilot_20261009.run import dump


def solve(m,out,stage,seconds,gap,inp,meta,warmroot):
    rr,cc,vv=zip(*m.entries);a=coo_matrix((vv,(rr,cc)),shape=(len(m.constraint_lower),len(m.costs))).tocsr()
    lp=highspy.HighsLp();lp.num_col_,lp.num_row_=a.shape[1],a.shape[0]
    lp.col_cost_,lp.col_lower_,lp.col_upper_=m.costs,m.lower_bounds,m.upper_bounds
    lp.row_lower_,lp.row_upper_=m.constraint_lower,m.constraint_upper
    lp.integrality_=[highspy.HighsVarType.kInteger if v else highspy.HighsVarType.kContinuous for v in m.integrality]
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise;lp.a_matrix_.start_,lp.a_matrix_.index_,lp.a_matrix_.value_=a.indptr,a.indices,a.data
    h=highspy.Highs()
    for k,v in [('threads',1),('random_seed',0),('mip_rel_gap',gap),('time_limit',seconds),('log_to_console',False),('log_file',str(out/(stage+'.log')))]:h.setOptionValue(k,v)
    h.passModel(lp)
    if (warmroot/'stations.csv').exists():
        rows={(r['station'],int(r['year'])):r for r in csv.DictReader((warmroot/'stations.csv').open(encoding='utf-8-sig'))}
        projects=list(csv.DictReader((warmroot/'projects.csv').open(encoding='utf-8-sig')))
        values={}
        for (sid,slot,y,r),v in meta['x'].items():values[v]=float(abs(float(rows[sid,y][f'unit_{slot+1}_mva'])-r)<1e-6)
        for (sid,y),v in meta['third'].items():values[v]=float(rows[sid,y]['unit_3_mva'])/50
        for (sid,y),v in meta['modules'].items():
            values[v]=min(m.upper_bounds[v],math.ceil(int(rows[sid,y]['storage_modules'])/inp.get('storage_usable_energy_fraction',1.)))
        for (eid,y),v in meta['edgevars'].items():values[v]=float(any(r['id']==eid and int(r['year'])<=y for r in projects))
        h.setSolution(len(values),np.array(list(values),dtype=np.int32),np.array(list(values.values()),dtype=float))
    print('SOLVE',stage,len(m.costs),'variables','warm',len(values) if 'values' in locals() else 0,flush=True)
    started=time.monotonic();h.run();info=h.getInfo();raw=h.getSolution();status=h.getModelStatus()
    result={'stage':stage,'status':h.modelStatusToString(status),'solver':h.version(),'elapsed_seconds':time.monotonic()-started,
            'variables':len(m.costs),'constraints':len(m.constraint_lower),'relative_gap_target':gap,
            'objective':float(info.objective_function_value) if raw.value_valid else None,
            'dual_bound':float(info.mip_dual_bound) if math.isfinite(info.mip_dual_bound) else None,
            'mip_gap':float(info.mip_gap) if math.isfinite(info.mip_gap) else None,
            'accepted':status==highspy.HighsModelStatus.kOptimal,'proven_infeasible':status==highspy.HighsModelStatus.kInfeasible}
    z=np.asarray(raw.col_value) if raw.value_valid else None
    if z is not None:
        az=a@z;integers=np.array(m.integrality,dtype=bool)
        checks={'lower_violation':float(max(0,np.max(np.asarray(m.constraint_lower)-az))),
                'upper_violation':float(max(0,np.max(az-np.asarray(m.constraint_upper)))),
                'bound_violation':float(max(0,np.max(np.asarray(m.lower_bounds)-z),np.max(z-np.asarray(m.upper_bounds)))),
                'integer_violation':float(np.max(abs(z[integers]-np.round(z[integers]))))}
        result['matrix_check']=checks;result['feasible_incumbent']=max(checks.values())<1e-5
        np.savez_compressed(out/(stage+'_solution.npz'),solution=z)
    dump(out/(stage+'_solver.json'),result)
    print('RESULT',result['status'],result['objective'],result['mip_gap'],flush=True)
    return z,result
