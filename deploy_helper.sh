#!/bin/bash

echo "🚀 電池測試器 Web App - 部署助手"
echo "=================================="
echo ""
echo "✅ GitHub 儲存庫已準備完成！"
echo "📍 儲存庫地址: https://github.com/Andrewhuang723/battery-tester-webapp"
echo ""

echo "🌐 選擇部署平台："
echo "1. Render.com (推薦 - 完全免費，SSL，自定義域名)"
echo "2. Railway.app (簡單快速)"
echo "3. Vercel.com (適合靜態和API)"
echo "4. 查看所有選項的詳細說明"
echo "5. 稍後再部署"
echo ""

read -p "請選擇 (1-5): " PLATFORM

case $PLATFORM in
    1)
        echo ""
        echo "🎯 Render.com 部署步驟："
        echo "======================="
        echo "1. 前往 https://render.com"
        echo "2. 使用 GitHub 帳號註冊/登入"
        echo "3. 點擊 'New Web Service'"
        echo "4. 選擇 'Build and deploy from a Git repository'"
        echo "5. 連接 GitHub 並選擇 'battery-tester-webapp' 儲存庫"
        echo "6. 配置設定："
        echo "   - Name: battery-tester-webapp"
        echo "   - Environment: Python 3"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: python app_production.py"
        echo "7. 點擊 'Create Web Service'"
        echo ""
        echo "🔗 立即前往 Render:"
        echo "https://render.com/new-service"
        ;;
    2)
        echo ""
        echo "🚅 Railway.app 部署步驟："
        echo "========================"
        echo "1. 前往 https://railway.app"
        echo "2. 點擊 'Start a New Project'"
        echo "3. 選擇 'Deploy from GitHub repo'"
        echo "4. 選擇 'battery-tester-webapp' 儲存庫"
        echo "5. Railway 會自動檢測並部署！"
        echo ""
        echo "🔗 立即前往 Railway:"
        echo "https://railway.app/new"
        ;;
    3)
        echo ""
        echo "⚡ Vercel.com 部署步驟："
        echo "======================"
        echo "1. 前往 https://vercel.com"
        echo "2. 使用 GitHub 帳號註冊/登入"
        echo "3. 點擊 'New Project'"
        echo "4. 導入 'battery-tester-webapp' 儲存庫"
        echo "5. Vercel 會自動配置並部署"
        echo ""
        echo "🔗 立即前往 Vercel:"
        echo "https://vercel.com/new"
        ;;
    4)
        echo ""
        echo "📖 詳細部署說明文檔："
        echo "===================="
        echo "查看專案中的 DEPLOYMENT_GUIDE.md 檔案"
        echo "包含所有平台的詳細說明和故障排除"
        echo ""
        if command -v open >/dev/null 2>&1; then
            echo "正在開啟部署指南..."
            open DEPLOYMENT_GUIDE.md
        fi
        ;;
    5)
        echo ""
        echo "📋 稍後部署時，您可以："
        echo "1. 重新執行此腳本"
        echo "2. 查看 DEPLOYMENT_GUIDE.md"
        echo "3. 訪問任何上述平台並連接您的 GitHub 儲存庫"
        ;;
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

echo ""
echo "🎉 恭喜！您的電池測試器 Web App 已準備就緒："
echo ""
echo "📁 GitHub 儲存庫: https://github.com/Andrewhuang723/battery-tester-webapp"
echo "🔋 功能特色:"
echo "   • 跨平台 Web 界面"
echo "   • 支援 CSV/XLS/XLSX 檔案"
echo "   • 自動產生詳細和步驟資料"
echo "   • 批量處理和下載"
echo "   • 生產環境就緒"
echo ""
echo "🚀 部署後，您將擁有一個可公開訪問的網站："
echo "   例如: https://battery-tester-webapp.onrender.com"
echo ""
echo "💡 提示: 部署通常需要 3-5 分鐘完成"