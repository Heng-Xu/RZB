"""验证排除式说明检查能拦截复发、保留实质约束并定位生成文本。"""
from pathlib import Path
import json
import unittest
from check_report_policy import body_policy_errors

POLICY=json.loads((Path(__file__).with_name('report_policy.json')).read_text())

class ProsePolicyTests(unittest.TestCase):
    def check(self,text,sections=None,tables=None):
        return body_policy_errors([('第三章.md',text)],sections or {},tables or {},POLICY['forbidden_body_patterns'])

    def test_user_examples_are_detected(self):
        examples=[
            '不能将当前无响应解释为设备寿命没有经济意义。',
            '不能脱离设备组合单独确定。',
            '不能直接等同于设备新增过多。',
            '该比较保持线路技术能力不变，避免把造价变化解释成转供能力变化。',
            '二者的来源和统计范围不同，不将其作为两地区已核定的实际初始转供率直接比较。',
            '上述差异用于说明案例基础，不能通过两个地区的横向差值认定某一参数对容载比的独立影响。',
            '分布式电源电量渗透率下降并不表示当月光伏发电量减少。',
        ]
        for text in examples:
            with self.subTest(text=text):
                self.assertTrue(self.check(text))

    def test_substantive_limits_are_preserved(self):
        examples=[
            '建议范围内不能满足供电安全准则时，可结合实际情况适当提高。',
            '当前候选集合内单靠联络无法弥补相关缺口。',
            '当前研究未开展逐时荷电状态仿真。',
            '现有资料缺少同范围用户年电量记录。',
            '既有边不重复计建设费用，新增边按投运年计费。',
            '储能额定功率保持0.50 MW。',
            '高渗透率情景下未取得可行方案。',
        ]
        for text in examples:
            with self.subTest(text=text):
                self.assertEqual(self.check(text),[])

    def test_nested_generated_text_is_located(self):
        errors=self.check('标题\n[[SECTION:analysis]]',{'analysis':'结果\n[[TABLE:comparison]]'},
                          {'comparison':'表题\n不能直接等同于设备新增过多。'})
        self.assertTrue(any('第三章.md:2 → 生成段落.json[analysis]:2 → 计算表.json[comparison]:2' in e for e in errors))

    def test_unreferenced_records_are_not_body(self):
        self.assertEqual(self.check('正文',{'archived':'不能直接等同于设备新增过多。'}),[])

    def test_reference_cycle_fails(self):
        with self.assertRaisesRegex(ValueError,'正文引用循环'):
            self.check('[[SECTION:a]]',{'a':'[[SECTION:a]]'})

if __name__=='__main__':
    unittest.main()
