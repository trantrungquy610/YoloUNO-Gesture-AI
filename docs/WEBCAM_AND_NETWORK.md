# Thiết lập webcam và Wi-Fi

## Kiểm tra độ phân giải webcam (Windows)

```powershell
py -m venv .venv
.venv\\Scripts\\activate
pip install opencv-python
python webcam/check_webcam.py
```

Chương trình sẽ yêu cầu độ phân giải 1280x720, sau đó in ra chế độ thực tế mà driver camera trả về. Nhấn `Q` để thoát. Nếu không mở được webcam, hãy đóng Teams/Zoom/Camera rồi thử đặt `CAMERA_INDEX = 1` trong mã nguồn.

## Yêu cầu kết nối Wi-Fi

1. Laptop và YOLO UNO phải kết nối cùng một mạng LAN/subnet. Wi-Fi dành cho khách (Guest Wi-Fi) hoặc tính năng cô lập các thiết bị (client isolation) có thể chặn lưu lượng kết nối trực tiếp giữa các thiết bị.
2. Lấy địa chỉ IP STA của ESP32 từ Serial Monitor (firmware sẽ in dòng `STA IP: ...`).
3. Xác nhận cổng 8080 có thể truy cập được và endpoint tương ứng đã được triển khai trong firmware trước khi chạy chương trình gửi dữ liệu.
4. Bắt đầu với tốc độ 2 FPS. Chỉ tăng tốc độ sau khi đã đo thời gian truyền HTTP, thời gian suy luận và xác nhận hệ thống hoạt động ổn định.
5. Nếu Windows Firewall hiển thị yêu cầu cấp quyền, hãy cho phép Python hoạt động trên mạng riêng (Private network).

## Gửi các khung hình (sau khi endpoint firmware được triển khai)

```powershell
python webcam/webcam_sender.py --url http://ESP32_STA_IP:8080/api/gesture/frame --fps 2 --preview
```

Thay `ESP32_STA_IP` bằng địa chỉ hiện tại được bo mạch in ra. Chương trình gửi 4096 byte cho mỗi khung hình (ảnh xám kích thước 64x64). Chương trình chỉ gửi dữ liệu, không thực hiện phân loại cử chỉ.
