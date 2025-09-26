"""
生產環境版本的電池測試器 Web App
適用於公開部署
"""
from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import os
import tempfile
import zipfile
from werkzeug.utils import secure_filename
import re
from datetime import datetime
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 生產環境配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'battery_tester_production_key_2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 確保資料夾存在
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def convert_to_seconds(row):
    """將時間字串轉換為秒數"""
    try:
        hours, minutes, seconds = map(float, row.split(":"))
        total_seconds = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        return total_seconds
    except Exception as e:
        logger.error(f"Error processing row: {row}, Error: {e}")
        return None

def get_n_cols(fpath: str):
    """取得欄位數量"""
    with open(fpath, 'r') as f:
        for line in f.readlines():
            row = line.strip().rsplit(",")
            if len(row) > 0 and row[0] == "System Time":
                return len(row)
    return 0

def is_match_date_string(ds: str):
    """檢查是否符合日期格式"""
    pattern = r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$"
    return bool(re.match(pattern, ds))

def extract_origin_csv_original(fpath: str):
    """處理承德充放電機CSV檔案格式"""
    rows = []
    last_time_per_step_list = []
    step_name = None
    n_cols = get_n_cols(fpath=fpath)

    try:
        with open(fpath, 'r') as f:
            for line in f.readlines():
                row = line.strip().rsplit(",")
                if len(row) > 0 and row[0] in {"%", "@", "Label", "", "$", "System Time", "Start Time"}:
                    if len(row) == 5 and row[0] == "" and row[1] == "":
                        step_name = row[2]         
                    elif len(row) == 2 and row[0] == '%':
                        last_time_per_step_list.append(len(rows)-1)
                else:
                    if len(row) == n_cols and is_match_date_string(row[0]):
                        row.append(step_name)
                        rows.append(row)

        last_time_per_step_list.append(len(rows) - 1)
    except Exception as e:
        logger.error(f"Error processing file {fpath}: {e}")
        raise Exception("此檔案並非'承德充放電機'檔案格式，請確認選擇檔案。")

    return rows, last_time_per_step_list

def process_battery_data(file_path, output_folder):
    """完整的電池資料處理函數"""
    try:
        logger.info(f"開始處理檔案: {file_path}")
        rows, steps = extract_origin_csv_original(file_path)
        
        # 建立 DataFrame
        df = pd.DataFrame(rows)
        df.columns = ["System Time", "Step Time", "V", "I", "T", "R", "P", "mAh", "Wh", "Total Time", "Step name"]
        df["System Time"] = df["System Time"].apply(lambda s: pd.to_datetime(s, format="%y/%m/%d %H:%M:%S"))
        df[["V", "I", "T", "R", "P", "mAh", "Wh"]] = df[["V", "I", "T", "R", "P", "mAh", "Wh"]].astype(dtype=float)
        
        filename_head = os.path.basename(file_path).split(".")[0]
        
        # 儲存詳細資料檔案
        detail_file_path = os.path.join(output_folder, f"{filename_head}_detail.csv")
        df.to_csv(detail_file_path, index=False)
        
        # 儲存步驟資料檔案
        step_df = df.loc[steps]
        step_file_path = os.path.join(output_folder, f"{filename_head}_step.csv")
        step_df.to_csv(step_file_path, index=False)
        
        logger.info(f"處理完成: {len(df)} 行資料, {len(step_df)} 個步驟")
        
        return True, {
            'detail_file': f"{filename_head}_detail.csv",
            'step_file': f"{filename_head}_step.csv",
            'total_rows': len(df),
            'step_rows': len(step_df)
        }
        
    except Exception as e:
        logger.error(f"處理檔案失敗: {e}")
        return False, str(e)

@app.route('/')
def index():
    """主頁面"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """處理檔案上傳"""
    if 'files[]' not in request.files:
        return jsonify({'success': False, 'message': '沒有選擇檔案'})
    
    files = request.files.getlist('files[]')
    
    if not files or files[0].filename == '':
        return jsonify({'success': False, 'message': '沒有選擇檔案'})
    
    processed_files = []
    errors = []
    
    for file in files:
        if file and (file.filename.endswith('.csv') or file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                success, result = process_battery_data(file_path, PROCESSED_FOLDER)
                
                if success:
                    processed_files.append({
                        'original': filename,
                        'detail_file': result['detail_file'],
                        'step_file': result['step_file'],
                        'message': f"成功處理 {result['total_rows']} 行資料，產生 {result['step_rows']} 個步驟記錄"
                    })
                else:
                    errors.append(f"{filename}: {result}")
                
                # 清理上傳的原始檔案
                os.remove(file_path)
                
            except Exception as e:
                logger.error(f"處理檔案 {file.filename} 時發生錯誤: {e}")
                errors.append(f"{file.filename}: {str(e)}")
                try:
                    if 'file_path' in locals() and os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
        else:
            errors.append(f"{file.filename}: 不是有效的檔案格式（支援 .csv, .xls, .xlsx）")
    
    return jsonify({
        'success': len(processed_files) > 0,
        'processed_files': processed_files,
        'errors': errors
    })

@app.route('/download/<filename>')
def download_file(filename):
    """下載處理後的檔案"""
    try:
        file_path = os.path.join(PROCESSED_FOLDER, secure_filename(filename))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "檔案不存在", 404
    except Exception as e:
        logger.error(f"下載檔案 {filename} 時發生錯誤: {e}")
        return f"下載錯誤: {str(e)}", 500

@app.route('/download_all')
def download_all():
    """打包下載所有處理後的檔案"""
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'processed_files.zip')
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename in os.listdir(PROCESSED_FOLDER):
                if filename.endswith('.csv'):
                    file_path = os.path.join(PROCESSED_FOLDER, filename)
                    zipf.write(file_path, filename)
        
        return send_file(zip_path, as_attachment=True, download_name='battery_test_results.zip')
    
    except Exception as e:
        logger.error(f"打包檔案時發生錯誤: {e}")
        return f"打包錯誤: {str(e)}", 500

@app.route('/clear')
def clear_files():
    """清理所有處理後的檔案"""
    try:
        for filename in os.listdir(PROCESSED_FOLDER):
            os.remove(os.path.join(PROCESSED_FOLDER, filename))
        return jsonify({'success': True, 'message': '檔案已清理'})
    except Exception as e:
        logger.error(f"清理檔案時發生錯誤: {e}")
        return jsonify({'success': False, 'message': f'清理錯誤: {str(e)}'})

@app.route('/health')
def health_check():
    """健康檢查端點"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)