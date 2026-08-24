"""
app.py —— Flask入口，定义所有接口（路由）
对应《接口与数据库设计文档》第二章：接口设计
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection, init_db

app = Flask(__name__)

# CORS：因为React跑在 localhost:3000，Flask跑在 localhost:5000，
# 端口不一样，浏览器默认会拦截这种"跨域"请求。
# 加上这一行，等于告诉浏览器"允许来自其他端口的请求访问这个后端"。
CORS(app)


# ---------- 注册接口 ----------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    username = username.strip()
    password = password.strip()

    if not username:
        return jsonify({"status": "fail", "message": "用户名不能为空"}), 400

    if not password:
        return jsonify({"status": "fail", "message": "密码不能为空"}), 400

    if password != confirm_password:
        return jsonify({"status": "fail", "message": "两次输入的密码不一致"}), 400

    conn = get_db_connection()
    existing_user = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({"status": "fail", "message": "用户名已存在"}), 409
    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "注册成功"}), 200


# ---------- 登录接口 ----------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    username = username.strip()
    password = password.strip()

    if not username:
        return jsonify({"status": "fail", "message": "用户名不能为空"}), 400

    conn = get_db_connection()
    existing_user = conn.execute(
        "SELECT id FROM users WHERE username = ? AND password = ?", (username,password)
    ).fetchone()
    conn.close()
    if existing_user:
        return jsonify({ "status": "success", "message": "登录成功", "data": { "username": username } }), 200
    
    return jsonify({ "status": "fail", "message": "用户名或密码错误"}), 401

if __name__ == '__main__':
    init_db()          # 启动时先确保数据库表已经建好
    app.run(debug=True, port=5000)
