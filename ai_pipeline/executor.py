"""
executor.py —— 环节④：接口/页面自动化执行（V2，完全去除硬编码）

跟V1版本的核心区别：
V1：代码里写死 REGISTER_PREFIXES = ("F-01", "F-03", ...) 来判断"这条用例该去哪个页面"，
    只对这一个项目的编号规则有效，换个项目就要改代码。
V2：这些判断全部交给AI在环节③生成用例时一并决定（见prompts.py），
    本文件不认识任何项目专属的字符串，只负责"照着AI给的指令去操作浏览器"。
    唯一需要的外部信息是 ui_manifest.json（这个系统有哪些页面/字段/按钮），
    换成任何其他项目，只需要换一份 ui_manifest.json，这个文件完全不用改。
"""

import re
import json
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:3000"


def build_button_text_pattern(button_text: str):
    """
    Ant Design会给两个汉字的按钮文字自动插入一个空格（比如"注册"渲染成"注 册"），
    这里构造一个正则：字符之间允许出现任意空白（包括没有），保证不管UI库怎么排版都能匹配上。
    """
    escaped_chars = [re.escape(ch) for ch in button_text]
    pattern_str = r"\s*".join(escaped_chars)
    return re.compile(pattern_str)


def build_selector_lookup(ui_manifest: dict) -> dict:
    """
    把 ui_manifest 转换成一个方便查询的字典：
    { "/register": {"username": {"selector_type": "placeholder", "selector_value": "用户名（至少6位）"}, ...}, ... }
    """
    lookup = {}
    for page_def in ui_manifest.get("pages", []):
        route = page_def["route"]
        lookup[route] = {
            field["field_name"]: {
                "selector_type": field["selector_type"],
                "selector_value": field["selector_value"],
            }
            for field in page_def.get("fields", [])
        }
    return lookup


def fill_field(page, selector_type: str, selector_value: str, value: str):
    """根据selector_type，用对应方式定位到输入框并填值。目前支持placeholder，可按需扩展。"""
    if selector_type == "placeholder":
        page.get_by_placeholder(selector_value, exact=True).fill(value)
    elif selector_type == "label":
        page.get_by_label(selector_value, exact=True).fill(value)
    elif selector_type == "testid":
        page.get_by_test_id(selector_value).fill(value)
    else:
        raise ValueError(f"暂不支持的selector_type：{selector_type}")


def extract_quoted_message(text: str) -> str:
    """
    从"预期结果"里提取真正的提示文案：
    优先取引号里的内容；没有引号但含"提示"二字的，取"提示"后面的部分；否则返回整句话。
    """
    quoted_pattern = r"[\'\u2018\u2019\"\u201c\u201d]([^\'\u2018\u2019\"\u201c\u201d]+)[\'\u2018\u2019\"\u201c\u201d]"
    match = re.search(quoted_pattern, text)
    if match:
        return match.group(1)
    if "提示" in text:
        return text.split("提示", 1)[1].strip()
    return text


def judge_pass(expected: str, actual: str) -> str:
    """拿预期结果里的关键提示文案，看它是否出现在实际结果里，判定通过/失败"""
    key_phrase = extract_quoted_message(expected)
    if key_phrase in actual:
        return "通过"
    if "成功" in expected and ("成功" in actual or "已跳转" in actual or "欢迎" in actual):
        return "通过"
    return "失败"


