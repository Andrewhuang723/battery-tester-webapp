# 📤 GitHub 上傳步驟指南

## 🚀 快速上傳到 GitHub

### 方法 1: 使用助手腳本（推薦）

```bash
cd /Users/andrewhuang/Desktop/Battery/Tester_MacOS
./upload_to_github.sh
```

### 方法 2: 手動步驟

#### 步驟 1: 在 GitHub 上創建儲存庫

1. 前往 [GitHub.com](https://github.com)
2. 點擊右上角的 "+" → "New repository"
3. 填寫儲存庫資訊：
   - **Repository name**: `battery-tester-webapp`
   - **Description**: `電池測試器 Web App - 承德充放電機 CSV 資料處理工具`
   - **Visibility**: Public 或 Private（根據需要選擇）
   - **不要勾選** "Add a README file"
4. 點擊 "Create repository"

#### 步驟 2: 連接本地儲存庫到 GitHub

```bash
# 進入專案目錄
cd /Users/andrewhuang/Desktop/Battery/Tester_MacOS

# 添加 remote（替換 YOUR_USERNAME 和 YOUR_REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/battery-tester-webapp.git

# 確保在 main 分支
git branch -M main

# 推送到 GitHub
git push -u origin main
```

#### 步驟 3: 驗證上傳

訪問您的 GitHub 儲存庫頁面，確認所有檔案都已上傳：

- ✅ app_production.py
- ✅ requirements.txt
- ✅ templates/index.html
- ✅ Procfile
- ✅ README.md
- ✅ DEPLOYMENT_GUIDE.md
- ✅ 其他配置檔案

## 🔐 如果遇到驗證問題

如果推送時要求登入，您可能需要：

1. **使用 Personal Access Token**：
   - 前往 GitHub → Settings → Developer settings → Personal access tokens
   - 生成新的 token
   - 在命令行中使用 token 作為密碼

2. **或者使用 SSH 金鑰**：
   ```bash
   # 生成 SSH 金鑰（如果還沒有）
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   
   # 添加到 GitHub
   # 複製 ~/.ssh/id_rsa.pub 的內容到 GitHub → Settings → SSH keys
   
   # 使用 SSH URL
   git remote set-url origin git@github.com:YOUR_USERNAME/battery-tester-webapp.git
   ```

## 🎯 上傳完成後

一旦成功推送到 GitHub，您就可以：

1. **部署到免費平台**：
   - [Render.com](https://render.com) （最推薦）
   - [Railway.app](https://railway.app)
   - [Vercel.com](https://vercel.com)

2. **分享您的專案**：
   - 儲存庫 URL：`https://github.com/YOUR_USERNAME/battery-tester-webapp`
   - 部署後的網站 URL：`https://your-app-name.onrender.com`

3. **繼續開發**：
   - 本地修改後使用 `git add .` → `git commit -m "message"` → `git push`

## 📞 需要幫助？

如果遇到任何問題，請參考：
- [GitHub 官方文檔](https://docs.github.com)
- [Git 基礎教程](https://git-scm.com/docs)
- 或直接查看終端錯誤訊息並搜索解決方案