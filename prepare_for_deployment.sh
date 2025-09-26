#!/bin/bash

# 電池測試器 Web App GitHub 儲存庫準備腳本

echo "🔋 準備電池測試器 Web App 以供部署..."

# 創建 .gitignore 文件
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Flask
instance/
.webassets-cache

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Uploads and processed files (these will be created at runtime)
uploads/*
processed/*
!uploads/.gitkeep
!processed/.gitkeep

# Logs
*.log
EOL

# 創建必要的空目錄標記文件
mkdir -p uploads processed
touch uploads/.gitkeep
touch processed/.gitkeep

# 初始化 git 儲存庫（如果尚未初始化）
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 儲存庫..."
    git init
fi

# 添加所有文件
echo "📁 添加文件到 Git..."
git add .

# 提交
echo "💾 提交更改..."
git commit -m "Initial commit: Battery Tester Web App ready for deployment

Features:
- Web-based battery data processing
- Support for CSV, XLS, XLSX files
- Automatic generation of detail and step files
- Ready for deployment on Render, Railway, Vercel
- Production-ready with proper logging and error handling"

echo "✅ Git 儲存庫準備完成！"
echo ""
echo "📋 接下來的步驟："
echo "1. 在 GitHub 上創建新的儲存庫"
echo "2. 運行以下命令連接到您的 GitHub 儲存庫："
echo "   git remote add origin https://github.com/您的用戶名/您的儲存庫名.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. 選擇部署平台："
echo "   - Render.com (推薦): https://render.com"
echo "   - Railway.app: https://railway.app" 
echo "   - Vercel.com: https://vercel.com"
echo ""
echo "4. 查看 DEPLOYMENT_GUIDE.md 獲取詳細部署說明"