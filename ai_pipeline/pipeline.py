"""
pipeline.py —— 核心流水线逻辑
对应架构图环节1&2（PRD解析→需求结构化）与环节③（测试用例自动生成）
"""

import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

from prompts import PROMPT_1_PRD_PARSING, PROMPT_2_TESTCASE_GENERATION

load_dotenv()

MODEL = "claude-sonnet-4-6"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), timeout=60)


def _strip_code_fence(text: str) -> str:
    """去掉模型可能返回的```json代码块标记"""
    t = text.strip()
    t = re.sub(r"^```json\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"^```\s*", "", t)
    t = re.sub(r"```\s*$", "", t)
    return t.strip()


def call_gpt(prompt_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt_text}],
    )
    return response.choices[0].message.content


def parse_prd(prd_text: str) -> list:
    """
    环节1&2：PRD解析 → 需求结构化
    输入：PRD原文（字符串）
    输出：需求规格说明书（list of dict）
    """
    raw = call_gpt(PROMPT_1_PRD_PARSING + prd_text)
    cleaned = _strip_code_fence(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"PRD解析结果不是合法JSON，原始返回：\n{raw}") from e


def generate_test_cases(requirement_spec: list, ui_manifest: dict) -> list:
    """
    环节3：测试用例自动生成
    输入：
        requirement_spec —— 需求规格说明书（list of dict，即parse_prd的输出）
        ui_manifest —— 描述被测系统页面/字段/按钮的说明书（dict）
    输出：测试用例（list of dict），每条包含执行页面路径/字段填写映射/提交按钮文字
    """
    spec_json_text = json.dumps(requirement_spec, ensure_ascii=False, indent=2)
    manifest_json_text = json.dumps(ui_manifest, ensure_ascii=False, indent=2)

    prompt = PROMPT_2_TESTCASE_GENERATION.replace(
        "{requirement_spec_json}", spec_json_text
    ).replace(
        "{ui_manifest_json}", manifest_json_text
    )

    raw = call_gpt(prompt)
    cleaned = _strip_code_fence(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"测试用例生成结果不是合法JSON，原始返回：\n{raw}") from e


def run_pipeline(prd_text: str, ui_manifest_path: str = "ui_manifest.json") -> dict:
    """
    完整流水线：PRD → 需求规格说明书 → 测试用例（含自动化执行指令）
    返回一个包含两步结果的字典，方便调用方分别取用
    """
    print("【步骤1/2】正在调用大模型解析PRD……")
    requirement_spec = parse_prd(prd_text)
    print(f"解析完成，共生成 {len(requirement_spec)} 条需求条目。\n")

    with open(ui_manifest_path, "r", encoding="utf-8") as f:
        ui_manifest = json.load(f)

    print("【步骤2/2】正在调用大模型生成测试用例（含自动化执行指令）……")
    test_cases = generate_test_cases(requirement_spec, ui_manifest)
    print(f"生成完成，共产出 {len(test_cases)} 条测试用例。\n")

    return {
        "requirement_spec": requirement_spec,
        "test_cases": test_cases,
    }


def generate_bug_tickets(failed_cases: list) -> list:
    """
    环节6：Bug自动推送
    输入：执行后判定为"失败"的测试用例列表
    输出：标准化Bug单（list of dict）
    """
    from prompts import PROMPT_3_BUG_GENERATION

    if not failed_cases:
        return []

    failed_json_text = json.dumps(failed_cases, ensure_ascii=False, indent=2)
    prompt = PROMPT_3_BUG_GENERATION.replace("{failed_cases_json}", failed_json_text)

    raw = call_gpt(prompt)
    cleaned = _strip_code_fence(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Bug单生成结果不是合法JSON，原始返回：\n{raw}") from e


def generate_report_narrative(stats: dict, bugs: list) -> dict:
    """
    环节5：测试报告生成（叙述部分）
    输入：compute_statistics()算出的统计数据 + generate_bug_tickets()生成的Bug清单
    输出：{"测试概述":..., "重点问题说明":..., "测试结论":..., "风险与建议":[...]}
    """
    from prompts import PROMPT_4_REPORT_NARRATIVE

    stats_json_text = json.dumps(stats, ensure_ascii=False, indent=2)
    bugs_json_text = json.dumps(bugs, ensure_ascii=False, indent=2)

    prompt = PROMPT_4_REPORT_NARRATIVE.replace(
        "{stats_json}", stats_json_text
    ).replace(
        "{bugs_json}", bugs_json_text
    )

    raw = call_gpt(prompt)
    cleaned = _strip_code_fence(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"测试报告叙述生成结果不是合法JSON，原始返回：\n{raw}") from e
