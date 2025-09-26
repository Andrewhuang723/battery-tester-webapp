#!/bin/bash

echo "🔋 電池測試器 Web App - GitHub 上傳助手"
echo "================================================"

# 檢查是否已有 remote
REMOTE_EXISTS=$(git remote | grep origin)

if [ -n "$REMOTE_EXISTS" ]; then
    echo "✅ 已存在 origin remote，正在檢查..."
    git remote -v
else
    echo "📝 請提供您的 GitHub 儲存庫資訊："
    echo ""
    echo "1. 請先在 GitHub 上創建一個新的儲存庫"
    echo "   - 前往 https://github.com/new"
    echo "   - 儲存庫名稱建議: battery-tester-webapp"
    echo "   - 設為 Public 或 Private"
    echo "   - 不要勾選 'Add a README file'"
    echo "   - 點擊 'Create repository'"
    echo ""
    
    read -p "請輸入您的 GitHub 用戶名: " USERNAME
    read -p "請輸入儲存庫名稱 (例如: battery-tester-webapp): " REPO_NAME
    
    # 設定 remote
    GITHUB_URL="https://github.com/$USERNAME/$REPO_NAME.git"
    echo "🔗 設定 remote URL: $GITHUB_URL"
    git remote add origin $GITHUB_URL
fi

echo ""
echo "📤 準備推送到 GitHub..."

# 確保在 main 分支
git branch -M main

# 推送到 GitHub
echo "🚀 正在推送到 GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 成功推送到 GitHub！"
    echo ""
    echo "📍 您的儲存庫網址:"
    echo "   https://github.com/$USERNAME/$REPO_NAME"
    echo ""
    echo "🚀 接下來可以部署到以下平台:"
    echo "   1. Render.com: https://render.com"
    echo "   2. Railway.app: https://railway.app" 
    echo "   3. Vercel.com: https://vercel.com"
    echo ""
    echo "📖 查看 DEPLOYMENT_GUIDE.md 獲取詳細部署說明"
else
    echo "❌ 推送失敗，請檢查："
    echo "   1. GitHub 儲存庫是否已創建"
    echo "   2. 用戶名和儲存庫名稱是否正確"
    echo "   3. 是否需要登入 GitHub (可能需要設定 personal access token)"
    echo ""
    echo "💡 如果需要設定 GitHub 驗證，請參考:"
    echo "   https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
fi