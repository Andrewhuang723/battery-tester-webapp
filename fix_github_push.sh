#!/bin/bash

echo "🔧 修復 GitHub 推送衝突問題"
echo "============================="
echo ""

# 檢查當前的 remote
echo "📍 當前的 remote 設定："
git remote -v
echo ""

# 獲取遠端的更改
echo "📥 正在獲取遠端儲存庫的更改..."
git fetch origin

echo ""
echo "🔄 有幾種解決方案："
echo "1. 強制推送（會覆蓋遠端的內容）- 適用於空儲存庫或不重要的遠端內容"
echo "2. 合併遠端更改（保留遠端內容並合併）- 較安全的選項"
echo "3. 重置並重新開始"
echo ""

read -p "請選擇解決方案 (1/2/3): " CHOICE

case $CHOICE in
    1)
        echo "⚠️  正在執行強制推送..."
        echo "這將會覆蓋遠端儲存庫的所有內容"
        read -p "確定要繼續嗎？(y/N): " CONFIRM
        if [[ $CONFIRM =~ ^[Yy]$ ]]; then
            git push --force-with-lease origin main
            if [ $? -eq 0 ]; then
                echo "✅ 強制推送成功！"
            else
                echo "❌ 強制推送失敗"
            fi
        else
            echo "❌ 操作已取消"
        fi
        ;;
    2)
        echo "🔄 正在合併遠端更改..."
        
        # 先拉取遠端更改
        git pull origin main --allow-unrelated-histories
        
        if [ $? -eq 0 ]; then
            echo "✅ 成功合併遠端更改"
            echo "🚀 正在推送..."
            git push -u origin main
            if [ $? -eq 0 ]; then
                echo "✅ 推送成功！"
            else
                echo "❌ 推送失敗"
            fi
        else
            echo "❌ 合併失敗，可能需要手動解決衝突"
            echo "請檢查是否有衝突文件需要處理"
        fi
        ;;
    3)
        echo "🔄 重置並重新開始..."
        
        # 刪除遠端設定
        git remote remove origin
        
        echo "📝 請重新輸入您的 GitHub 儲存庫 URL："
        read -p "GitHub URL: " NEW_URL
        
        # 重新添加遠端
        git remote add origin "$NEW_URL"
        
        # 嘗試強制推送
        echo "🚀 重新推送到 GitHub..."
        git push --force-with-lease -u origin main
        
        if [ $? -eq 0 ]; then
            echo "✅ 重新推送成功！"
        else
            echo "❌ 推送仍然失敗"
            echo "建議："
            echo "1. 檢查 GitHub 儲存庫是否存在"
            echo "2. 確認您有推送權限"
            echo "3. 檢查是否需要 Personal Access Token"
        fi
        ;;
    *)
        echo "❌ 無效的選擇"
        exit 1
        ;;
esac

echo ""
echo "📋 推送完成後的下一步："
echo "1. 訪問您的 GitHub 儲存庫確認檔案已上傳"
echo "2. 選擇部署平台（Render.com 推薦）"  
echo "3. 查看 DEPLOYMENT_GUIDE.md 獲取部署說明"