"""检验转供标定与容量下限的受控对照，防止参数仅作记录。"""
import copy
import json

import numpy as np

from .run import OUT, build, calibrate, previous,initial_transfer_audit


def toy_input():
    inp=json.loads((OUT/'pizhou/inputs.json').read_text())
    pair=next((e['station_a'],e['station_b']) for e in inp['network']['edges'] if e['id'].startswith('EQ-'))
    inp['stations']={s:copy.deepcopy(inp['stations'][s]) for s in pair}
    for s,r in inp['stations'].items():
        r['initial_units']=[50.,50.];r['base_forward_mw']=20.;r['allow_third']=False
    inp['initial_peak_mw']=40.;inp['initial_capacity_mva']=200.;inp['physical_capacity_upper_mva']=320.
    inp['annual_observed_peak_mw']={str(y):40. for y in range(2021,2026)}
    inp['transfer_calibration_forward_mw']={s:20. for s in pair}
    inp['transfer_calibration_net_mw']={s:20. for s in pair}
    source=next(e for e in inp['network']['edges'] if set((e['station_a'],e['station_b']))==set(pair) and not e['existing'])
    inp['network']['edges']=[copy.deepcopy(source)]
    inp['network']['feeders']={f:copy.deepcopy(inp['network']['feeders'][f]) for f in (source['a'],source['b'])}
    return inp


def test_transfer_input_changes_realized_existing_capacity():
    p=toy_input()
    low=calibrate(p,.3);high=calibrate(p,.9)
    assert abs(low['initial_transfer_audit']['weighted_rate']-.3)<1e-7
    assert abs(high['initial_transfer_audit']['weighted_rate']-.9)<1e-7
    assert high['initial_network_scale']>low['initial_network_scale']
    assert high['stations']==low['stations']
    assert high['network']['edges'][0]==low['network']['edges'][0]


def test_paired_models_differ_only_in_four_capacity_lower_bounds():
    p=calibrate(toy_input(),.67)
    scenes={y:np.array([[20.,20.],[-8.,-8.]]) for y in p['years']}
    a,ma=build(p,scenes,2.);b,mb=build(p,scenes,0.)
    for key in ('costs','lower_bounds','upper_bounds','integrality','entries','constraint_upper'):
        assert getattr(a,key)==getattr(b,key),key
    assert ma==mb
    differences=[(x,y) for x,y in zip(a.constraint_lower,b.constraint_lower,strict=True) if x!=y]
    assert differences==[(80.,0.)]*4


def test_fixed_existing_network_does_not_regenerate_when_capacity_is_compressed():
    reference=calibrate(toy_input(),.9)
    compressed=copy.deepcopy(reference)
    for station in compressed['stations'].values():station['initial_units']=[10.,10.]
    realized=initial_transfer_audit(compressed)
    assert realized['weighted_rate']==0.
    assert compressed['network']==reference['network']
    assert reference['initial_transfer_audit']['weighted_rate']>.89


def test_static_snapshots_cover_individual_extrema_as_synchronous_vectors():
    from .capacity_audit import snapshots,PROFILES
    for region in ('city','pizhou'):
        inp=json.loads((OUT/region/'inputs.json').read_text())
        selected,records=snapshots(region,inp)
        z=np.load(PROFILES/f'{region}_stations.npz')
        raw=z['power_mw'][:,[list(z['station_ids']).index(s) for s in inp['stations']]]
        calibrated=raw*inp['initial_peak_mw']/raw.sum(axis=1).max()
        assert np.allclose(selected.max(axis=0),calibrated.max(axis=0))
        assert np.allclose(selected.min(axis=0),calibrated.min(axis=0))
        assert np.allclose(selected,calibrated[[r['source_hour'] for r in records]])
        assert np.max(selected.sum(axis=1))<=inp['initial_peak_mw']+1e-6


def test_strengthened_elastic_pair_only_changes_the_four_lower_bounds():
    from .capacity_run import build as capacity_build
    p=calibrate(toy_input(),.67)
    scenes={y:np.array([[20.,20.],[-8.,-8.]]) for y in p['years']}
    selected={(y,h,f) for y in p['years'] for h in (0,1) for f in (-1,0,1)}
    a,ma=capacity_build(p,scenes,'elastic_floor_2',selected)
    b,mb=capacity_build(p,scenes,'elastic_no_floor',selected)
    for key in ('costs','lower_bounds','upper_bounds','integrality','entries','constraint_upper'):
        assert getattr(a,key)==getattr(b,key),key
    assert ma==mb
    assert [(x,y) for x,y in zip(a.constraint_lower,b.constraint_lower,strict=True) if x!=y]==[(80.,0.)]*4
