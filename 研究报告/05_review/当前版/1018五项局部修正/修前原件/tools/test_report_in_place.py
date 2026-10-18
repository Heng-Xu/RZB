"""报告原件修订视图的回归检查：原批注、已有修订及拒绝后恢复。"""
from lxml import etree as E

from revise_report_in_place import Editor, NS, qn, text, view
import pytest
from verify_annual_report_update import check_capacity_period


def test_capacity_period_must_match_every_annual_record():
    annual=[{'year':year,'capacity_mva':2027.0 if year<2027 else 2057.0} for year in range(2022,2028)]
    check_capacity_period(annual,2022,2026,2027.0)
    with pytest.raises(AssertionError,match='容量保持年份范围'):
        check_capacity_period(annual,2022,2027,2027.0)


def fixture(body):
    return E.fromstring(('<w:document xmlns:w="'+NS['w']+'"><w:body>'+body+'</w:body></w:document>').encode())


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
