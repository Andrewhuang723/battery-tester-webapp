#!/bin/bash

echo "🔋 手動推送到 GitHub"
echo "==================="

# 請替換下面的 URL 為您實際的 GitHub 儲存庫 URL
echo "📝 請將下面的 YOUR_GITHUB_URL 替換為您的實際儲存庫 URL"
echo "例如: https://github.com/Andrewhuang723/battery-tester-webapp.git"
echo ""

read -p "請貼上您的 GitHub 儲存庫 URL: " GITHUB_URL

if [ -z "$GITHUB_URL" ]; then
    echo "❌ 沒有提供 URL，請重新執行"
    exit 1
fi

echo "🔗 設定 remote URL: $GITHUB_URL"

# 移除舊的 remote（如果存在）
git remote remove origin 2>/dev/null || true

# 添加新的 remote
git remote add origin "$GITHUB_URL"

# 確保在 main 分支
git branch -M main

echo "🚀 正在推送到 GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 成功推送到 GitHub！"
    echo "📍 儲存庫網址: ${GITHUB_URL%.git}"
    echo ""
    echo "🚀 接下來可以部署到:"
    echo "   • Render.com: https://render.com"
    echo "   • Railway.app: https://railway.app"
    echo "   • Vercel.com: https://vercel.com"
else
    echo ""
    echo "❌ 推送失敗，可能的原因："
    echo "   1. 需要 GitHub 登入驗證"
    echo "   2. 儲存庫 URL 不正確"
    echo "   3. 需要設定 Personal Access Token"
    echo ""
    echo "💡 嘗試解決方案："
    echo "   1. 確認儲存庫已在 GitHub 上創建"
    echo "   2. 檢查 URL 是否正確"
    echo "   3. 如果需要驗證，請參考 GITHUB_UPLOAD_GUIDE.md"
fi