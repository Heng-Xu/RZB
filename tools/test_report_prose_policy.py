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

    def test_known_input_and_template_misstatements_are_detected(self):
        for text in [
            '年网供最大负荷统一标定到容载比2.00。',
            '将地区名称和规模转换为五站仿真模板结构。',
            '两类方案本站总容量相同，仍需结合主变组合和邻站转接安排解释储能配置。',
        ]:
            with self.subTest(text=text):
                self.assertTrue(self.check(text))
        self.assertEqual(self.check('两类方案共用实际年度负荷和初始设备，推广计算采用独立五站模板。'),[])

    def test_nested_generated_text_is_located(self):
        errors=self.check('标题\n[[SECTION:analysis]]',{'analysis':'结果\n[[TABLE:comparison]]'},
                          {'comparison':'表题\n不能直接等同于设备新增过多。'})
        self.assertTrue(any('第三章.md:2 → 生成段落.json[analysis]:2 → 计算表.json[comparison]:2' in e for e in errors))

    def test_unreferenced_records_are_not_body(self):
        self.assertEqual(self.check('正文',{'archived':'不能直接等同于设备新增过多。'}),[])

    def test_actual_policy_version_name_is_preserved(self):
        self.assertEqual(self.check('2025年4月《配电网规划设计技术导则（修订稿）》第6.2.2.1条[69]。'),[])
        self.assertTrue(self.check('研究报告修订稿采用新结果。'))

    def test_multiple_constraints_need_explicit_math_break(self):
        self.assertTrue(self.check(r'\begin{aligned} A&\leq B, C&\leq D.\end{aligned}'))
        self.assertEqual(self.check(r'\begin{aligned} A&\leq B,\\ C&\leq D.\end{aligned}'),[])

    def test_reference_cycle_fails(self):
        with self.assertRaisesRegex(ValueError,'正文引用循环'):
            self.check('[[SECTION:a]]',{'a':'[[SECTION:a]]'})

    def test_feedback_1013_prose_and_fixed_values(self):
        for text in ['采用收资《近5年容载比》中的记录。',
                     '储能价格另作专项敏感性分析，不增加主矩阵查表维度。',
                     '| 储能支撑持续时间 | 2、4、6 h | ≤2 h；(2 h,4 h]；>4 h |',
                     '| 负荷分散系数 | 1.00、1.10、1.15 | ≤1.10；>1.10 |']:
            with self.subTest(text=text):self.assertTrue(self.check(text))
        for text in ['根据项目提供的2021—2025年容量及负荷记录计算。',
                     '| 储能支撑持续时间 | 2、4、6 h | 2 h；4 h；6 h |',
                     '六项参数在本版均列入推广矩阵。']:
            with self.subTest(text=text):self.assertEqual(self.check(text),[])

if __name__=='__main__':
    unittest.main()
