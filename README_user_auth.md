# Flask MySQL 用戶認證系統

本專案實現了一個基於 Flask 和 MySQL 的用戶認證系統，可以處理用戶註冊、登入和退出功能。

## 功能特點

- 用戶註冊（支持用戶名和電子郵件驗證）
- 安全密碼儲存（使用哈希加密）
- 用戶登入與退出
- 記住我功能
- 基於 Flask-Login 的會話管理
- MySQL 資料庫整合

## 安裝與配置

### 前置條件

- Python 3.6+
- MySQL 8.0+
- pip（Python 包管理器）

### 安裝步驟

1. 安裝所需的 Python 套件：

```bash
pip install flask flask-sqlalchemy flask-login pymysql cryptography
```

2. 安裝並配置 MySQL 資料庫：

```bash
# 使用 Homebrew 安裝 MySQL (macOS)
brew install mysql

# 啟動 MySQL 服務
brew services start mysql

# 創建資料庫
mysql -u root -e "CREATE DATABASE IF NOT EXISTS flask_auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

3. 配置資料庫連接：

編輯 `config.py` 文件中的資料庫連接信息：

```python
# 開發環境資料庫連接
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/flask_auth_db'
```

如果 MySQL 設置了密碼，請相應更新連接字串：

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:your_password@localhost/flask_auth_db'
```

## 運行應用

```bash
python app.py
```

應用將在 `http://127.0.0.1:5000` 啟動，同時會提供一個 ngrok 隧道，以便可以從外部訪問（如果 ngrok 配置正確）。

## 使用方法

1. 訪問 `/auth/register` 註冊新用戶
2. 訪問 `/auth/login` 登入已有帳號
3. 訪問 `/auth/logout` 登出當前帳號

## 檔案結構

- `app.py` - 主應用入口點
- `models.py` - 定義資料庫模型
- `auth.py` - 認證相關路由
- `config.py` - 應用配置
- `templates/` - HTML 模板
  - `login.html` - 登入頁面
  - `register.html` - 註冊頁面

## 安全性考慮

- 密碼使用 Werkzeug 提供的 `generate_password_hash` 函數進行哈希加密
- 使用 CSRF 保護來防止跨站請求偽造攻擊
- 用戶會話使用安全 cookie 存儲

## 問題排除

### 資料庫連接問題

如果遇到資料庫連接問題，請檢查：

1. MySQL 服務是否正在運行
2. 資料庫用戶名和密碼是否正確
3. 資料庫 `flask_auth_db` 是否存在

### 用戶註冊問題

如果用戶無法註冊：

1. 檢查是否存在同名用戶或相同電子郵件
2. 確認所有必填欄位都已填寫
3. 檢查密碼是否符合要求

## 部署到生產環境

對於生產環境，請確保：

1. 更改 `SECRET_KEY` 為安全的隨機字串
2. 使用環境變數設置敏感配置（例如資料庫密碼）
3. 將 `DEBUG` 設為 `False`
4. 考慮使用 Gunicorn 或 uWSGI 代替開發伺服器
5. 設置 HTTPS 以加密通信 