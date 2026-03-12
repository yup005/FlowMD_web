import os
from dotenv import load_dotenv # 导入插件

# 关键：手动加载 .env 文件中的变量到系统内存
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    # 基础配置
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # 安全钥匙：优先从环境变量读取，读不到才用默认值
    # 这样你部署到服务器时，只需修改服务器的环境变量，不需要动代码
    ADMIN_KEY = os.environ.get('ADMIN_KEY')
    if not ADMIN_KEY:
        raise ValueError("CAN NOT FIND ADMIN_KEY！")

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("CAN NOT FIND SECRET_KEY！")

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'clinic.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 文件上传路径
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')