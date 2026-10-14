"""扩大设计的完整序列、互异组合及缓存数值核验。"""
import itertools
import json
import numpy as np
import expand_indicator_backgrounds as wide


def test_original_backgrounds_and_every_price_sequence_are_present():
    jobs=wide.tasks();by_key={wide.first.key(p):p for p in jobs}
    assert len(by_key)==len(jobs)
    assert {wide.first.key(p) for p in wide.SMALL_JOBS}<=set(by_key)
    assert len(wide.backgrounds())==888
    for b in wide.backgrounds():
        for eta,driver,price in itertools.product([1.,2.,3.],['line_price','storage_price'],wide.PRICE_NODES):
            p=dict(b,eta=eta,energy_penetration=round(.2*eta,10),h95_h=4,line_price=1.,storage_price=1.)
            p[driver]=price
            assert wide.first.key(p) in by_key


def test_design_record_roundtrips_without_changing_the_declared_domain():
    declaration=wide.design()
    assert json.loads(json.dumps(declaration))==declaration


def test_energy_and_duration_sequences_cover_all_backgrounds():
    keys={wide.first.key(p) for p in wide.tasks()}
    for b in wide.backgrounds():
        for eta in [1.,2.,3.]:
            for e,h in [(e,4) for e in wide.energy_nodes(eta)]+[(e,h) for e,h in itertools.product([.15*eta,.2*eta],range(1,9))]:
                p=dict(b,eta=eta,energy_penetration=round(e,10),h95_h=h,line_price=1.,storage_price=1.)
                assert wide.first.key(p) in keys


def test_cache_keeps_original_network_values_and_returns_independent_copies():
    base=np.array([25.,37.5,50.,62.5,75.])
    pairs=sorted({tuple(sorted((i,(i+1)%5))) for i in range(5)})
    before=wide.CALIBRATE(base,pairs,.4,.95)
    wide.enable_network_cache()
    after=wide.first.model.locked.calibrate_initial_network(base,pairs,.4,.95)
    assert before[0]==after[0] and before[2:]==after[2:]
    np.testing.assert_array_equal(before[1],after[1])
    after[0][0]['capacity']=-1;after[1][0]=-1;after[3]['station_transfer_mw'][0]=-1
    again=wide.first.model.locked.calibrate_initial_network(base,pairs,.4,.95)
    assert again[0]==before[0] and again[2:]==before[2:]
    np.testing.assert_array_equal(again[1],before[1])


def test_precision_retry_keeps_original_cost_check():
    p=dict(growth_rate=0.,cable_fraction=.3,initial_transfer_fraction=.1,diversity=1.,
        eta=3.,energy_penetration=.6,h95_h=8,line_price=1.,storage_price=1.,node_purpose='费用数值核验')
    r=wide.solve_task(p)
    assert r['verified'] and abs(sum(r['cost_components'].values())-r['cost'])<1e-4
    assert r['physical_check']['violating_pairs']==0
