"""独立复核最终研究报告的来源、模型数值、图件和可编辑公式。"""

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from zipfile import ZipFile

from docx import Document

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MD = ROOT / '研究报告/03_MD'
OUT = ROOT / '实验/研究/rebuild_2026/outputs'
WORD = ROOT / '研究报告/04_word/研究报告终稿.docx'
PDF = ROOT / '研究报告/04_word/研究报告终稿.pdf'


def csvrows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    checks = {}
    model = json.loads((OUT/'ordered_guide_result_audit.json').read_text())
    assert model['status'] == 'PASS'
    checks['model_audit'] = model['status']
    chapter = (MD/'05 第五章 优化结果分析.md').read_text()
    station_records = 0
    for name, folder in [('邳州','ordered_guide_pizhou_n1'),('市区','ordered_guide_city_n1')]:
        for label, scheme in [('刚性','rigid'),('弹性','elastic')]:
            years = csvrows(OUT/folder/f'{scheme}_years.csv')
            station_records += len(csvrows(OUT/folder/f'{scheme}_stations.csv'))
            for r in years:
                y = int(r['year'])
                row = re.search(rf'^\| {name}{label} \| {y} \|.*$', chapter, re.M)
                assert row, (name,label,y)
                cells = [x.strip() for x in row.group().strip('|').split('|')]
                assert abs(float(cells[2])-float(r['net_peak_proxy_mw'])) < .001
                assert abs(float(cells[3])-float(r['capacity_mva'])) < .001
                assert abs(float(cells[4])-float(r['clr'])) < .0001
                assert abs(float(cells[5])-float(r['new_transformer_purchase_mva'])) < .001
                assert int(cells[7]) == int(r['new_lines_commissioned'])
            summary = {x['scheme']: x for x in json.loads((OUT/folder/'summary.json').read_text())}
            assert f'{summary[scheme]["objective_npv_10k"]:.2f}' in chapter
    assert station_records == 392
    checks['annual_rows_checked'] = 16
    checks['station_year_records'] = station_records
    matrix = csvrows(OUT/'generic_parameter_matrix_v2/conditional_recommendation_matrix.csv')
    assert len(matrix)==18 and all(x['status']=='solved' for x in matrix)
    assert sum(x['economically_preferred']=='elastic' for x in matrix)==1
    checks['matrix_solved'] = len(matrix)
    manifest = csvrows(ROOT/'研究报告/数据来源/2026-09-28_10kV线路与成本依据/source_manifest.csv')
    for r in manifest:
        p = ROOT/'研究报告/数据来源/2026-09-28_10kV线路与成本依据'/r['archive_path']
        assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
    checks['source_hashes_checked'] = len(manifest)
    figures = re.findall(r'!\[[^]]*\]\(([^)]+)\)', chapter)
    assert len(figures)==6 and all((MD/x).exists() for x in figures)
    checks['figures_checked'] = len(figures)
    doc = Document(WORD)
    assert len(doc.inline_shapes)==6
    assert not any('\\tag{' in p.text or p.text.startswith('$$') for p in doc.paragraphs)
    with ZipFile(WORD) as z:
        xml = z.read('word/document.xml').decode()
    checks['native_display_formulas'] = xml.count('<m:oMathPara>')
    assert checks['native_display_formulas']>=11
    pages = int(re.search(r'^Pages:\s*(\d+)', subprocess.check_output(
        ['pdfinfo',str(PDF)],text=True),re.M).group(1))
    assert 140 <= pages <= 160
    checks['pdf_pages'] = pages
    checks['word_sha256'] = hashlib.sha256(WORD.read_bytes()).hexdigest()
    checks['pdf_sha256'] = hashlib.sha256(PDF.read_bytes()).hexdigest()
    checks['status'] = 'PASS'
    (HERE/'终稿独立核验.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    assembly = HERE/'装配核验.json'
    if assembly.exists():
        details = json.loads(assembly.read_text(encoding='utf-8'))
        details.pop('pdf_pages_before_reprint', None)
        details['pdf_status'] = 'final_verified'
        details['pdf_pages'] = pages
        details['word_sha256'] = checks['word_sha256']
        details['pdf_sha256'] = checks['pdf_sha256']
        assembly.write_text(json.dumps(details,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(checks,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
