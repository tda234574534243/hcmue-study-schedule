# 📅 HCMUE Schedule Tool (TKB)

Công cụ hỗ trợ lấy và hiển thị thời khóa biểu từ hệ thống **HCMUE** dành cho sinh viên.
---

## 🛠 Cài đặt & Thiết lập

### 1. Sử dụng Môi trường ảo (Khuyên dùng)
Để tránh xung đột thư viện và giữ máy sạch sẽ, bạn nên chạy tool trong môi trường ảo (`venv`):

1. Mở Terminal/CMD tại thư mục chứa code.
2. Chạy lệnh tạo môi trường ảo: 
   `python -m venv venv`
3. Kích hoạt môi trường ảo:
   - **Windows:** `venv\Scripts\activate`
   - **macOS/Linux:** `source venv/bin/activate`
4. Cài đặt thư viện: 
   `pip install requests python-dotenv tabulate pandas openpyxl`

### 2. Cấu hình thông tin ban đầu
Chạy script setup để khởi tạo thông tin đăng nhập và API Key:
`python setup.py`

> **Lưu ý:** Bạn cần lấy `API_KEY` và `CLIENT_ID` từ Network tab (F12) trên trang web của trường khi đăng nhập. Script sẽ tự động lưu vào file `.env`.

---

## 🚀 Hướng dẫn sử dụng

Sử dụng các Flag (tham số) sau để điều khiển tool:

| Lệnh | Chức năng |
| :--- | :--- |
| `python tkb.py` | Xem TKB toàn tuần (Danh sách) |
| `python tkb.py -l` | Xem TKB toàn tuần (Dạng lưới - Layout) |
| `python tkb.py -today` | Xem lịch học riêng ngày **Hôm nay** |
| `python tkb.py -t` | Xem lịch học riêng ngày **Ngày mai** |
| `python tkb.py -next` | Hiển thị môn sắp học & thời gian đếm ngược |
| `python tkb.py -search "Tên môn"` | Tìm kiếm lịch của một môn nhất định |
| `python tkb.py -export` | Xuất lịch tuần này ra file Excel (.xlsx) |
| `python tkb.py -h` | Hiển thị bảng trợ giúp (Help) |

---

## 💡 Mẹo nhỏ cho Windows (Quick Run)
Bạn có thể tạo một file tên là `run.bat` trong cùng thư mục với nội dung sau để chạy nhanh bằng cách click đúp:

```batch
@echo off
if not exist venv (
    echo [!] Dang khoi tao moi truong ao...
    python -m venv venv
    call venv\Scripts\activate
    pip install requests python-dotenv tabulate pandas openpyxl
) else (
    call venv\Scripts\activate
)
python tkb.py %*
pause