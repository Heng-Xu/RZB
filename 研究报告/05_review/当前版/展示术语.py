"""将原计算字段映射为交付术语，不修改求解参数或计算结果。"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DISPLAY_NAMES = json.loads((HERE / '1007研究报告修订/工作簿显示术语映射.json').read_text())
LOAD_DIVERSITY = {'偏集中': 1.15, '较均匀': 1.00}
STRUCTURED_SHEET = '按供电类别与负荷分散系数查表'
LOAD_DIVERSITY_NOTE = (
    '负荷分散系数为同一统计期、同一电压等级及统计范围内，各站最大负荷之和与对应站群同时最大负荷的比值。'
    '本研究取1.00和1.15，两组情景沿用各自的站间负荷权重，推荐范围按相应组合归纳。'
)


def display_value(key, value):
    return LOAD_DIVERSITY[value] if key == '负荷分布' else value


def apply_workbook_terms(workbook):
    for sheet in workbook:
        headers = [cell.value for cell in sheet[1]]
        for column, key in enumerate(headers, 1):
            if key == '负荷分布':
                for cells in sheet.iter_rows(min_row=2, min_col=column, max_col=column):
                    cell = cells[0]
                    cell.value = display_value(key, cell.value)
                    cell.number_format = '0.00'
            sheet.cell(1, column).value = DISPLAY_NAMES.get(key, key)
    if '按供电类别与分布查表' in workbook.sheetnames:
        workbook['按供电类别与分布查表'].title = STRUCTURED_SHEET
    instructions = workbook['使用说明']
    for row in instructions:
        for cell in row:
            if isinstance(cell.value, str):
                cell.value = cell.value.replace('按供电类别与分布查表', STRUCTURED_SHEET)
    if not any(row[0].value == '负荷分散系数' for row in instructions):
        instructions.append(['负荷分散系数', LOAD_DIVERSITY_NOTE])
