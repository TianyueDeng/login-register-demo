# AI自动化测试插件原型 V2 —— 完全数据驱动，无项目专属硬编码

## 跟V1版本的核心区别

V1版本里，`executor.py`写死了"F-01系列去注册页"这种判断逻辑，只对这一个项目有效。
V2版本把这些知识彻底移出Python代码：
- **该去哪个页面、填哪些字段、点哪个按钮**——由AI在生成测试用例时直接决定并写进结果里
- **每个页面长什么样（字段名对应什么占位符文字、按钮文字是什么）**——写在`ui_manifest.json`这份外部数据里

`executor.py`本身不包含任何"F-01""注册""登录"这类项目专属字符串，换一个完全不同的项目，
只需要换一份`ui_manifest.json`，Python代码一行都不用改。

## 文件说明

```
ai_pipeline/
├── prompts.py           ← 两份Prompt方案（V2：方案2新增UI说明书输入+执行指令输出）
├── pipeline.py           ← 环节①②③：PRD解析 + 测试用例生成
├── executor.py           ← 环节④：完全数据驱动的自动化执行，无硬编码
├── main.py               ← 运行环节①②③的入口
├── run_stage4.py          ← 运行环节④的入口
├── ui_manifest.json       ← 描述被测系统的页面/字段/按钮（换项目只改这个文件）
├── sample_prd.txt         ← 示例PRD
└── requirements.txt       ← 依赖清单
```

## 运行步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 设置API密钥
```powershell
$env:ANTHROPIC_API_KEY="你的密钥"
```
（如果用OpenAI，把pipeline.py顶部几行换成OpenAI SDK的写法，之前已经教过怎么改）

### 3. 确认前后端都在跑
- Flask：`http://localhost:5000`
- React：`http://localhost:3000`

### 4. 跑环节①②③（生成需求规格说明书 + 测试用例）
```bash
python main.py
```
生成 `output/requirement_spec.json` 和 `output/test_cases.json`

**打开 `output/test_cases.json` 看一眼**，你会看到每条用例除了原来的11个字段，
多了3个新字段：`执行页面路径`、`字段填写映射`、`提交按钮文字`——这是AI自己根据
`ui_manifest.json`判断出来的，不是人工填的。

### 5. 跑环节④（真实自动化执行）
```bash
python run_stage4.py
```
程序会照着上一步AI生成的执行指令，真实操作浏览器，把结果写入
`output/test_cases_executed.json`，终端也会打印统计和未通过清单。

## 如果想换成别的项目验证"零硬编码"这件事

1. 把`sample_prd.txt`换成别的项目的PRD
2. 把`ui_manifest.json`换成描述那个新项目页面结构的说明书
3. 重新运行`main.py`和`run_stage4.py`
4. **`executor.py`不需要做任何修改**——这就是这次重构要证明的事
