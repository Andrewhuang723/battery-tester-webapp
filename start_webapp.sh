#!/bin/bash

echo "🚀 電池測試器 Web App 部署腳本"
echo "================================"
echo ""

# 檢查Python環境
echo "🐍 檢查Python環境..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "❌ 錯誤: 找不到Python。請先安裝Python 3.7+"
    exit 1
fi

echo "✅ 找到Python: $PYTHON_CMD"

# 檢查並安裝依賴
echo ""
echo "📦 檢查並安裝依賴套件..."
$PYTHON_CMD -c "import flask, pandas, werkzeug" 2>/dev/null || {
    echo "安裝缺失的套件..."
    $PYTHON_CMD -m pip install flask pandas werkzeug
}

echo "✅ 所有依賴套件已就緒"

# 創建必要的資料夾
echo ""
echo "📁 創建資料夾結構..."
mkdir -p uploads processed

# 檢查端口可用性
echo ""
echo "🌐 檢查端口可用性..."
PORT=5001
while lsof -i :$PORT >/dev/null 2>&1; do
    echo "端口 $PORT 已被占用，嘗試下一個端口..."
    PORT=$((PORT + 1))
done

echo "✅ 將使用端口: $PORT"

# 更新端口設定
sed -i.bak "s/port=[0-9]\+/port=$PORT/" app.py

# 獲取本機IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

echo ""
echo "🎉 準備啟動Web應用程式!"
echo ""
echo "📍 訪問地址:"
echo "   本機: http://localhost:$PORT"
if [ ! -z "$LOCAL_IP" ]; then
    echo "   網路: http://$LOCAL_IP:$PORT"
fi
echo ""
echo "🎯 使用說明:"
echo "1. 在瀏覽器中開啟上述地址"
echo "2. 拖拉或選擇CSV檔案"
echo "3. 點擊'開始處理'按鈕"
echo "4. 下載處理後的檔案"
echo ""
echo "⚠️  注意: 按 Ctrl+C 可停止服務器"
echo ""

# 啟動應用程式
echo "🚀 啟動中..."
$PYTHON_CMD app.py