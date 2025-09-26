# 🔋 電池測試器 Web App# Battery Tester App



一個專為承德充放電機CSV資料處理設計的Web應用程式。電池測試數據處理應用程式 - 圖形化介面版本



## ✨ 功能特色## 📱 應用程式



- 🌐 **跨平台**: 在任何有瀏覽器的設備上使用### 🎯 主要應用

- ⚡ **快速處理**: 自動轉換時間格式，快速處理大量資料- **`BatteryTester.app`** - 可執行的 macOS 應用程式

- 📊 **雙重輸出**: 自動產生詳細資料和步驟資料兩個檔案

- 🔒 **安全可靠**: 資料在本地處理，保護隱私### 📄 支援檔案

- 📦 **批量處理**: 支援多檔案同時上傳處理- `run_gui.py` - GUI 版本的主程式

- `utils.py` - 工具函數庫

## 🚀 在線使用- `create_gui_app.sh` - 重新建構應用程式的腳本



**[點擊這裡訪問線上版本](您的部署網址)**## 🚀 使用方法



## 📁 支援的檔案格式### 快速開始

1. **雙擊** `BatteryTester.app` 啟動應用程式

- CSV 檔案 (.csv)2. 在歡迎對話框中點擊 **OK**

- Excel 檔案 (.xls, .xlsx)3. **選擇輸入檔案** - 選擇您的電池測試數據檔案

4. **選擇保存位置** - 選擇輸出檔案夾

## 🛠️ 本地運行5. **完成** - 應用程式會顯示處理結果



```bash### 處理結果

# 安裝依賴應用程式會產生兩個 CSV 檔案：

pip install -r requirements.txt- `*_detail.csv` - 完整的詳細數據

- `*_step.csv` - 測試步驟摘要數據

# 運行應用程式

python app_production.py## 🔧 重新建構應用程式

```

如果需要修改應用程式或重新建構：

然後訪問 http://localhost:5000```bash

./create_gui_app.sh

## 📋 使用說明```



1. **上傳檔案**: 點擊選擇檔案或直接拖拽檔案到上傳區域## 💡 功能特色

2. **開始處理**: 點擊"開始處理"按鈕

3. **下載結果**: 處理完成後可下載詳細資料和步驟資料- ✅ **純圖形介面** - 使用對話框，無需終端

4. **批量下載**: 多個檔案可一次性打包下載- ✅ **用戶友好** - 每步都有清楚的指示

- ✅ **錯誤處理** - 詳細的錯誤訊息

## 🔧 技術架構- ✅ **支援多種格式** - CSV、Excel 等檔案格式

- ✅ **自動數據處理** - 時間格式轉換、數據類型最佳化

- **後端**: Flask + Python

- **前端**: HTML5 + CSS3 + JavaScript## 🛠️ 系統需求

- **資料處理**: Pandas + NumPy

- **部署**: 支援 Render, Railway, Vercel 等平台- macOS 10.13 或更高版本

- Python 3 (系統內建或自行安裝)

## 📄 授權- pandas 套件



MIT License - 詳見 LICENSE 檔案## ❗ 故障排除



## 🤝 貢獻如果應用程式無法運行：

1. 確保已安裝 Python 3：`python3 --version`

歡迎提交 Issues 和 Pull Requests！2. 安裝 pandas：`pip3 install pandas`

3. 檢查檔案權限：`chmod +x BatteryTester.app/Contents/MacOS/BatteryTester`

---4. 在終端測試：`python3 run_gui.py`



**開發者**: [您的名字]  如有問題，請檢查系統 Python 環境設定。
**聯絡方式**: [您的聯絡方式]  
**最後更新**: 2024年9月