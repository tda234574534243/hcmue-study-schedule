import requests
import json
import urllib3
import os
import re
import argparse
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
from tabulate import tabulate

load_dotenv(override=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIG ---
USERNAME, PASSWORD = os.getenv("USERNAME"), os.getenv("PASSWORD")
API_KEY, CLIENT_ID = os.getenv("API_KEY"), os.getenv("CLIENT_ID")
NAM_HOC, HOC_KY = os.getenv("NAM_HOC"), os.getenv("HOC_KY")
TOKEN_FILE = "token_store.json"

NGAY_BAT_DAU_HK = datetime(2025, 12, 29)
THU_TU_THU = {"Thứ Hai": 2, "Thứ Ba": 3, "Thứ Tư": 4, "Thứ Năm": 5, "Thứ Sáu": 6, "Thứ Bảy": 7, "Chủ Nhật": 8}
LIST_THU = list(THU_TU_THU.keys())

def get_week_range(date):
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start.replace(hour=0, minute=0, second=0), end.replace(hour=23, minute=59, second=59)

def check_in_week(tuan_hoc_str, start_week, end_week):
    try:
        if "->" in tuan_hoc_str:
            s, e = tuan_hoc_str.split("->")
            return not (end_week < datetime.strptime(s.strip(), "%d/%m/%Y") or start_week > datetime.strptime(e.strip(), "%d/%m/%Y"))
        return start_week <= datetime.strptime(tuan_hoc_str.strip(), "%d/%m/%Y") <= end_week
    except: return True

def extract_ca_info(ca_str):
    """Bóc tách số tiết bắt đầu và giờ bắt đầu"""
    match = re.search(r'(\d+)\s*\((\d+)h(\d+)\)', str(ca_str))
    if match:
        ca_num = int(match.group(1))
        hour = int(match.group(2))
        minute = int(match.group(3))
        return ca_num, hour, minute
    return extract_ca_number(ca_str), 0, 0

def extract_ca_number(ca_str):
    match = re.search(r'\d+', str(ca_str))
    return int(match.group()) if match else 0

def get_access_token():
    # 1. Kiểm tra file token cũ
    if os.path.exists(TOKEN_FILE):
        print(f"[*] Đang dùng lại Token cũ từ file: {TOKEN_FILE}")
        with open(TOKEN_FILE, 'r') as f: 
            return json.load(f).get('token')
    
    # 2. Nếu không có file, tiến hành đăng nhập mới
    url = "https://onlineapi.hcmue.edu.vn/api/authenticate/authpsc"
    headers = {
        "Content-Type": "application/json", 
        "Apikey": API_KEY, 
        "Clientid": CLIENT_ID
    }
    
    # Debug xem gửi cái gì đi
    print(f"[*] Đang đăng nhập tài khoản: {USERNAME}")
    
    try:
        payload = {"username": USERNAME, "password": PASSWORD}
        res = requests.post(url, json=payload, headers=headers, verify=False, timeout=10)
        
        # --- KHÚC DEBUG QUAN TRỌNG ---
        print(f"[*] Server Response Code: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            token = data.get("Token")
            if token:
                print("[OK] Đăng nhập thành công! Đã lấy được Token mới.")
                with open(TOKEN_FILE, 'w') as f: 
                    json.dump({'token': token}, f)
                return token
            else:
                print("[!] Đăng nhập thành công nhưng không thấy Token trong JSON trả về.")
                print(f"[*] Body nhận được: {data}")
        else:
            print(f"[!] Đăng nhập thất bại. Mã lỗi: {res.status_code}")
            print(f"[*] Nội dung lỗi: {res.text}")
            
    except Exception as e:
        print(f"[!] Lỗi kết nối khi đăng nhập: {e}")
    
    return None

def show_next_class(filtered):
    now = datetime.now()
    day_name_map = {0: "Thứ Hai", 1: "Thứ Ba", 2: "Thứ Tư", 3: "Thứ Năm", 4: "Thứ Sáu", 5: "Thứ Bảy", 6: "Chủ Nhật"}
    today_vn = day_name_map[now.weekday()]
    
    today_classes = [i for i in filtered if i['Thu'] == today_vn]
    future_classes = []

    for c in today_classes:
        ca_num, h, m = extract_ca_info(c['CaHoc'])
        class_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if class_time > now:
            future_classes.append((class_time, c))
    
    if not future_classes:
        print("[*] Không còn tiết học nào trong hôm nay. Nghỉ ngơi đi!")
    else:
        future_classes.sort(key=lambda x: x[0])
        next_time, next_class = future_classes[0]
        diff = next_time - now
        minutes = int(diff.total_seconds() // 60)
        print(f"[!] TIẾT HỌC TIẾP THEO: {next_class['TenHP']}")
        print(f"    Phòng: {next_class['Phong']} | Bắt đầu lúc: {next_time.strftime('%H:%M')} (Còn {minutes} phút)")

def export_excel(filtered, start_w):
    filename = f"TKB_Tuan_{start_w.strftime('%d_%m')}.xlsx"
    data = []
    for i in filtered:
        data.append({
            "Thứ": i['Thu'],
            "Môn Học": i['TenHP'],
            "Ca Học": i['CaHoc'],
            "Phòng": i['Phong']
        })
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"[OK] Đã xuất lịch ra file: {filename}")

def fetch_and_show_tkb(args, token):
    params = {"namhoc": NAM_HOC, "hocky": HOC_KY}
    headers = {"Authorization": f"Bearer {token}", "Apikey": API_KEY, "Clientid": CLIENT_ID}
    
    target_date = datetime.now()
    if args.tomorrow: target_date += timedelta(days=1)
    
    start_w, end_w = get_week_range(target_date)
    current_week = ((start_w - NGAY_BAT_DAU_HK).days // 7) + 1
    day_name_map = {0: "Thứ Hai", 1: "Thứ Ba", 2: "Thứ Tư", 3: "Thứ Năm", 4: "Thứ Sáu", 5: "Thứ Bảy", 6: "Chủ Nhật"}
    target_vn = day_name_map[target_date.weekday()]

    try:
        res = requests.get("https://onlineapi.hcmue.edu.vn/api/student/DrawingStudentSchedule_Perior", params=params, headers=headers, verify=False)
        if res.status_code == 200:
            raw_data = res.json().get("result", [])
            filtered = [i for i in raw_data if check_in_week(i.get('TuanHoc', ''), start_w, end_w)]

            # 1. Tính năng Search
            if args.search:
                filtered = [i for i in filtered if args.search.lower() in i['TenHP'].lower()]
                print(f"[*] Kết quả tìm kiếm môn: '{args.search}' trong tuần này:")

            # 2. Tính năng Export
            if args.export:
                export_excel(filtered, start_w)
                return

            # 3. Tính năng Next
            if args.next:
                show_next_class(filtered)
                return

            # Lọc theo ngày (Hôm nay / Ngày mai)
            if args.today or args.tomorrow:
                filtered = [i for i in filtered if i['Thu'] == target_vn]
                status = "HÔM NAY" if args.today else "NGÀY MAI"
                print(f"[*] Lịch {status} ({target_vn} - {target_date.strftime('%d/%m')}):")
            else:
                print(f"[*] Học kỳ: {NAM_HOC} - {HOC_KY} | Tuần: {current_week}")

            if not filtered:
                print("--- Trống lịch ---")
                return

            # Hiển thị
            if args.layout and not (args.today or args.tomorrow or args.search):
                ca_map = {extract_ca_number(i['CaHoc']): i['CaHoc'] for i in filtered if i.get('CaHoc')}
                sorted_ca = sorted(ca_map.keys())
                table = []
                for cn in sorted_ca:
                    ca_str = ca_map[cn]
                    short_ca = f"Ca {cn}\n" + (ca_str.split('(')[1].split(')')[0] if '(' in ca_str else "")
                    row = [short_ca]
                    for thu in LIST_THU:
                        mon = next((i for i in filtered if i['Thu'] == thu and extract_ca_number(i.get('CaHoc')) == cn), None)
                        row.append(f"{mon['TenHP']}\n[{mon['Phong']}]" if mon else "---")
                    table.append(row)
                print(tabulate(table, headers=["Ca / Thứ"] + LIST_THU, tablefmt="grid", stralign="center"))
            else:
                filtered.sort(key=lambda x: (THU_TU_THU.get(x['Thu'], 9), extract_ca_number(x.get('CaHoc'))))
                clean = [[i['Thu'], i['TenHP'], i['CaHoc'], i['Phong']] for i in filtered]
                print(tabulate(clean, headers=["Thứ", "Môn Học", "Ca Học", "Phòng"], tablefmt="grid"))

        elif res.status_code == 401:
            if os.path.exists(TOKEN_FILE): os.remove(TOKEN_FILE)
            print("[!] Token hết hạn.")
    except Exception as e: print(f"[!] Lỗi: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HCMUE TKB Utility")
    parser.add_argument("-l", "--layout", action="store_true", help="Hiển thị lưới ngang")
    parser.add_argument("-t", "--tomorrow", action="store_true", help="Lịch ngày mai")
    parser.add_argument("-today", "--today", action="store_true", help="Lịch hôm nay")
    parser.add_argument("-export", action="store_true", help="Xuất Excel lịch tuần này")
    parser.add_argument("-next", action="store_true", help="Xem tiết học sắp tới")
    parser.add_argument("-search", type=str, help="Tìm kiếm môn học theo tên")
    
    args = parser.parse_args()
    t = get_access_token()
    if t: fetch_and_show_tkb(args, t)