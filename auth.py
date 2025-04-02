from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # 驗證表單數據
        if not username or not email or not password:
            flash('所有字段都必須填寫', 'danger')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('兩次輸入的密碼不匹配', 'danger')
            return render_template('register.html')
        
        # 檢查用戶名和郵箱是否已存在
        user_by_username = User.query.filter_by(username=username).first()
        user_by_email = User.query.filter_by(email=email).first()
        
        if user_by_username:
            flash('用戶名已被使用', 'danger')
            return render_template('register.html')
        
        if user_by_email:
            flash('電子郵件已被註冊', 'danger')
            return render_template('register.html')
        
        # 創建新用戶
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('註冊成功，請登入', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'註冊失敗：{str(e)}', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        if not username or not password:
            flash('請輸入用戶名和密碼', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('用戶名或密碼不正確', 'danger')
            return render_template('login.html')
        
        # 登入用戶
        login_user(user, remember=remember)
        
        # 更新最後登入時間
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 取得原來想要訪問的頁面，若沒有則返回首頁
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('index')
            
        flash('登入成功', 'success')
        return redirect(next_page)
    
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出', 'info')
    return redirect(url_for('index')) 