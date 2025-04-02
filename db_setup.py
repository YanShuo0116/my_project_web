from flask import Flask
from models import db, User
from config import config
import click

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    return app

@click.group()
def cli():
    """數據庫管理命令"""
    pass

@cli.command()
@click.option('--drop', is_flag=True, help='刪除並重建所有表格')
def init_db(drop):
    """初始化數據庫架構"""
    app = create_app()
    with app.app_context():
        if drop:
            click.echo('刪除所有資料表...')
            db.drop_all()
            click.echo('資料表已刪除')
        
        click.echo('創建資料表...')
        db.create_all()
        click.echo('資料表已創建')
        
        # 檢查管理員帳號是否存在
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com', is_admin=True)
            admin_user.set_password('admin123')  # 請在正式環境中使用更安全的密碼
            db.session.add(admin_user)
            db.session.commit()
            click.echo('已創建默認管理員帳號')
        else:
            click.echo('管理員帳號已存在')

@cli.command()
def create_admin():
    """創建一個新的管理員帳號"""
    username = click.prompt('請輸入管理員用戶名')
    email = click.prompt('請輸入管理員郵箱')
    password = click.prompt('請輸入密碼', hide_input=True, confirmation_prompt=True)
    
    app = create_app()
    with app.app_context():
        # 檢查用戶名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            click.echo(f'用戶名 {username} 已存在')
            return
        
        user = User(username=username, email=email, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'已創建管理員帳號: {username}')

@cli.command()
def list_users():
    """列出所有用戶"""
    app = create_app()
    with app.app_context():
        users = User.query.all()
        if not users:
            click.echo('沒有找到用戶')
            return
        
        click.echo("用戶列表:")
        for user in users:
            admin_status = "管理員" if user.is_admin else "普通用戶"
            click.echo(f"ID: {user.id}, 用戶名: {user.username}, 郵箱: {user.email}, 角色: {admin_status}")

if __name__ == '__main__':
    cli() 