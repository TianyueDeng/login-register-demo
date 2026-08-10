# 后端运行说明

## 1. 安装依赖
```bash
pip install -r requirements.txt
```

## 2. 补全代码
按 app.py、database.py 里的 TODO 注释，参照《接口与数据库设计文档》《需求规格说明书》填写业务逻辑。

## 3. 启动服务
```bash
python app.py
```
启动后，服务运行在 http://localhost:5000

## 4. 自测接口（不用等前端页面做好）
可以用 Postman，或者用 curl 命令行直接测试，比如：

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test01", "password": "123456", "confirm_password": "123456"}'
```
