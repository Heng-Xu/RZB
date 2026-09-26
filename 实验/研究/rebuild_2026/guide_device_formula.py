"""DL/T 2041—2025 第 6.3、8.5 节的设备级承载与可开放容量原式。"""


def device_hosting_interval_mw(
    load_mw: float,
    other_generation_mw: float,
    existing_storage_charge_mw: float,
    transformer_rating_mva: float,
    power_factor: float,
    max_reverse_loading_rate: float,
    dg_max_output_factor: float,
    planned_new_storage_min_mw: float = 0.0,
    planned_new_storage_max_mw: float = 0.0,
) -> tuple[float, float]:
    """第 6.3 节：新储能规模区间在除以 τ_max 后相加，不能重复放进 P_ESS。"""
    if not 0 < dg_max_output_factor <= 1:
        raise ValueError("τ_max 应在 (0, 1] 内")
    if not 0 < power_factor <= 1 or not 0 <= max_reverse_loading_rate <= 1:
        raise ValueError("功率因数或最大反向负载率越界")
    if transformer_rating_mva < 0 or existing_storage_charge_mw < 0:
        raise ValueError("设备容量和既有储能充电功率不得为负")
    if planned_new_storage_min_mw < 0 or planned_new_storage_max_mw < planned_new_storage_min_mw:
        raise ValueError("新增储能装机规模区间无效")
    base = (
        load_mw - other_generation_mw + existing_storage_charge_mw
        + transformer_rating_mva * power_factor * max_reverse_loading_rate
    ) / dg_max_output_factor
    return base + planned_new_storage_min_mw, base + planned_new_storage_max_mw


def device_open_capacity_intervals_mw(
    hosting_min_mw: float,
    hosting_max_mw: float,
    connected_dg_mw: float,
    registered_unconnected_dg_mw: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """第 8.5 节：可开放并网区间、扣除已备案未并网后的可开放备案区间。"""
    if hosting_max_mw < hosting_min_mw or connected_dg_mw < 0 or registered_unconnected_dg_mw < 0:
        raise ValueError("承载区间或已并网/已备案容量无效")
    grid_connection = hosting_min_mw - connected_dg_mw, hosting_max_mw - connected_dg_mw
    registration = (
        grid_connection[0] - registered_unconnected_dg_mw,
        grid_connection[1] - registered_unconnected_dg_mw,
    )
    return grid_connection, registration
