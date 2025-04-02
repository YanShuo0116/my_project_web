from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager
from models import db, User
from admin import admin
from auth import auth
from config import config

def create_admin_app(config_name='default'):
    app = Flask(__name__)
    
    # 從配置對象中加載配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化資料庫
    db.init_app(app)
    
    # 初始化登入管理器
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '請先登入才能訪問此頁面'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 註冊認證藍圖
    app.register_blueprint(auth, url_prefix='/auth')
    
    # 註冊管理員藍圖
    app.register_blueprint(admin, url_prefix='/admin')
    
    # 錯誤處理
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    # 根路徑直接導向管理後台首頁
    @app.route('/')
    def index():
        return redirect(url_for('admin.index'))
    
    return app

if __name__ == "__main__":
    app = create_admin_app()
    
    # 確保數據庫表格和管理員帳號存在
    with app.app_context():
        # 創建表格(如果不存在)
        db.create_all()
        
        # 確保默認管理員帳號存在
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com', is_admin=True)
            admin_user.set_password('admin123')  # 請在正式環境中使用更安全的密碼
            db.session.add(admin_user)
            db.session.commit()
            print('已創建默認管理員帳號')
        else:
            print('管理員帳號已存在')
    
    print("管理員後台啟動中...")
    print("訪問 http://127.0.0.1:5500/ 直接進入管理後台")
    # 在開發模式下啟動時保存會話
    app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 30  # 30天
    app.run(port=5500, debug=True) 