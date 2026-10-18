"""报告原件修订视图的回归检查：原批注、已有修订及拒绝后恢复。"""
from lxml import etree as E

from revise_report_in_place import Editor, NS, qn, text, view, reuse_unchanged_blocks
import pytest
from verify_annual_report_update import check_capacity_period
from report_matrix_display import adjoining_bands
from check_report_policy import check_adjoining_matrix


def test_adjoining_planning_bands_preserve_capacity_bounds_and_platforms():
    assert adjoining_bands(['1.91～2.09','1.76～2.09','1.50～1.95','1.36～1.95']) == ['1.91～2.09','1.76～1.91','1.50～1.76','1.36～1.50']
    assert adjoining_bands(['1.84～2.22','1.84～2.00','1.84～2.00','1.84～2.00']) == ['1.84～2.22','1.84～1.84','1.84～1.84','1.84～1.84']
    with pytest.raises(AssertionError,match='下界出现回升'):
        adjoining_bands(['1.91～2.09','1.76～2.09','1.80～1.95','1.36～1.95'])


def test_matrix_continuity_check_locates_overlap_and_gap():
    check_adjoining_matrix('| 条件 | 1.91～2.09 | 1.76～1.91 | 1.50～1.76 | 1.36～1.50 |', '计算表.json[示例]')
    for upper in ['1.90','2.09']:
        with pytest.raises(AssertionError,match=r'计算表.json\[示例\]:1'):
            check_adjoining_matrix(f'| 条件 | 1.91～2.09 | 1.76～{upper} | 1.50～1.76 | 1.36～1.50 |', '计算表.json[示例]')


def test_capacity_period_must_match_every_annual_record():
    annual=[{'year':year,'capacity_mva':2027.0 if year<2027 else 2057.0} for year in range(2022,2028)]
    check_capacity_period(annual,2022,2026,2027.0)
    with pytest.raises(AssertionError,match='容量保持年份范围'):
        check_capacity_period(annual,2022,2027,2027.0)


def fixture(body):
    return E.fromstring(('<w:document xmlns:w="'+NS['w']+'"><w:body>'+body+'</w:body></w:document>').encode())


def test_followup_reuses_unchanged_revision_id_and_date():
    old=fixture('<w:p><w:ins w:id="8" w:author="xh" w:date="2026-10-18T08:12:00+08:00"><w:r><w:t>保留句</w:t></w:r></w:ins></w:p>'
                '<w:p><w:ins w:id="9" w:author="xh" w:date="2026-10-19T09:00:00+08:00"><w:r><w:t>旧句</w:t></w:r></w:ins></w:p>')
    new=fixture('<w:p><w:ins w:id="1" w:author="xh" w:date="2026-10-19T10:00:00+08:00"><w:r><w:t>保留句</w:t></w:r></w:ins></w:p>'
                '<w:p><w:ins w:id="2" w:author="xh" w:date="2026-10-19T10:00:00+08:00"><w:r><w:t>新句</w:t></w:r></w:ins></w:p>')
    rels=b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
    before={'word/document.xml':E.tostring(old),'word/_rels/document.xml.rels':rels}
    after={'word/document.xml':E.tostring(new),'word/_rels/document.xml.rels':rels}
    fresh,record=reuse_unchanged_blocks(new,before,after)
    assert E.tostring(new.find('.//'+qn('p')))==E.tostring(old.find('.//'+qn('p')))
    assert record['未变修订ID及日期保留']==1
    assert new.xpath('.//w:ins/@w:id',namespaces=NS)==['8','11']
    assert '11' in fresh


def test_reused_bookmark_ids_do_not_collide_with_later_new_blocks():
    old=fixture('<w:p><w:bookmarkStart w:id="5" w:name="keep"/><w:r><w:t>保留</w:t></w:r><w:bookmarkEnd w:id="5"/></w:p>')
    new=fixture('<w:p><w:bookmarkStart w:id="3" w:name="keep"/><w:r><w:t>保留</w:t></w:r><w:bookmarkEnd w:id="3"/></w:p>'
                '<w:p><w:bookmarkStart w:id="5" w:name="new1"/><w:r><w:t>新增一</w:t></w:r><w:bookmarkEnd w:id="5"/></w:p>'
                '<w:p><w:bookmarkStart w:id="6" w:name="new2"/><w:r><w:t>新增二</w:t></w:r><w:bookmarkEnd w:id="6"/></w:p>')
    rels=b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
    parts=lambda root:{'word/document.xml':E.tostring(root),'word/_rels/document.xml.rels':rels}
    reuse_unchanged_blocks(new,parts(old),parts(new))
    starts=new.xpath('.//w:bookmarkStart/@w:id',namespaces=NS)
    assert len(starts)==len(set(starts))==3
    assert sorted(starts)==sorted(new.xpath('.//w:bookmarkEnd/@w:id',namespaces=NS))


def test_incremental_text_preserves_original_comment_and_revision():
    root=fixture('<w:p><w:commentRangeStart w:id="7"/><w:r><w:t>原句内容</w:t></w:r>'
        '<w:commentRangeEnd w:id="7"/><w:ins w:id="8" w:author="甲方"><w:r><w:t>补充</w:t></w:r></w:ins></w:p>')
    original=E.tostring(root)
    Editor(root).replace(root.find('.//'+qn('p')),'原句改写内容补充')
    assert text(view(root,True))=='原句改写内容补充'
    assert text(view(root,False))=='原句内容补充'
    for accepted in [True,False]:
        result=view(root,accepted)
        assert result.xpath('.//w:commentRangeStart/@w:id',namespaces=NS)==['7']
        assert result.xpath('.//w:ins[@w:author="甲方"]/@w:id',namespaces=NS)==['8']
    assert b'commentRangeEnd' in original


def test_row_replacement_rejects_to_original_table():
    root=fixture('<w:tbl><w:tr><w:tc><w:p><w:r><w:t>2025旧值</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
    editor=Editor(root);old=root.find('.//'+qn('tbl'));editor.delete_block(old)
    new=fixture('<w:tbl><w:tr><w:tc><w:p><w:r><w:t>2035新值</w:t></w:r></w:p></w:tc></w:tr></w:tbl>').find('.//'+qn('tbl'))
    editor.insert_block(new)
    for row in new.findall(qn('tr')):old.append(row)
    assert text(view(root,True))=='2035新值'
    assert text(view(root,False))=='2025旧值'
    assert len(view(root,True).xpath('.//w:tbl/w:tr',namespaces=NS))==1


def test_rejected_paragraph_properties_restore_original_indent():
    root=fixture('<w:p><w:pPr><w:jc w:val="center"/><w:ind w:left="0"/>'
        '<w:pPrChange w:id="2" w:author="xh"><w:pPr><w:ind w:left="420"/></w:pPr></w:pPrChange>'
        '</w:pPr><w:r><w:t>图题</w:t></w:r></w:p>')
    accepted=view(root,True);rejected=view(root,False)
    assert accepted.xpath('.//w:pPr/w:ind/@w:left',namespaces=NS)==['0']
    assert rejected.xpath('.//w:pPr/w:ind/@w:left',namespaces=NS)==['420']
    assert not rejected.xpath('.//w:pPr/w:jc',namespaces=NS)
