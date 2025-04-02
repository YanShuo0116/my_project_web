from flask import Flask, request, render_template, send_file, jsonify, flash, redirect, url_for
import traceback
import time
import google.generativeai as genai
from gtts import gTTS
import os
import threading
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_required
from models import db, User
from auth import auth
from admin import admin
import pymysql
from config import config

# 小小設定一下
lock = threading.Lock()
Us_uk = "us"

# 配置API
api_key = os.environ.get('GOOGLE_API_KEY', '')  # 從環境變量獲取API金鑰
if not api_key:
    print("警告: 未設置 GOOGLE_API_KEY 環境變量")
genai.configure(api_key=api_key)

# 選擇模型
model = genai.GenerativeModel('gemini-1.5-flash')

# 建立 Flask 
def create_app(config_name='default'):
    app = Flask(__name__)
    CORS(app)
    
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
    
    # 確保資料庫表格存在
    with app.app_context():
        # db.drop_all()  # 刪除所有表格 (已註釋掉以保留數據)
        db.create_all()
        
        # 創建默認管理員帳號（如果不存在）
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com', is_admin=True)
            admin_user.set_password('admin123')  # 請在正式環境中使用更安全的密碼
            db.session.add(admin_user)
            db.session.commit()
            print('已創建默認管理員帳號')
    
    # 定義路由
    @app.route('/', methods=["GET", "POST"])
    def index():
        return render_template('index.html')
    
    @app.route('/new_we', methods=["GET", "POST"])
    def we():
        return render_template('new_we.html')
    
    @app.route("/update-accent", methods=["GET"])
    def update_accent():
        global Us_uk
        accent = request.args.get('accent')
        if accent in ['us', 'co.uk']:
            Us_uk = accent  # 更新口音
            return jsonify({"status": "success", "accent": Us_uk}), 200
        return jsonify({"status": "error", "message": "Invalid accent"}), 400
    
    @app.route("/translator", methods=["GET", "POST"])
    def translator():
        translation, explanation, examples = None, None, None
        if request.method == "POST":
            word = request.form.get("word", "").strip()
            if word:
                with lock:
                    time.sleep(0.5)  
                    translation, explanation, examples = translate_word(word)
    
                    generate_audio_file(word, "word.mp3")
                    
                    example_lines = examples.split("\n")
                    generate_audio_file(example_lines[0], "example1.mp3")
                    generate_audio_file(example_lines[3], "example2.mp3")
        
        return render_template('translator.html', translation=translation, explanation=explanation, examples=examples)
    
    # 播放
    @app.route("/play-audio", methods=["GET"])
    def play_audio():
        type_ = request.args.get("type")
        file_map = {
            "word": "audio_files/word.mp3",
            "example1": "audio_files/example1.mp3",
            "example2": "audio_files/example2.mp3",
        }
        filepath = file_map.get(type_)
        if filepath and os.path.exists(filepath):
            return send_file(filepath)
        return "音檔不存在", 404
    
    @app.route("/ai-teacher", methods=["GET", "POST"])
    def ai_teacher():
        teacher_answer = None
        if request.method == "POST":
            prompt_Q = request.form.get("prompt_Q", "").strip()
            if prompt_Q:
                teacher_answer = anser_Q(prompt_Q)
        return render_template('teach.html', teacher_answer=teacher_answer)
    
    # 確保音檔目錄存在
    os.makedirs('audio_files', exist_ok=True)
    
    return app

# 定義主要的工具函數
def translate_word(word):
    try:
        # 1. 翻譯
        translation_prompt = f"""請按照以下格式提供單字 '{word}' 的翻譯和同義詞以下為你輸出範例,無需輸出＊符號：
＊翻譯：
[中文翻譯]

＊詳細解釋：
[單字的詳細解釋，包括詞性和不同的意思]

＊例句：
1. [包含該單字的英文例句1]
[例句1的中文翻譯]

2. [包含該單字的英文例句2]
[例句2的中文翻譯]
"""
        translation_response = model.generate_content(translation_prompt)
        
        # 從回應中提取所需資訊
        full_response = translation_response.text
        
        # 分割回應以獲取翻譯、解釋和例句
        sections = full_response.split("\n\n")
        
        translation = sections[0].replace("翻譯：", "").strip() if len(sections) > 0 else "無法獲取翻譯"
        explanation = sections[1].replace("詳細解釋：", "").strip() if len(sections) > 1 else "無法獲取解釋"
        examples = "\n".join(sections[2:]).replace("例句：", "").strip() if len(sections) > 2 else "無法獲取例句"
        
        return translation, explanation, examples
    except Exception as e:
        print(f"翻譯過程中發生錯誤: {str(e)}")
        traceback.print_exc()
        return "處理請求時發生錯誤", "請稍後再試", "無法生成例句"

def generate_audio_file(text, filename):
    try:
        tts = gTTS(text=text, lang='en', tld=Us_uk)
        audio_path = os.path.join('audio_files', filename)
        tts.save(audio_path)
        return True
    except Exception as e:
        print(f"生成音頻時發生錯誤: {str(e)}")
        return False

def anser_Q(prompt_Q):
    try:
        teacher_prompt = f"""你是一位專業的英語教師，請針對以下問題提供詳細的解答，並使用繁體中文回覆：

問題: {prompt_Q}

請提供專業且詳盡的回答，如果有需要可以提供例子來幫助理解。你可以使用markdown格式讓回答更易讀。
"""
        
        response = model.generate_content(teacher_prompt)
        return response.text
    except Exception as e:
        print(f"AI老師回答問題時發生錯誤: {str(e)}")
        traceback.print_exc()
        return "處理請求時發生錯誤，請稍後再試。"

# 作文功能全局數據存儲
composition_data = {} 
