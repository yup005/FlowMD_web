import os
from flask import Blueprint, request, redirect, url_for, current_app
from models import db, Provider

provider_bp = Blueprint('provider', __name__)


@provider_bp.route('/add_provider', methods=['POST'])
def add_provider():
    if request.args.get('key') != current_app.config['ADMIN_KEY']:
        return "Unauthorized", 403

    name = request.form.get('name')
    job_title = request.form.get('p_title')
    bio = request.form.get('bio')
    photo = request.files.get('photo')

    if photo:
        photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename))
        new_p = Provider(name=name, job_title=job_title, bio=bio, photo=photo.filename)
        db.session.add(new_p)
        db.session.commit()

    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))

@provider_bp.route('/delete_provider/<int:id>')
def delete_provider(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']: return "Unauthorized", 403
    p = Provider.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))


@provider_bp.route('/hide_provider/<int:id>')
def hide_provider(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']: return "Unauthorized", 403
    p = Provider.query.get_or_404(id)
    p.is_hidden = not p.is_hidden
    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))


@provider_bp.route('/edit_provider/<int:id>', methods=['POST'])
def edit_provider(id):
    if request.args.get('key') != current_app.config['ADMIN_KEY']: return "Unauthorized", 403
    p = Provider.query.get_or_404(id)

    p.name = request.form.get('name')
    p.job_title = request.form.get('job_title')
    p.bio = request.form.get('bio')

    # 接收 rank 值并转换为整数
    new_rank = request.form.get('rank')
    if new_rank:
        p.rank = int(new_rank)

    db.session.commit()
    return redirect(url_for('admin', key=current_app.config['ADMIN_KEY']))