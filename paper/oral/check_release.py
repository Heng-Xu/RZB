"""Read-only checks for the oral deck, its source records and Git scope.

This is independent of the research-report acceptance workflow. It never
changes report files or marks their existing acceptance issues as resolved.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

import pymupdf

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / 'EPG_NSGA_II_MIND2026_Oral_20261020'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged-scope', action='store_true')
    args = parser.parse_args()
    if args.staged_scope:
        paths = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z']).decode().split('\0')
        paths = [p for p in paths if p]
        assert paths, 'Nothing staged'
        unexpected = [p for p in paths if not (p.startswith('paper/oral/') or p in {'prompt.md', 'memory/current.md'})]
        assert not unexpected, f'Unrelated staged paths: {unexpected}'
        print(f'Staged scope verified: {len(paths)} oral-presentation/record files.')

    audit = json.loads((PROJECT / 'validation/delivery_audit.json').read_text())
    visual = json.loads((PROJECT / 'validation/final_visual_review.json').read_text())
    quality = json.loads((PROJECT / 'validation/svg_quality_report.json').read_text())
    assert audit['status'] == visual['status'] == 'passed'
    assert quality['stage'] == 'final' and quality['summary']['errors'] == 0
    assert quality['summary']['warnings'] == 0 and quality['summary']['total'] == 5
    for item in quality['source_fingerprint']['files']:
        assert sha(PROJECT / 'svg_output' / item['file']) == item['sha256'], f"Stale SVG check: {item['file']}"
    assert audit['speaker_notes_match_script'] and audit['total_spoken_words'] == 640
    for name, record in audit['files'].items():
        assert sha(ROOT / name) == record['sha256'], f'Delivery hash mismatch: {name}'
    for name, digest in visual['files'].items():
        assert sha(ROOT / name) == digest, f'Visual review stale: {name}'
    for item in json.loads((PROJECT / 'sources/historical_model_manifest.json').read_text()):
        assert sha(PROJECT / item['local']) == item['sha256'], item['local']
    for item in json.loads((PROJECT / 'validation/cleanup_manifest.json').read_text())['entries']:
        assert sha(ROOT / item['archive']) == item['sha256'], item['archive']

    sections = re.findall(r'^# (\d\d_[^\n]+)\n(.*?)(?=^# |\Z)',
                          (PROJECT / 'notes/total.md').read_text(), re.M | re.S)
    expected = [body.strip().removesuffix('---').strip() for _, body in sections]
    assert len(expected) == 5
    normalize = lambda s: ' '.join(s.split())
    pptx = ROOT / 'EPG-NSGA-II_MIND2026_Oral_Corrected.pptx'
    with zipfile.ZipFile(pptx) as z:
        slides = [name for name in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', name)]
        assert len(slides) == 5
        maths = pictures = 0
        for i in range(1, 6):
            slide = ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
            maths += len(slide.findall('.//m:oMath', NS))
            pictures += len(slide.findall('.//p:pic', NS))
            note = ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
            bodies = []
            for shape in note.findall('.//p:sp', NS):
                ph = shape.find('.//p:ph', NS)
                if ph is not None and ph.get('type') == 'body':
                    bodies.append(' '.join(t.text or '' for t in shape.findall('.//a:t', NS)))
            assert normalize(' '.join(bodies)) == normalize(expected[i-1]), f'Note {i}'
        assert maths == 2 and pictures == 0
    with pymupdf.open(ROOT / 'EPG-NSGA-II_MIND2026_Oral_Corrected.pdf') as pdf:
        assert len(pdf) == 5
        for page in pdf:
            assert abs(page.rect.width / page.rect.height - 16/9) < 1e-5
            assert not page.get_images() and '\ufffd' not in page.get_text()
            for font in page.get_fonts(full=True):
                assert font[0] > 0 and pdf.extract_font(font[0])[3], font[3]
    assert len(list((PROJECT / '.review').glob('0*.json'))) == 5
    for path in (PROJECT / '.review').glob('0*.json'):
        page_review = json.loads(path.read_text())
        assert page_review['status'] in {'ok', 'fixed'}
        assert not page_review['needs_human_items']
    print('Oral release passed: 5 slides, 2 native formulas, embedded PDF fonts, '
          'matching notes, source/cleanup hashes and final visual evidence.')


if __name__ == '__main__':
    main()
