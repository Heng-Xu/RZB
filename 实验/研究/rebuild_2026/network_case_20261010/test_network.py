import numpy as np
from scipy.optimize import linprog
from .run import circulation_check, NETWORK_TOLERANCE_MW


def test_circulation_matches_independent_lp():
    rng=np.random.default_rng(41)
    for _ in range(200):
        n=6
        arcs=[(i,j,float(rng.uniform(0,4))) for i in range(n) for j in range(n) if i!=j and rng.random()<.3]
        lo=rng.uniform(-3,2,n);hi=lo+rng.uniform(0,5,n)
        a=np.zeros((n,len(arcs)))
        for k,(i,j,c) in enumerate(arcs):a[i,k]+=1;a[j,k]-=1
        lp=linprog(np.zeros(len(arcs)),A_ub=np.vstack([a,-a]),b_ub=np.r_[hi,-lo],bounds=[(0,c) for i,j,c in arcs],method='highs')
        deficit,_=circulation_check(n,arcs,lo,hi)
        assert (deficit<NETWORK_TOLERANCE_MW)==lp.success


def test_disconnected_and_shared_receiving_limit():
    # 两个供出站共同使用同一个受端馈线，只能接收3MW，不能各用3MW。
    arcs=[(0,3,3),(1,3,3),(3,2,3)]
    lo=np.array([2.,2.,-10,0]);hi=np.array([3.,3.,0,0])
    gap,_=circulation_check(4,arcs,lo,hi)
    assert abs(gap-1)<1e-6
    gap,_=circulation_check(2,[],np.array([2.,-4]),np.array([3.,0]))
    assert gap>=2-1e-6


def test_district_capacity_does_not_overflow_flow_integer():
    # 根节点环流量超过1700MW，曾可能在过细整数缩放时溢出。
    lo=np.full(20,-100.);hi=np.full(20,100.);lo[0]=5
    gap,_=circulation_check(20,[(0,1,5.)],lo,hi)
    assert gap<NETWORK_TOLERANCE_MW


def test_soc_requires_real_energy_and_recharging():
    from .soc_check import check_day
    inp={'stations':{'S':{'forward_duration_h':2}},'growth_rate':0.,'network':{'feeders':{},'edges':[]}}
    power=np.ones((24,1));power[11:13]=6.75;units=np.array([[5.,5.,0.]])
    # 20模块名义4.30MWh，在80%窗口和95%效率下不足以支撑两小时2MW。
    short=check_day(inp,power,units,np.array([20]),set(),2025,12,0)
    enough=check_day(inp,power,units,np.array([26]),set(),2025,12,0)
    assert not short['passes_screen'] and enough['passes_screen']
    # 全日超过主变容量，储能不能凭初始SOC持续提供净能量。
    flat=check_day(inp,np.full((24,1),10.),units,np.array([100]),set(),2025,12,-1)
    assert not flat['passes_screen']
