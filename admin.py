from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from models import User, db
from datetime import datetime

admin = Blueprint('admin', __name__)

def admin_required(func):
    """裝飾器確保只有管理員可以訪問視圖"""
    @login_required
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # 未授權訪問
        return func(*args, **kwargs)
    decorated_view.__name__ = func.__name__
    return decorated_view

@admin.route('/')
@admin_required
def index():
    """管理員控制面板首頁"""
    total_users = User.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    return render_template('admin/index.html', total_users=total_users, recent_users=recent_users)

@admin.route('/users')
@admin_required
def user_list():
    """用戶列表管理頁面"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    return render_template('admin/users.html', users=users)

@admin.route('/users/<int:user_id>')
@admin_required
def user_detail(user_id):
    """用戶詳細資訊頁面"""
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_detail.html', user=user)

@admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):
    """編輯用戶資訊"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        is_admin = 'is_admin' in request.form
        
        # 檢查用戶名是否已存在
        if username != user.username and User.query.filter_by(username=username).first():
            flash('用戶名已被使用', 'danger')
            return render_template('admin/user_edit.html', user=user)
        
        # 檢查郵箱是否已存在
        if email != user.email and User.query.filter_by(email=email).first():
            flash('電子郵件已被註冊', 'danger')
            return render_template('admin/user_edit.html', user=user)
        
        # 更新用戶資訊
        user.username = username
        user.email = email
        user.is_admin = is_admin
        
        # 如果提供了新密碼，則更新密碼
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('用戶資訊已更新', 'success')
            return redirect(url_for('admin.user_detail', user_id=user.id))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失敗：{str(e)}', 'danger')
    
    return render_template('admin/user_edit.html', user=user)

@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def user_delete(user_id):
    """刪除用戶"""
    user = User.query.get_or_404(user_id)
    
    # 防止刪除自己
    if user.id == current_user.id:
        flash('您不能刪除自己的帳號', 'danger')
        return redirect(url_for('admin.user_list'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('用戶已刪除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')
    
    return redirect(url_for('admin.user_list'))

@admin.route('/create_admin', methods=['GET', 'POST'])
@admin_required
def create_admin():
    """創建新管理員帳號"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # 驗證表單數據
        if not username or not email or not password:
            flash('所有字段都必須填寫', 'danger')
            return render_template('admin/create_admin.html')
        
        # 檢查用戶名和郵箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('用戶名已被使用', 'danger')
            return render_template('admin/create_admin.html')
        
        if User.query.filter_by(email=email).first():
            flash('電子郵件已被註冊', 'danger')
            return render_template('admin/create_admin.html')
        
        # 創建新管理員
        new_admin = User(username=username, email=email, is_admin=True)
        new_admin.set_password(password)
        
        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('管理員帳號創建成功', 'success')
            return redirect(url_for('admin.user_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'創建失敗：{str(e)}', 'danger')
            return render_template('admin/create_admin.html')
    
    return render_template('admin/create_admin.html') 