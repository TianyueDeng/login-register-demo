"""
run_stage4.py —— 环节④独立运行入口
读取 output/test_cases.json（已包含AI生成的执行页面路径/字段填写映射/提交按钮文字）
和 ui_manifest.json，用Playwright真实操作浏览器执行每一条用例，
结果保存到 output/test_cases_executed.json

运行前提：
1. Flask后端已经在 http://localhost:5000 跑起来
2. React前端已经在 http://localhost:3000 跑起来
"""

import json
import os
from executor import run_all


def main():
    input_path = "output/test_cases.json"
    if not os.path.exists(input_path):
        print(f"找不到 {input_path}，请先运行 main.py 生成测试用例。")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    with open("ui_manifest.json", "r", encoding="utf-8") as f:
        ui_manifest = json.load(f)

    print(f"读取到 {len(test_cases)} 条测试用例，开始自动化执行……\n")
    executed_cases = run_all(test_cases, ui_manifest)

    output_path = "output/test_cases_executed.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(executed_cases, f, ensure_ascii=False, indent=2)

    passed = sum(1 for c in executed_cases if c["是否通过"] == "通过")
    failed = len(executed_cases) - passed

    print(f"\n执行完成！共 {len(executed_cases)} 条，通过 {passed} 条，失败 {failed} 条。")
    print(f"完整结果已保存到 {output_path}")

    if failed > 0:
        print("\n未通过的用例：")
        for c in executed_cases:
            if c["是否通过"] != "通过":
                print(f"  - {c['用例编号']}：预期「{c['预期结果']}」，实际「{c['实际结果']}」")


if __name__ == "__main__":
    main()
