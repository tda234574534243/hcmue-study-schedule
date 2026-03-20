import os
import re
from dotenv import load_dotenv

def get_current_config():
    """Đọc cấu hình hiện tại và loại bỏ dấu nháy để hiển thị"""
    config = {}
    if os.path.exists(".env"):
        # Đọc thủ công để tránh việc load_dotenv tự xử lý dấu nháy không như ý
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    # Loại bỏ dấu nháy đơn hoặc kép ở đầu/cuối giá trị nếu có
                    clean_val = val.strip().strip("'").strip('"')
                    config[key] = clean_val
    return config

def setup_env():
    print("=== CHƯƠNG TRÌNH CẤU HÌNH FILE .ENV (AUTO-QUOTE) ===")
    print("Gợi ý: Nhấn [Enter] để giữ lại giá trị cũ. Script sẽ tự bọc dấu nháy.\n")
    
    old_config = get_current_config()
    new_config = {}

    fields = [
        ('USERNAME', '1. Mã số sinh viên (Username)'),
        ('PASSWORD', '2. Mật khẩu'),
        ('API_KEY', '3. API Key'),
        ('CLIENT_ID', '4. Client ID'),
        ('NAM_HOC', '5. Năm học (VD: 2025-2026)'),
        ('HOC_KY', '6. Học kỳ (VD: HK02)')
    ]

    for key, label in fields:
        old_val = old_config.get(key, "")
        display_old = f" [{old_val}]" if old_val else ""
        
        user_input = input(f"{label}{display_old}: ").strip()
        
        # Lấy giá trị mới hoặc giữ giá trị cũ
        val_to_save = user_input if user_input else old_val
        new_config[key] = val_to_save

    # Ghi file với định dạng KEY='VALUE'
    try:
        with open(".env", "w", encoding="utf-8") as f:
            for key, value in new_config.items():
                # Ép kiểu string và bọc nháy đơn
                f.write(f"{key}='{value}'\n")
        
        # Xóa file token cũ nếu thông tin đăng nhập thay đổi
        if os.path.exists("token_store.json"):
            if new_config['USERNAME'] != old_config.get('USERNAME') or \
               new_config['PASSWORD'] != old_config.get('PASSWORD'):
                os.remove("token_store.json")
                print("\n[!] Đã xóa token_store.json để làm mới đăng nhập.")

        print("\n" + "="*45)
        print(" [OK] Cập nhật .env thành công (Đã bọc dấu nháy)!")
        print("="*45)
    except Exception as e:
        print(f"\n[!] Lỗi khi ghi file: {e}")

if __name__ == "__main__":
    setup_env()