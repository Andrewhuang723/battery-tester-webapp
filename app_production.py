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
import gzip
import base64
import io
import gc

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 生產環境配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'battery_tester_production_key_2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
MAX_RESPONSE_SIZE = 4.5 * 1024 * 1024  # 4.5MB Vercel payload limit safeguard

# 確保資料夾存在
# 在 Vercel 等 Serverless 環境中，通常只能寫入 /tmp 目錄
UPLOAD_FOLDER = '/tmp/uploads'
PROCESSED_FOLDER = '/tmp/processed'
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
    try:
        # 簡單的編碼偵測
        encodings = ['utf-8', 'cp950', 'latin1']
        for encoding in encodings:
            try:
                with open(fpath, 'r', encoding=encoding) as f:
                    for line in f:
                        row = line.strip().rsplit(",")
                        if len(row) > 0 and row[0] == "System Time":
                            return len(row)
                break
            except UnicodeDecodeError:
                continue
    except Exception:
        pass
    return 0

def is_match_date_string(ds: str):
    """檢查是否符合日期格式"""
    pattern = r"^\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$"
    return bool(re.match(pattern, ds))

def extract_origin_csv_original(fpath: str):
    """處理承德充放電機CSV檔案格式"""
    # rows = []  # 不再使用 list 儲存所有 rows
    last_time_per_step_list = []
    step_name = "Unknown"
    n_cols = get_n_cols(fpath=fpath)
    
    # 使用 StringIO 作為緩衝區，減少記憶體碎片化
    csv_buffer = io.StringIO()
    row_count = 0

    try:
        # 嘗試使用 utf-8 讀取，如果失敗則嘗試 cp950 (常見於繁體中文 Windows)
        encodings = ['utf-8', 'cp950', 'latin1']
        
        # 使用迭代器而非 readlines() 以節省記憶體
        file_iterator = None
        
        for encoding in encodings:
            try:
                # 測試是否能讀取
                with open(fpath, 'r', encoding=encoding) as f:
                    f.read(1024) # 嘗試讀取一小段
                
                # 如果成功，重新開啟並使用該編碼
                file_iterator = open(fpath, 'r', encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if file_iterator is None:
            # 如果所有編碼都失敗，使用 errors='replace'
            file_iterator = open(fpath, 'r', encoding='utf-8', errors='replace')

        try:
            for line in file_iterator:
                # 快速檢查是否為特殊行，避免 split 所有行
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                    
                # 簡單的字串檢查比 split 快
                if stripped_line.startswith(('%', '@', 'Label', '$', 'System Time', 'Start Time')) or stripped_line.startswith(',,'):
                    row = stripped_line.rsplit(',')
                    if len(row) >= 3 and row[0] == "" and row[1] == "":
                        step_name = row[2]         
                    elif len(row) >= 1 and row[0] == '%':
                        last_time_per_step_list.append(row_count - 1)
                else:
                    # 這是資料行嗎？
                    # 為了效能，我們先檢查開頭是否為數字 (日期格式)
                    if stripped_line[0].isdigit():
                        row = stripped_line.rsplit(',')
                        if len(row) == n_cols and is_match_date_string(row[0]):
                            # 寫入 buffer，補上 step_name
                            # 注意：這裡我們手動構建 CSV 行，比 append list 快
                            csv_buffer.write(f"{stripped_line},{step_name}\n")
                            row_count += 1
        finally:
            file_iterator.close()

        last_time_per_step_list.append(row_count - 1)
        
        # 將 buffer 轉回開頭
        csv_buffer.seek(0)
        
        return csv_buffer, last_time_per_step_list
        
    except Exception as e:
        logger.error(f"Error processing file {fpath}: {e}")
        raise Exception(f"檔案處理錯誤: {str(e)}。請確認檔案格式是否正確。")

def process_battery_data(file_path, output_folder):
    """完整的電池資料處理函數"""
    try:
        logger.info(f"開始處理檔案: {file_path}")
        
        # 檢查檔案大小，如果太大可能導致超時
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024: # 50MB
            logger.warning(f"檔案過大 ({file_size/1024/1024:.2f} MB)，可能會導致處理超時")

        csv_buffer, steps = extract_origin_csv_original(file_path)
        
        # 使用 read_csv 直接從 buffer 讀取，比 DataFrame(rows) 快且省記憶體
        # 我們需要手動指定欄位名稱，因為 buffer 中沒有 header
        col_names = ["System Time", "Step Time", "V", "I", "T", "R", "P", "mAh", "Wh", "Total Time", "Step name"]
        
        try:
            df = pd.read_csv(csv_buffer, names=col_names, header=None)
        except pd.errors.EmptyDataError:
             return False, "無法從檔案中提取有效數據，請確認檔案內容。"
             
        # 釋放 buffer
        csv_buffer.close()
        del csv_buffer
        gc.collect()

        df["System Time"] = pd.to_datetime(df["System Time"], format="%y/%m/%d %H:%M:%S", errors='coerce')
        # 移除無法轉換時間的行
        df = df.dropna(subset=["System Time"])
        
        # 轉換數值欄位
        numeric_cols = ["V", "I", "T", "R", "P", "mAh", "Wh"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        filename_head = os.path.basename(file_path).split(".")[0]
        
        # 移除寫入磁碟的操作以節省 IO 和空間
        # detail_file_path = os.path.join(output_folder, f"{filename_head}_detail.csv")
        # df.to_csv(detail_file_path, index=False)
        
        # step_df = df.loc[steps]
        # step_file_path = os.path.join(output_folder, f"{filename_head}_step.csv")
        # step_df.to_csv(step_file_path, index=False)
        
        # 確保 steps 索引在有效範圍內
        valid_steps = [s for s in steps if 0 <= s < len(df)]
        step_df = df.iloc[valid_steps] # 使用 iloc 因為 steps 是整數位置
        
        logger.info(f"處理完成: {len(df)} 行資料, {len(step_df)} 個步驟")

        # 壓縮資料以減少傳輸大小 (解決 Vercel 4.5MB 限制)
        def compress_data(data_str):
            try:
                compressed = gzip.compress(data_str.encode('utf-8'))
                return base64.b64encode(compressed).decode('ascii')
            except Exception as e:
                logger.error(f"壓縮失敗: {e}")
                return None
        
        # 檢查資料大小
        detail_csv = df.to_csv(index=False)
        step_csv = step_df.to_csv(index=False)
        
        # 釋放 DataFrame
        del df
        del step_df
        gc.collect()
        
        detail_b64 = compress_data(detail_csv)
        step_b64 = compress_data(step_csv)
        
        # 釋放 CSV 字串
        del detail_csv
        del step_csv
        gc.collect()
        
        return True, {
            'detail_file': f"{filename_head}_detail.csv",
            'step_file': f"{filename_head}_step.csv",
            'detail_content_b64': detail_b64,
            'step_content_b64': step_b64,
            'total_rows': len(detail_b64) if detail_b64 else 0, # 這裡回傳長度作為參考
            'step_rows': len(step_b64) if step_b64 else 0
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
    current_response_size = 0
    
    for file in files:
        if file and (file.filename.endswith('.csv') or file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
            try:
                # 檢查目前回應大小是否已接近上限
                if current_response_size > MAX_RESPONSE_SIZE:
                    errors.append(f"{file.filename}: 略過處理，因為單次請求的總回應大小已達上限 (4.5MB)。請分批上傳。")
                    continue

                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                success, result = process_battery_data(file_path, PROCESSED_FOLDER)
                
                if success:
                    # 計算新增的大小
                    detail_len = len(result.get('detail_content_b64', '')) if result.get('detail_content_b64') else 0
                    step_len = len(result.get('step_content_b64', '')) if result.get('step_content_b64') else 0
                    total_len = detail_len + step_len
                    
                    if current_response_size + total_len > MAX_RESPONSE_SIZE:
                        # 如果加上這個檔案會超過限制，則只回傳步驟資料或報錯
                        if current_response_size + step_len < MAX_RESPONSE_SIZE:
                             processed_files.append({
                                'original': filename,
                                'detail_file': result['detail_file'],
                                'step_file': result['step_file'],
                                'detail_content_b64': None, # 省略詳細資料
                                'step_content_b64': result.get('step_content_b64'),
                                'message': f"成功處理 (詳細資料過大已省略，僅提供步驟資料)"
                            })
                             current_response_size += step_len
                        else:
                            errors.append(f"{filename}: 處理成功但結果過大無法回傳。")
                    else:
                        processed_files.append({
                            'original': filename,
                            'detail_file': result['detail_file'],
                            'step_file': result['step_file'],
                            'detail_content_b64': result.get('detail_content_b64'),
                            'step_content_b64': result.get('step_content_b64'),
                            'message': f"成功處理" # 簡化訊息，因為 total_rows 現在是長度
                        })
                        current_response_size += total_len
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
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)