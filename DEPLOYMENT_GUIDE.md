# 電池測試器 Web App 部署指南

本指南將幫助您將電池測試器 Web App 部署到公開網站。

## 🚀 推薦的免費部署平台

### 1. Render.com（推薦）
- **優點**：完全免費，支持自動部署，SSL證書
- **部署步驟**：

1. 前往 [Render.com](https://render.com) 並註冊帳號
2. 點擊 "New Web Service"
3. 連接您的 GitHub 儲存庫或上傳檔案
4. 配置如下：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app_production.py`
   - **Environment**: Python 3
5. 點擊 "Create Web Service"

### 2. Railway.app
1. 前往 [Railway.app](https://railway.app) 並註冊
2. 點擊 "Deploy from GitHub repo"
3. 選擇您的儲存庫
4. Railway 會自動檢測並部署

### 3. Vercel（適合靜態站點）
1. 前往 [Vercel.com](https://vercel.com) 並註冊
2. 導入您的 GitHub 儲存庫
3. Vercel 會自動部署

## 📁 部署文件說明

- `app_production.py`: 生產環境的主應用程式文件
- `requirements.txt`: Python 依賴包列表
- `Procfile`: Render/Heroku 部署配置
- `railway.json`: Railway 部署配置
- `vercel.json`: Vercel 部署配置
- `Dockerfile`: Docker 容器配置（可選）

## 🔧 環境變量設置

在部署平台中設置以下環境變量：

- `SECRET_KEY`: 設置一個隨機的密鑰字符串
- `PORT`: 通常由平台自動設置，默認 5000

## 📋 部署檢查清單

- [ ] 所有文件已上傳到 Git 儲存庫
- [ ] requirements.txt 包含所有必要依賴
- [ ] app_production.py 已準備好生產環境配置
- [ ] 環境變量已正確設置
- [ ] SSL 證書已啟用（大多數平台自動提供）

## 🌐 部署後測試

部署完成後，訪問您的網站並測試：

1. 上傳測試 CSV 文件
2. 檢查處理功能是否正常
3. 測試下載功能
4. 驗證所有頁面都能正常加載

## 🛠️ 本地測試生產環境版本

在部署前，您可以在本地測試生產環境版本：

```bash
pip install -r requirements.txt
python app_production.py
```

然後訪問 http://localhost:5000

## 📞 支援

如果遇到部署問題，請檢查：

1. 平台的部署日誌
2. 確保所有文件路徑正確
3. 檢查依賴包版本兼容性
4. 確認環境變量設置正確

## 🔒 安全注意事項

- 不要在代碼中硬編碼敏感信息
- 使用環境變量存儲密鑰
- 定期更新依賴包
- 啟用 HTTPS（大多數平台自動提供）