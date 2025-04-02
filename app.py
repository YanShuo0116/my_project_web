#語音小BUG 再次生成不會覆蓋
from flask import Flask, request, render_template, send_file, jsonify, flash, redirect, url_for
from pyngrok import ngrok
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

#小小設定一下
lock = threading.Lock()
Us_uk="us"

# 配置API                                                                            #README.MD裡有網址
ngrok.set_auth_token("2pTLpO34I2oLaQ7JQZzXdItaVjg_6dHVsJfvwJsW8CMKJWGmc")     # 替換為你的 ngrok 金鑰!!!!!!!!!!!!
api_key = os.environ.get('GOOGLE_API_KEY')
if not api_key:
    print("警告: 未設置 GOOGLE_API_KEY 環境變量")
genai.configure(api_key=api_key)

#選擇模型
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
    
    @app.route("/composition", methods=["GET", "POST"])
    def composition():
        global composition_data
        step = request.args.get("step", "1")
        essay_topic = None
        paragraph_theme = None
        key_points = None
        topic_sentence = None
        essay = None
        evaluation = None
        refined_essay = None
        if request.method == "POST":
            data = request.form.to_dict()
            print(f"接收到的表單數據: {data}")
            if step == '1':
                topic = data.get('topic')
                essay_topic = data.get('essay_topic')
                if not essay_topic:
                   essay_topic= generate_essay_topic(topic)
                save_composition_data(step, {"topic":topic,"essay_topic": essay_topic})
                
                
                return render_template('composition.html', step=step, essay_topic=essay_topic)
            elif step == '2':
                topic = composition_data.get('1').get('topic')
                essay_topic = composition_data.get('1').get('essay_topic')
                keywords = data.get('keywords')
                paragraph_theme= generate_paragraph_theme(topic, essay_topic,keywords)
                save_composition_data(step, {"paragraph_theme": paragraph_theme, "keywords": keywords})
               
                return render_template('composition.html', step=step, paragraph_theme=paragraph_theme, keywords=keywords)
            elif step == '3':
                 topic = composition_data.get('1').get('topic')
                 essay_topic = composition_data.get('1').get('essay_topic')
                 paragraph_theme = composition_data.get('2').get('paragraph_theme')
                 key_points = generate_key_points(topic, essay_topic, paragraph_theme)
                 save_composition_data(step, {"key_points": key_points})
               
                 return render_template('composition.html', step=step, key_points=key_points, paragraph_theme=paragraph_theme)
            elif step == '4':
                topic = composition_data.get('1').get('topic')
                essay_topic = composition_data.get('1').get('essay_topic')
                paragraph_theme = composition_data.get('2').get('paragraph_theme')
                keywords = composition_data.get('2').get('keywords')
                key_points = composition_data.get('3').get('key_points')
                topic_sentence = generate_topic_sentence(topic, essay_topic, paragraph_theme, keywords)
                save_composition_data(step,{"topic_sentence":topic_sentence})
                return render_template('composition.html', step=step, topic_sentence=topic_sentence, key_points=key_points, paragraph_theme = paragraph_theme)
            elif step == '5':
                essay = compose_essay()
                evaluation = generate_essay_evaluation(essay)
                refined_essay= generate_refined_essay(essay)
                return render_template('composition.html', step=step, essay=essay, evaluation=evaluation, refined_essay = refined_essay)
        
        return render_template('composition.html', step=step, essay_topic=essay_topic, paragraph_theme=paragraph_theme, key_points=key_points, topic_sentence=topic_sentence, essay = essay, evaluation=evaluation, refined_essay = refined_essay)
    
    # 確保音檔目錄存在
    os.makedirs('audio_files', exist_ok=True)
    
    return app

# 定義主要的工具函數
def translate_word(word):
    try:
        # 1. 翻譯
        translation_prompt = f"""請按照以下格式提供單字 '{word}' 的翻譯和同義詞以下為你輸出範例,無需輸出＊符號：
Limit

1. 限制 (n./v.)  The maximum amount allowed.  (限制的數量或程度)

2. 邊界 (n.)  The furthest extent or point. (邊緣，界限)

3. 極限 (n.) The point beyond which something cannot continue or operate. (無法超越的點)

同義詞: Restriction, Constraint, Boundary"""
        translation_response = model.generate_content(translation_prompt).text

        # 2. 相關詞語
        explanation_prompt = f"請列出與單字 '{word}' 相關的詞語，包含變形或派生詞(2~5個)，格式如下：\nUnnerve\n- Unnerving\n- Unnervingly"
        explanation_response = model.generate_content(explanation_prompt).text

        # 3. 例句
        example_prompt = f"""請提供 2 個使用單字 '{word}' 的簡短例句，並附上<繁體中文>翻譯,以下為你輸出範例(例句1翻譯和例句2中間空一行 總共只能有五行),無需輸出＊符號。
The speed limit on this road is 50 km/h.
翻譯: 這條道路的限速是每小時50公里。

We need to limit the number of participants in the event.
翻譯: 我們需要限制活動的參加人數。
"""
        example_response = model.generate_content(example_prompt).text

        return translation_response, explanation_response, example_response
    except Exception as e:
        print(f"Error processing word '{word}': {traceback.format_exc()}")
        return "翻譯失敗", "相關詞語生成失敗", "例句生成失敗"

def generate_audio_file(content, filename):
    if not content.strip():  # 檢查文本空白
        print(f"警告：文本為空，無法生成音頻：{filename}")
        return
    tts = gTTS(text=content, lang='en' , tld=Us_uk )
    filepath = os.path.join('audio_files', filename)
    tts.save(filepath)
    return filepath

def anser_Q(prompt_Q):
    try:
        # 生成回答
        answerQ_prompt = f"""你是專業英文老師，請使用反體中文夾雜英文簡短回答 '{prompt_Q}' 的這個問題 (你不能輸出＊字符號)。如果問題與英文不相關則輸出「請提出英文相關問題」。
        以下為範例:
        輸入:
        有用到Arriving的片語嗎？
        你輸出:
        Q:有用到Arriving的片語嗎？
        A:Arriving at是一個常見的片語，通常用來表示到達某個地點或目的地。例如："I'm arriving at the airport at 3 PM."
        """
        answerQ_response = model.generate_content(answerQ_prompt).text
        return answerQ_response
    except Exception as e:
        print(f"Error processing question '{prompt_Q}': {traceback.format_exc()}")
        return "抱歉，回答失敗，請稍後再試"

# 下面是原始檔案中的其他工具函數，根據需要添加
# def generate_essay_topic(topic): ...
# def generate_paragraph_theme(topic, essay_topic, keywords): ...
# 等等

app = create_app()

# ngrok配置
def start_ngrok():
    try:
        public_url = ngrok.connect(5000).public_url
        print(f" * ngrok tunnel '{public_url}' -> 'http://127.0.0.1:5000/'")
    except Exception as e:
        print(f" * 無法啟動ngrok: {str(e)}")
        print(" * 應用將僅在本地運行")

# 啟動應用
if __name__ == "__main__":
    try:
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            start_ngrok()
    except Exception as e:
        print(f" * 無法啟動ngrok: {str(e)}")
    app.run()
