"""
database.py —— 负责数据库的建表与连接
对应《接口与数据库设计文档》第一章：数据库设计
"""

import sqlite3

DB_NAME = "users.db"


def get_db_connection():
    """
    获取一个数据库连接。
    每次要读/写数据库的时候，都调用这个函数拿到连接。
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 让查询结果可以像字典一样用列名取值，比如 row['username']
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
