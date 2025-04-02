document.addEventListener('DOMContentLoaded', function() {
    // 導航欄滾動效果
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });

    // 主題切換功能
    const themeToggle = document.querySelector('#theme-toggle');
    const body = document.body;
    const currentTheme = localStorage.getItem('theme');

    // 檢查本地存儲中的主題設置
    if (currentTheme) {
        body.classList[currentTheme === 'dark' ? 'add' : 'remove']('dark-mode');
        themeToggle.checked = currentTheme === 'dark';
    }

    // 主題切換事件監聽器
    themeToggle.addEventListener('change', function() {
        if (this.checked) {
            body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });

    // 載入動畫
    const loadingScreen = document.querySelector('.loading-screen');
    if (loadingScreen) {
        setTimeout(() => {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500);
        }, 1000);
    }

    // 表單提交處理
    const form = document.querySelector('#teacherForm');
    const loadingSpinner = document.querySelector('.loading-spinner');
    const resultContainer = document.querySelector('.result-container');
    const promptInput = document.querySelector('input[name="prompt_Q"]');

    if (form) {
        form.addEventListener('submit', function(e) {
            // 顯示載入動畫
            loadingSpinner.style.display = 'block';
            
            // 如果已有結果，先隱藏
            if (resultContainer) {
                resultContainer.style.opacity = '0';
            }
        });
    }

    // 改善移動裝置上的輸入體驗
    if (promptInput) {
        // 自動聚焦輸入框（在手機上）
        if (window.innerWidth <= 768) {
            setTimeout(() => {
                promptInput.focus();
            }, 1500);
        }
        
        // 增加焦點時的樣式變化，提升用戶體驗
        promptInput.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
            
            // 在移動設備上，滾動到輸入框位置
            if (window.innerWidth <= 768) {
                setTimeout(() => {
                    this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
        });

        promptInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
        });
        
        // 如果用戶點擊了輸入框，自動顯示鍵盤
        promptInput.addEventListener('touchstart', function() {
            this.focus();
        });
        
        // 自動調整輸入框大小
        promptInput.addEventListener('input', function() {
            // 如果輸入內容較長，增加高度
            if (this.value.length > 30 && window.innerWidth <= 768) {
                this.style.height = 'calc(5rem + 2px)';
            } else {
                this.style.height = '';
            }
        });

        // 處理鍵盤的提交功能 - 允許用戶按Enter直接提交
        promptInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.submit();
            }
        });
    }

    // 如果頁面載入時有結果，顯示結果
    if (resultContainer) {
        resultContainer.style.opacity = '1';
    }

    // 自動調整文本區域高度
    const textarea = document.querySelector('textarea');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
});