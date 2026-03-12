from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 这里不直接关联 app，防止循环导入
db = SQLAlchemy()


# 如果要增加新的变量 可以更新一下database
# flask db migrate -m "add upload_date[这是新变量名]"
# flask db migrate -m "add is_hidden to provider"
# flask db upgrade


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    before_img = db.Column(db.String(100))
    after_img = db.Column(db.String(100))
    is_hidden = db.Column(db.Boolean, default=False)
    upload_date = db.Column(db.DateTime, default=datetime.now)
    rank = db.Column(db.Integer, default=10)
    tag = db.Column(db.String(50), default='pico')

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    bio = db.Column(db.Text)
    photo = db.Column(db.String(100))
    is_hidden = db.Column(db.Boolean, default=False)
    # 数值越小，排名越靠前（默认值为 10）
    rank = db.Column(db.Integer, default=10)