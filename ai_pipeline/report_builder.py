"""
report_builder.py —— 环节⑤⑥：测试报告生成 + Bug自动推送

设计原则：能用代码算准确的数字（统计表格），就不让AI去猜；
只有"怎么评价、怎么建议"这种需要判断的叙述性内容，才交给AI生成。
"""

import json
from datetime import date
from collections import defaultdict


def compute_statistics(executed_cases: list) -> dict:
    """
    按所属模块分组，统计每组的用例总数/通过数/不通过数/通过率。
    这一步完全由代码计算，不依赖AI，保证数字绝对准确。
    """
    by_module = defaultdict(lambda: {"total": 0, "passed": 0})

    for case in executed_cases:
        module = case.get("所属模块", "未分类")
        by_module[module]["total"] += 1
        if case.get("是否通过") == "通过":
            by_module[module]["passed"] += 1

    module_stats = []
    for module, counts in by_module.items():
        total = counts["total"]
        passed = counts["passed"]
        failed = total - passed
        pass_rate = f"{passed / total * 100:.1f}%" if total else "0%"
        module_stats.append({
            "模块": module,
            "用例总数": total,
            "通过数": passed,
            "不通过数": failed,
            "通过率": pass_rate,
        })

    total_all = len(executed_cases)
    passed_all = sum(1 for c in executed_cases if c.get("是否通过") == "通过")
    failed_all = total_all - passed_all
    overall_pass_rate = f"{passed_all / total_all * 100:.1f}%" if total_all else "0%"

    return {
        "按模块统计": module_stats,
        "总用例数": total_all,
        "总通过数": passed_all,
        "总不通过数": failed_all,
        "总通过率": overall_pass_rate,
    }


def get_failed_cases(executed_cases: list) -> list:
    """挑出"是否通过"不是"通过"的用例，这些是要生成Bug单的对象"""
    return [c for c in executed_cases if c.get("是否通过") != "通过"]


def build_markdown_report(stats: dict, bugs: list, narrative: dict) -> str:
    """
    把"代码算出的统计表格" + "AI写的叙述文字"，拼装成一份完整的Markdown测试报告。
    """
    lines = []
    lines.append("# 登录注册Demo系统 —— 测试报告（AI自动生成）\n")
    lines.append(f"生成日期：{date.today().isoformat()}\n")

    lines.append("## 一、测试概述\n")
    lines.append(narrative.get("测试概述", "") + "\n")

    lines.append("## 二、测试执行统计\n")
    lines.append("| 模块 | 用例总数 | 通过数 | 不通过数 | 通过率 |")
    lines.append("|---|---|---|---|---|")
    for row in stats["按模块统计"]:
        lines.append(f"| {row['模块']} | {row['用例总数']} | {row['通过数']} | {row['不通过数']} | {row['通过率']} |")
    lines.append(f"| **合计** | **{stats['总用例数']}** | **{stats['总通过数']}** | **{stats['总不通过数']}** | **{stats['总通过率']}** |\n")

    lines.append("## 三、缺陷统计\n")
    if bugs:
        lines.append("| Bug编号 | Bug标题 | 关联需求 | 严重程度 | 优先级 |")
        lines.append("|---|---|---|---|---|")
        for bug in bugs:
            lines.append(
                f"| {bug['Bug编号']} | {bug['Bug标题']} | {bug['关联需求编号']} | {bug['严重程度']} | {bug['优先级']} |"
            )
    else:
        lines.append("本轮测试未发现任何缺陷。")
    lines.append("")

    lines.append("## 四、重点问题说明\n")
    lines.append(narrative.get("重点问题说明", "") + "\n")

    lines.append("## 五、测试结论\n")
    lines.append(narrative.get("测试结论", "") + "\n")

    lines.append("## 六、风险与建议\n")
    for item in narrative.get("风险与建议", []):
        lines.append(f"- {item}")

    return "\n".join(lines)
