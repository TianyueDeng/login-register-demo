"""
run_stage56.py —— 环节⑤⑥独立运行入口
读取 output/test_cases_executed.json（环节④跑完、已经填好实际结果的用例），
挑出失败的用例生成Bug单（环节⑥），
再结合统计数据生成完整测试报告（环节⑤）。

运行前提：已经跑过 run_stage4.py，生成了 output/test_cases_executed.json
"""

import json
import os
from pipeline import generate_bug_tickets, generate_report_narrative
from report_builder import compute_statistics, get_failed_cases, build_markdown_report


def main():
    input_path = "output/test_cases_executed.json"
    if not os.path.exists(input_path):
        print(f"找不到 {input_path}，请先运行 run_stage4.py 完成自动化执行。")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        executed_cases = json.load(f)

    print("【步骤1/3】计算统计数据（代码计算，不依赖AI，保证准确）……")
    stats = compute_statistics(executed_cases)
    failed_cases = get_failed_cases(executed_cases)
    print(f"共 {stats['总用例数']} 条，通过 {stats['总通过数']} 条，不通过 {stats['总不通过数']} 条。\n")

    print("【步骤2/3】正在调用大模型生成Bug单……")
    bugs = generate_bug_tickets(failed_cases)
    print(f"共生成 {len(bugs)} 条Bug单。\n")

    print("【步骤3/3】正在调用大模型撰写测试报告……")
    narrative = generate_report_narrative(stats, bugs)
    report_md = build_markdown_report(stats, bugs, narrative)
    print("测试报告生成完成。\n")

    os.makedirs("output", exist_ok=True)

    with open("output/bug_tickets.json", "w", encoding="utf-8") as f:
        json.dump(bugs, f, ensure_ascii=False, indent=2)

    with open("output/test_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print("全部完成！结果已保存到：")
    print("  - output/bug_tickets.json   （AI生成的Bug单）")
    print("  - output/test_report.md    （AI生成的测试报告）")


if __name__ == "__main__":
    main()
