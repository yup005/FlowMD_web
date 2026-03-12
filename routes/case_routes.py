import os
import time  # 新增：用于生成时间戳解决重名问题
from flask import Blueprint, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename  # 新增：确保文件名安全
from models import db, Case

case_bp = Blueprint('case', __name__)


@case_bp.route('/add_case', methods=['POST'])
def add_case():
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403

    title = request.form.get('title')
    desc = request.form.get('description')
    tag = request.form.get('tag', 'General')

    # --- 1. 健壮性改进：安全转换 rank ---
    raw_rank = request.form.get('rank')
    try:
        rank = int(raw_rank) if raw_rank else 10
    except (ValueError, TypeError):
        rank = 10

    before = request.files.get('before')
    after = request.files.get('after')

    if before and after:
        # --- 2. 文件名冲突改进：时间戳 + 安全过滤 ---
        timestamp = int(time.time())

        # 处理 Before 图片：原文件名 -> 171000_secure_name.jpg
        b_filename = f"{timestamp}_{secure_filename(before.filename)}"
        before.save(os.path.join(current_app.config['UPLOAD_FOLDER'], b_filename))

        # 处理 After 图片
        a_filename = f"{timestamp}_{secure_filename(after.filename)}"
        after.save(os.path.join(current_app.config['UPLOAD_FOLDER'], a_filename))

        # 写入数据库记录（已包含 rank 和 tag）
        new_case = Case(
            title=title,
            description=desc,
            before_img=b_filename,
            after_img=a_filename,
            rank=rank,
            tag=tag
        )
        db.session.add(new_case)
        db.session.commit()

    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))


@case_bp.route('/delete_case/<int:id>')
def delete_case(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403
    case = Case.query.get_or_404(id)

    # 生产建议：如果需要物理删除服务器上的图片文件，可以在这里加上 os.remove
    db.session.delete(case)
    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))


@case_bp.route('/hide_case/<int:id>')
def hide_case(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403
    case = Case.query.get_or_404(id)
    case.is_hidden = not case.is_hidden
    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))


@case_bp.route('/edit_case/<int:id>', methods=['POST'])
def edit_case(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403

    case = Case.query.get_or_404(id)

    case.title = request.form.get('title')
    case.description = request.form.get('description')
    case.tag = request.form.get('tag', 'General')  # 加上默认值，防止为空

    # 保存 rank 权重字段（沿用你写的 try-except 逻辑，很棒）
    new_rank = request.form.get('rank')
    if new_rank:
        try:
            case.rank = int(new_rank)
        except ValueError:
            case.rank = 10

    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))