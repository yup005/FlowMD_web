import os
from flask import Flask, render_template, request, current_app
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

from config import Config
from models import db, Case, Provider
# 从 routes 文件夹导入蓝图对象，用于实现模块化开发
from routes.case_routes import case_bp
from routes.provider_routes import provider_bp


def create_app():
    """
    程序工厂函数：负责初始化 Flask 实例、加载配置并绑定数据库
    """
    app = Flask(__name__)

    # 1. 加载外部配置类 (config.py)
    app.config.from_object(Config)

    csrf = CSRFProtect(app)

    # 2. 数据库插件初始化
    # 将 models.py 中定义的 db 绑定到当前的 app 实例上
    db.init_app(app)

    # 3. 数据库迁移工具初始化
    # 允许我们通过终端命令 'flask db migrate' 来更新数据库表结构
    migrate = Migrate(app, db)

    # 4. 环境准备：确保存放图片的文件夹物理存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 5. 蓝图注册 (Blueprints)
    # 将不同模块的路由逻辑“拼装”到主程序中
    app.register_blueprint(case_bp)
    app.register_blueprint(provider_bp)



    @app.route('/')
    def index():
        # filter_by(is_hidden=False): 核心逻辑，确保用户只看到“上线”的内容
        cases = Case.query.filter_by(is_hidden=False).order_by(
            Case.rank.asc(),  # 第一排序：按权重升序（1在最前）
            Case.upload_date.desc()  # 第二排序：当权重相同时，按日期倒序（最新的在前）
        ).limit(4).all() # limit(4): 限制首页显示数量，保持页面简洁

        # 获取所有未隐藏的服务者/医生资料
        # asc() 表示升序，即 1 排在 2 前面
        providers = Provider.query.filter_by(is_hidden=False).order_by(Provider.rank.asc()).all()

        return render_template('index.html',
                               cases=cases,
                               providers=providers,
                               admin_key=current_app.config['ADMIN_KEY'])
    # 完整cases
    @app.route('/gallery')
    def gallery():
        all_cases = Case.query.filter_by(is_hidden=False).order_by(Case.upload_date.desc()).all()
        return render_template('archive.html', cases=all_cases)

    @app.route('/secret_admin')
    def admin():
        if request.args.get('key') != app.config['ADMIN_KEY']:
            return "Unauthorized Access", 403

        # 获取当前页码，默认为第 1 页
        page = request.args.get('page', 1, type=int)
        # 设置每页显示的数量（比如每页 10 个）
        per_page = 10

        # 案例部分进行分页, 使用 .paginate() 代替 .all()
        cases_pagination = Case.query.order_by(
            Case.rank.asc(),
            Case.upload_date.desc()
        ).paginate(page=page, per_page=10)

        # 医生部分通常数量不多，可以保持原样
        providers = Provider.query.all()

        return render_template('admin.html',
                               cases_pagination=cases_pagination,
                               providers=providers,
                               admin_key=current_app.config['ADMIN_KEY'])


    return app



if __name__ == '__main__':
    app = create_app()

    # 生产模式标准：这里不写任何数据库初始化代码。
    # 数据库的开启、升级，全部交给终端命令行。
    # with app.app_context():
    #     db.create_all()

    app.run(debug=True)