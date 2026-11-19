# Kế hoạch tích hợp firmware (dựa trên dự án PlatformIO được cung cấp)

## Các thông tin đã kiểm tra trong dự án hiện tại

- Môi trường build: `yolo_uno`, sử dụng Arduino framework và nền tảng ESP32.
- `AsyncWebServer` được khởi tạo trên cổng **8080** trong `src/task_webserver.cpp`.
- Dự án đã có `task_rgb.cpp` để điều khiển module RGB 4 pixel của OhStem.
- Trong `task_rgb.cpp` được cung cấp, `NUM_RGB` có giá trị 4 và `RGB_PIN` là GPIO 8; chú thích trong mã ghi D9-D10. Ví dụ Arduino của OhStem mô tả module 4 LED được kết nối ở D3-D4 và sử dụng `D3`; một bài hướng dẫn khác của OhStem lại mô tả D9-D10. Hãy sử dụng cách đấu nối và mã nguồn đã hoạt động trên bộ kit hiện tại của bạn; không thay đổi chân này trong quá trình tích hợp TinyML.
- Trong firmware được cung cấp, task RGB hiện tại liên tục chuyển đổi màu sắc. Chỉ thay thế hành vi này khi tích hợp điều khiển bằng cử chỉ, hoặc bổ sung một hàng đợi lệnh RGB dùng chung. Không để hai tiến trình độc lập cùng ghi dữ liệu điều khiển NeoPixel.
- Các topic telemetry MQTT hiện tại có dạng `yolouno/esp32_01/telemetry`. Hãy giữ nguyên cấu trúc này và bổ sung các trường thông tin về cử chỉ vào payload JSON hiện có.

## Quy ước HTTP dự kiến

`POST /api/gesture/frame`

- Content-Type: `application/octet-stream`
- Nội dung body: chính xác 4096 byte, ảnh xám 64x64 được lưu theo thứ tự từng hàng (row-major), mỗi pixel chiếm một byte (giá trị từ 0 đến 255).
- HTTP handler phải từ chối dữ liệu có độ dài khác 4096 byte và không được chạy suy luận CNN bên trong callback bất đồng bộ.
- Handler cần sao chép toàn bộ khung hình vào một FreeRTOS queue chỉ có một phần tử (loại bỏ khung hình cũ nếu queue đã đầy). Một worker task sẽ thực hiện tiền xử lý và suy luận.
- Chương trình gửi dữ liệu và firmware phải thống nhất quy trình cắt ảnh, thay đổi kích thước và chuyển ảnh xám. Dự án này sử dụng cách cắt vùng vuông ở chính giữa, chuyển sang ảnh xám và thay đổi kích thước thành 64x64 bằng `INTER_AREA`.

## Bộ nhớ

Tài liệu sản phẩm chính thức của OhStem công bố PSRAM có dung lượng tối đa 8 MB. Hãy kiểm tra trực tiếp trên bo mạch bằng `psramFound()` và `ESP.getPsramSize()` trước khi cấp phát một vùng nhớ tensor arena lớn. Nếu bản TensorFlow Lite Micro được chọn yêu cầu, hãy bắt đầu bằng RAM nội bộ; kiểm tra riêng việc bố trí dữ liệu trên PSRAM sau đó. Runtime TFLM và operator resolver phải tương thích với phiên bản TensorFlow dùng để xuất mô hình.

## Trình tự tích hợp an toàn

1. Tạm thời thêm đoạn mã chẩn đoán trong `src/psram_check.cpp.txt` vào hàm `setup()` và ghi lại kết quả.
2. Xây dựng một chương trình kiểm thử suy luận TensorFlow Lite Micro độc lập, tối giản trước khi chỉnh sửa firmware chính.
3. Tích hợp endpoint POST vào `AsyncWebServer` hiện có (không tạo thêm một web server thứ hai trên cổng 8080).
4. Thêm hàng đợi khung hình có giới hạn và task suy luận. Tránh thực hiện suy luận bên trong HTTP callback.
5. Thêm hàng đợi kết quả cử chỉ/controller với ngưỡng độ tin cậy và cơ chế chống dao động theo thời gian (ví dụ: yêu cầu cùng một lớp được nhận diện trong 3 lần suy luận liên tiếp).
6. Chuyển lệnh màu từ controller đến task RGB hiện có. Chỉ một task được phép gọi `rgb.show()`.
7. Mở rộng JSON telemetry MQTT hiện có; không gửi byte ảnh qua MQTT/CoreIoT.

## Quyền quản lý RGB và các lưu ý an toàn

- Sử dụng cách đấu nối module hiện tại mà bạn đã kiểm thử thành công.
- Firmware được cung cấp có `RGB_PIN 8`, `NUM_RGB 4`; chú thích của mã ghi cổng Grove D9-D10. Không suy luận hoặc thay đổi chân GPIO chỉ dựa trên tên cổng được ghi trong chú thích.
- Chỉ định một task duy nhất chịu trách nhiệm quản lý đối tượng RGB. Các task khác gửi lệnh thông qua queue.
