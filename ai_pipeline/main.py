"""
main.py —— 运行入口（环节①②③）
读取 sample_prd.txt 和 ui_manifest.json，跑完整流水线，
把结果保存到 output/requirement_spec.json 和 output/test_cases.json
"""

import json
import os
from pipeline import run_pipeline


def main():
    with open("sample_prd.txt", "r", encoding="utf-8") as f:
        prd_text = f.read()

    result = run_pipeline(prd_text, ui_manifest_path="ui_manifest.json")

    os.makedirs("output", exist_ok=True)

    with open("output/requirement_spec.json", "w", encoding="utf-8") as f:
        json.dump(result["requirement_spec"], f, ensure_ascii=False, indent=2)

    with open("output/test_cases.json", "w", encoding="utf-8") as f:
        json.dump(result["test_cases"], f, ensure_ascii=False, indent=2)

    print("全部完成！结果已保存到 output/ 文件夹：")
    print("  - output/requirement_spec.json  （需求规格说明书）")
    print("  - output/test_cases.json        （测试用例，含自动化执行指令）")


if __name__ == "__main__":
    main()
