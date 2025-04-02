# HTML試用初始版本 更新日期2024/12/11(陳衍碩)
# 畢業專題 - 專案最新說明 更新日期2025/04/02

## 網站連結
已成功部署到 Render.com！
📌 **[英文學習助手官方網站](https://english-assistant-g7im.onrender.com/)**

## 安裝包(大致上是這幾個)

```bash
pip3 install flask==3.0.0
pip3 install flask-login==0.6.3
pip3 install flask-sqlalchemy==3.1.1
pip3 install flask-cors==5.0.1
pip3 install google-generativeai==0.8.4
pip3 install pyngrok==7.2.3
pip3 install gtts==2.5.4
pip3 install pymysql==1.1.1
pip3 install gunicorn==21.2.0
pip3 install click==8.1.8
```

## API 調用

1. 去註冊以下API：

   - gemini api
     https://aistudio.google.com/welcome

   - 得到API後，**不要**直接放入程式碼，改用環境變數

2. API金鑰安全設定方法：
   - 在本地開發：建立`.env`檔案
   ```
   GOOGLE_API_KEY=你的金鑰
   ```
   - 在Render部署：使用環境變數設定

## 執行cmd 

本地運行：
```bash
python wsgi.py
```

## 啟動成功後會顯示

```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

## 資料夾結構與功能說明

```
MY_PROJECT/
│
├── render_app.py         # 主要程式 (Render專用版本)
├── app.py                # 原始主程式
├── wsgi.py               # 啟動入口
├── models.py             # 資料模型 (使用者、資料庫)
├── auth.py               # 使用者認證 (登入、註冊功能)
├── admin.py              # 管理後台功能
├── config.py             # 系統設定檔
├── requirements.txt      # 依賴套件清單
├── Procfile              # Render部署用
├── render.yaml           # Render設定檔
├── README.md             # 本說明文件
├── audio_files/          # 存放音檔目錄 (自動生成)
│
├── static/               # 靜態文件（CSS、JS、圖像等）
│   ├── css/
│   │   ├── styles.css    
│   │   ├── teach.css    
│   │   ├── button.css    # 特殊效果按鈕
│   │   ├── composition.css 
│   │   ├── translator.css
│   │   └── we.css
│   │
│   ├── js/
│   │   ├── scripts.js    
│   │   ├── teach.js  
│   │   ├── composition.js     
│   │   ├── translator.js
│   │   └── we.js
│   └── images/           # 圖片資源
│
└── templates/            # HTML 模板
    ├── index.html        # 主頁
    ├── teach.html        # AI老師頁面
    ├── composition.html  # 英文作文助手
    ├── translator.html   # 翻譯機
    ├── new_we.html       # 關於我們頁面
    └── admin/            # 管理後台模板目錄
        ├── layout.html   # 後台布局
        ├── index.html    # 後台首頁
        ├── users.html    # 用戶管理頁面
        └── ...           # 其他後台頁面
```

## 管理員帳號
- 使用者名稱：`admin`
- 密碼：`admin123`
- **注意：部署後請立即更改默認密碼！**

## GitHub 更新須知

### 必須避免的錯誤！！！

- ❌ **絕對不要**將`.env`檔案上傳到GitHub


### 正確更新步驟
1. 先同步最新版本：`git pull`
2. 修改你的檔案
3. 安全檢查：確保沒有敏感資訊
4. 提交：
   ```bash
   git add .
   git commit -m "你做的修改說明"
   git push
   ```


## 使用說明
網站已部署，請前往 [https://english-assistant-g7im.onrender.com/](https://english-assistant-g7im.onrender.com/) 體驗所有功能。

       _                        
       \`*-.                    
        )  _`-.                 
       .  : `. .                
       : _   '  \               
       ; *` _.   `*-._          
       `-.-'          `-.       
         ;       `       `.     
         :.       .        \    
         . \  .   :   .-'   .   
         '  `+.;  ;  '      :   
         :  '  |    ;       ;-. 
         ; '   : :`-:     _.`* ;
[success!] .*' /  .*' ; .*`- +'  `*' 
      `*-*   `*-*  `*-*'
