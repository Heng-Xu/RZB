"""显式调整指定作者的修订显示时间；默认预览，保留真实操作记录和原件。"""
from pathlib import Path
from zipfile import ZipFile
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from collections import Counter
import argparse, hashlib, json, random, re, shutil
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
TAGS = {'ins', 'del', 'tblGridChange', 'tblPrChange', 'trPrChange', 'pPrChange', 'rPrChange', 'tcPrChange', 'sectPrChange'}
qn = lambda key: '{' + W + '}' + key
START_TAG = re.compile(rb'<w:(?:' + b'|'.join(x.encode() for x in sorted(TAGS)) + rb')\b[^>]*>')
DATE_ATTR = re.compile(rb'\bw:date="[^"]*"')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def target_tag(tag, author):
    return re.search(rb'\bw:author="' + re.escape(author.encode()) + rb'"', tag) is not None

def masked(xml, author):
    return START_TAG.sub(lambda m: DATE_ATTR.sub(b'w:date="DISPLAY_TIME"', m[0]) if target_tag(m[0], author) else m[0], xml)

def plan(xml, author, first, last, hour_start, hour_end, zone, seed):
    assert first <= last and 0 <= hour_start < hour_end <= 23
    root = E.fromstring(xml)
    groups = []
    for block_no, block in enumerate(root.find(qn('body'))):
        revisions = [x for x in block.iter() if x.tag in {qn(t) for t in TAGS} and x.get(qn('author')) == author]
        if revisions:
            groups.append((block_no, revisions))
    assert groups, '没有该作者的修订'
    days = (last - first).days + 1
    seconds = (hour_end - hour_start) * 3600 + 1
    # 按文档顺序分配随机时点；同一段落或表格中的配对增删共享时间。
    slots = sorted(random.Random(seed).sample(range(days * seconds), len(groups)))
    rows = []
    for (block_no, revisions), slot in zip(groups, slots):
        day_no, offset = divmod(slot, seconds)
        local = datetime.combine(first + timedelta(days=day_no), time(hour_start), ZoneInfo(zone)) + timedelta(seconds=offset)
        for item in revisions:
            assert item.get(qn('date')) is not None and item.get(qn('id')) is not None
            assert not any(E.QName(k).localname == 'dateUtc' for k in item.attrib), '遇到扩展UTC字段，须另行核对后处理'
            rows.append({'修订ID': item.get(qn('id')), '类型': E.QName(item).localname, '正文块': block_no,
                         '原时间': item.get(qn('date')), '显示时间': local.isoformat(timespec='seconds')})
    assert len({x['修订ID'] for x in rows}) == len(rows)
    by_id = {x['修订ID'].encode(): x for x in rows}
    count = 0
    def replace(match):
        nonlocal count
        tag = match[0]
        if not target_tag(tag, author):
            return tag
        ident = re.search(rb'\bw:id="([^"]+)"', tag)[1]
        row = by_id[ident]
        assert DATE_ATTR.search(tag)[0] == b'w:date="' + row['原时间'].encode() + b'"'
        count += 1
        return DATE_ATTR.sub(b'w:date="' + row['显示时间'].encode() + b'"', tag)
    changed = START_TAG.sub(replace, xml)
    assert count == len(rows) and masked(xml, author) == masked(changed, author)
    E.fromstring(changed)
    return changed, rows, len(groups)

def verify(target, record_path):
    record = json.loads(record_path.read_text())
    backup = ROOT / record['备份']
    assert sha(backup) == record['修前SHA256'] and sha(target) == record['修后SHA256']
    with ZipFile(backup) as old, ZipFile(target) as new:
        assert old.namelist() == new.namelist()
        for part in old.namelist():
            before, after = old.read(part), new.read(part)
            if part == 'word/document.xml':
                assert masked(before, record['作者']) == masked(after, record['作者']), '时间之外的正文或属性发生变化'
                rebuilt, rows, groups = plan(before, record['作者'], date.fromisoformat(record['开始日期']),
                    date.fromisoformat(record['结束日期']), *record['每日小时范围'], record['时区'], record['随机种子'])
                assert after == rebuilt and rows == record['逐项映射'] and groups == record['分组数']
            else:
                assert before == after, '无关包部件发生变化: ' + part
    return {'状态': '通过', '修订数': len(record['逐项映射']), '仅修改': '指定作者的w:date', '其余包部件': '逐字节一致'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--start-date', type=date.fromisoformat, required=True)
    parser.add_argument('--end-date', type=date.fromisoformat, required=True)
    parser.add_argument('--hours', type=int, nargs=2, default=(8, 20))
    parser.add_argument('--seed', type=int, required=True)
    args = parser.parse_args()
    target = ROOT / '研究报告/甲方反馈/10.11/供电公司讨论稿.docx'
    audit = ROOT / '研究报告/05_review/当前版/1014修订时间显示调整'
    with ZipFile(target) as z:
        infos = z.infolist(); parts = {i.filename: z.read(i) for i in infos}
    changed, rows, groups = plan(parts['word/document.xml'], 'xh', args.start_date, args.end_date, *args.hours, 'Asia/Shanghai', args.seed)
    summary = {'修订数': len(rows), '分组数': groups, '按日期计数': dict(Counter(x['显示时间'][:10] for x in rows)),
               '最早时间': rows[0]['显示时间'], '最晚时间': rows[-1]['显示时间']}
    if args.apply:
        assert not audit.exists(), '已有本轮记录，禁止覆盖原件及真实时间映射'
        audit.mkdir(parents=True)
        backup = audit / '修前讨论稿.docx'; shutil.copy2(target, backup)
        record = {'状态': '元数据核验通过，待原生及WPS检查', '实际操作时间UTC': datetime.now(timezone.utc).isoformat(),
                  '性质': '用户指定的修订显示元数据调整，随机时间不表示实际编辑过程', '作者': 'xh',
                  '备份': str(backup.relative_to(ROOT)), '修前SHA256': sha(target), '开始日期': str(args.start_date),
                  '结束日期': str(args.end_date), '每日小时范围': args.hours, '时区': 'Asia/Shanghai',
                  '编码': 'ISO 8601显式+08:00偏移；不改系统时间、文件创建日期或批注日期',
                  '随机种子': args.seed, '分组数': groups, '逐项映射': rows}
        temporary = target.with_suffix('.docx.tmp')
        try:
            with ZipFile(temporary, 'w') as z:
                for info in infos:
                    z.writestr(info, changed if info.filename == 'word/document.xml' else parts[info.filename])
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        record['修后SHA256'] = sha(target)
        path = audit / '时间显示调整.json'
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
        summary['核验'] = verify(target, path)
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == '__main__':
    main()
