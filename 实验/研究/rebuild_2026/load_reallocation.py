"""按区县内正常负荷转接后的供电任务配置主变与储能。"""


def add_post_transfer_n1(model, supplies, original_load, shift_terms,
                         full_service, maximum_post_load, minimum_post_load=0):
    """shift_terms 是转出减转入；主变退出校核不增加事故转供。

    B/C 类服务量为 max(0, min(L'-12, 2L'/3))。其两条线性分支
    在 L'=36 MW 相交，用一个整数变量精确选择，避免先按原负荷
    折算比例后再扣转接量。supplies 中可含第三台未投运的激活项。
    """
    post = {i: -value for i, value in shift_terms.items()}
    model.constraint(post, lower=minimum_post_load - original_load,
                     upper=maximum_post_load - original_load)
    if full_service:
        for available, inactive_allowance in supplies:
            terms = dict(available)
            for i, value in shift_terms.items():
                terms[i] = terms.get(i, 0) + value
            model.constraint(terms, lower=original_load - inactive_allowance)
        return
    branch = model.variable(0)
    if minimum_post_load >= 36:
        model.upper_bounds[branch] = 0
        model.integrality[branch] = 0
    bound = max(36.0, maximum_post_load)
    # branch=1: L'<=36; branch=0: L'>=36.
    model.constraint({**post, branch: bound},
                     upper=36 + bound - original_load)
    model.constraint({**post, branch: bound}, lower=36 - original_load)
    for available, inactive_allowance in supplies:
        small, large = dict(available), dict(available)
        for i, value in shift_terms.items():
            small[i] = small.get(i, 0) + value
            large[i] = large.get(i, 0) + 2 * value / 3
        small[branch] = -bound
        large[branch] = bound
        model.constraint(small, lower=original_load - 12 - bound - inactive_allowance)
        model.constraint(large, lower=2 * original_load / 3 - inactive_allowance)