def run_setup_step(page, setup: dict, selector_lookup: dict):
    """
    执行"前置准备步骤"，用来提前把某条用例依赖的数据造出来（比如先注册一次，供后面测重复注册用）。
    这里不关心执行是否"成功"——哪怕这个用户名之前已经被造过、这次报"已存在"也无所谓，
    目的只是"确保这份数据存在"，不是要验证这一步本身的对错。
    """
    route = setup["执行页面路径"]
    field_map = setup["字段填写映射"]
    button_text = setup["提交按钮文字"]

    page_selectors = selector_lookup.get(route)
    if page_selectors is None:
        return  # UI说明书里没有这个页面，跳过，不影响主流程

    page.goto(f"{BASE_URL}{route}")
    page.wait_for_timeout(500)

    for field_name, value in field_map.items():
        selector_info = page_selectors.get(field_name)
        if selector_info is None:
            continue
        try:
            fill_field(page, selector_info["selector_type"], selector_info["selector_value"], value)
        except Exception:
            pass  # 准备步骤本身出小问题不影响主流程，继续尝试往下走

    try:
        button_pattern = build_button_text_pattern(button_text)
        page.locator("button").filter(has_text=button_pattern).click()
        page.wait_for_timeout(800)
    except Exception:
        pass


def run_case(page, case: dict, selector_lookup: dict) -> str:
    """
    执行一条测试用例，完全依据AI在这条用例里给出的指令：
    执行页面路径 / 字段填写映射 / 提交按钮文字
    不做任何针对具体需求编号的特判。
    如果这条用例带有"前置准备步骤"，会先默默执行一遍，确保依赖的数据已经存在。
    """
    setup = case.get("前置准备步骤")
    if setup:
        run_setup_step(page, setup, selector_lookup)

    route = case["执行页面路径"]
    field_map = case["字段填写映射"]
    button_text = case["提交按钮文字"]

    page_selectors = selector_lookup.get(route)
    if page_selectors is None:
        return f"（UI说明书里找不到页面 {route}，无法执行）"

    page.goto(f"{BASE_URL}{route}")
    page.wait_for_timeout(500)

    for field_name, value in field_map.items():
        selector_info = page_selectors.get(field_name)
        if selector_info is None:
            return f"（UI说明书里页面{route}找不到字段{field_name}，无法执行）"
        fill_field(page, selector_info["selector_type"], selector_info["selector_value"], value)

    route_before = page.url
    button_pattern = build_button_text_pattern(button_text)
    page.locator("button").filter(has_text=button_pattern).click()
    page.wait_for_timeout(800)

    # 通用信号1：页面路由发生了变化，说明操作大概率成功并跳转
    if page.url != route_before:
        return f"操作成功，页面已跳转至 {page.url.replace(BASE_URL, '')}"

    # 通用信号2：页面上出现了提示文字（大多数表单会用<p>展示校验/错误信息）
    # 注意：要排除"没有账号？去注册"这类固定导航链接段落（特征是内部包含<a>标签），
    # 不然会永远抓到页面最下面那行固定文字，而不是真正的动态提示。
    result_texts = []
    for p_locator in page.locator("p").all():
        if p_locator.locator("a").count() > 0:
            continue
        text = p_locator.text_content()
        if text and text.strip():
            result_texts.append(text.strip())

    return result_texts[-1] if result_texts else "（页面未出现任何提示，也未发生跳转，可能存在异常）"


def run_all(test_cases: list, ui_manifest: dict) -> list:
    """对每一条测试用例，真实操作浏览器执行一遍，回填 实际结果 和 是否通过"""
    import os
    selector_lookup = build_selector_lookup(ui_manifest)
    os.makedirs("output/debug_screenshots", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for case in test_cases:
            try:
                actual = run_case(page, case, selector_lookup)
            except Exception as e:
                actual = f"（执行出错：{e}）"
                screenshot_path = f"output/debug_screenshots/{case.get('用例编号', 'unknown')}.png"
                try:
                    page.screenshot(path=screenshot_path)
                    actual += f"\n（出错时的页面截图已保存到 {screenshot_path}，可以打开看看当时页面卡在哪）"
                except Exception:
                    pass

            case["实际结果"] = actual
            case["是否通过"] = judge_pass(case.get("预期结果", ""), actual)

            print(f"  [{case.get('用例编号')}] 预期：{case.get('预期结果')} | 实际：{actual} | {case['是否通过']}")

        browser.close()

    return test_cases
