import sqlite3
import os
from flask import current_app, g

def get_db_conn():
    if 'db' not in g:
        # 确保我们使用的是实例文件夹中的数据库路径
        db_path = current_app.config['DATABASE']
        # 确保数据库所在的目录存在
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db_conn()

    with current_app.open_resource('db.sql', mode='r') as f:
        db.executescript(f.read())
    
    # 先插入一个测试用户
    db.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", ('testuser', 'pbkdf2:sha256:600000$lA381FpA1N7xVbF3$87a17533879e0f065ba259d863f6f4e2c2f719e7a88e99905a2879133b05a557', 'testuser@example.com'))

    #再插入两条博客，user_id=1
    db.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", ('学习Flask1', '第一条实例', 1))
    db.execute("INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)", ('学习Flask2', '第二条示例', 1))

    # 可选：插入一条测试书籍
    db.execute("INSERT INTO books (title, authors, publisher, publishedDate, description, thumbnail, infoLink) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ('测试书籍', '测试作者', '测试出版社', '2024-01-01', '这是一本测试书籍', '', ''))
    
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)

def get_post(post_id):
    conn = get_db_conn()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    return post

def get_user_by_username(username):
    conn = get_db_conn()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    return user

def get_user_by_id(user_id):
    conn = get_db_conn()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return user