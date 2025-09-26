from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
import pandas as pd
import io
import os
import tempfile
import zipfile
from werkzeug.utils import secure_filename
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'battery_tester_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 確保上傳資料夾存在
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def convert_to_seconds(row):
    """
    將時間字串轉換為秒數 (來自 utils.py)
    """
    try:
        hours, minutes, seconds = map(float, row.split(":"))
        total_seconds = float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        return total_seconds
    except Exception as e:
        print(f"Error processing row: {row}, Error: {e}")
        return None

def get_n_cols(fpath: str):
    """
    取得欄位數量 (來自 utils.py)
    """
    f = open(fpath, 'r')
    for line in f.readlines():
        row = line.strip().rsplit(",")
        if len(row) > 0 and row[0] == "System Time":
            return len(row)
    return 0

def is_match_date_string(ds: str):
    """
    檢查是否符合日期格式 (來自 utils.py)
    """
    pattern = r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$"
    if re.match(pattern, ds):
        return True
    return False

def extract_origin_csv_original(fpath: str):
    """
    原始的 extract_origin_csv 函數 (來自 utils.py)
    處理承德充放電機CSV檔案格式
    """
    f = open(fpath, 'r')
    rows = []
    last_time_per_step_list = []
    step_name = None
    n_cols = get_n_cols(fpath=fpath)

    try:
        for line in f.readlines():
            row = line.strip().rsplit(",")
            if len(row) > 0 and row[0] in {"%", "@", "Label", "", "$", "System Time", "Start Time"}: #content
                if len(row) == 5 and row[0] == "" and row[1] == "": #header line 4
                    step_name = row[2]         
                elif len(row) == 2 and row[0] == '%': # header line 1
                    last_time_per_step_list.append(len(rows)-1)
                else:
                    pass
            else:
                if len(row) == n_cols and is_match_date_string(row[0]): # ensure the number of columns matches the data columns
                    row.append(step_name)
                    rows.append(row)

        last_time_per_step_list.append(len(rows) -1)
    
    except:
        raise Exception("此檔案並非'承德充放電機'檔案格式，請確認選擇檔案。")

    return rows, last_time_per_step_list

def process_battery_data(file_path, output_folder):
    """
    完整的電池資料處理函數 (整合自 run_gui.py)
    """
    try:
        # 使用原始的 extract_origin_csv 函數
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
        
        return True, {
            'detail_file': f"{filename_head}_detail.csv",
            'step_file': f"{filename_head}_step.csv",
            'total_rows': len(df),
            'step_rows': len(step_df)
        }
        
    except Exception as e:
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
                # 安全的檔案名稱
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # 使用完整的電池資料處理函數
                success, result = process_battery_data(file_path, PROCESSED_FOLDER)
                
                print(f"處理檔案 {filename}: success={success}, result={result}")  # 除錯
                
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
                errors.append(f"{file.filename}: {str(e)}")
                # 如果有錯誤，也要清理上傳的檔案
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
        else:
            errors.append(f"{file.filename}: 不是有效的檔案格式（支援 .csv, .xls, .xlsx）")
    
    response_data = {
        'success': len(processed_files) > 0,
        'processed_files': processed_files,
        'errors': errors
    }
    
    print(f"回傳資料: {response_data}")  # 除錯
    
    return jsonify(response_data)

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
        return f"下載錯誤: {str(e)}", 500

@app.route('/download_all')
def download_all():
    """打包下載所有處理後的檔案"""
    try:
        # 創建臨時zip檔案
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, 'processed_files.zip')
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename in os.listdir(PROCESSED_FOLDER):
                if filename.endswith('.csv'):
                    file_path = os.path.join(PROCESSED_FOLDER, filename)
                    zipf.write(file_path, filename)
        
        return send_file(zip_path, as_attachment=True, download_name='battery_test_results.zip')
    
    except Exception as e:
        return f"打包錯誤: {str(e)}", 500

@app.route('/clear')
def clear_files():
    """清理所有處理後的檔案"""
    try:
        for filename in os.listdir(PROCESSED_FOLDER):
            os.remove(os.path.join(PROCESSED_FOLDER, filename))
        return jsonify({'success': True, 'message': '檔案已清理'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'清理錯誤: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)