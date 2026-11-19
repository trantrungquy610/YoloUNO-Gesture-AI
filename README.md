# YoloUNO Gesture AI

Đây là workspace độc lập dành cho dự án nhận diện cử chỉ bàn tay bằng TinyML, sử dụng webcam của laptop và bo mạch YOLO UNO.

## Kiến trúc đã chọn

- **Webcam laptop:** Chỉ thực hiện việc thu thập hình ảnh và tiền xử lý: cắt vùng ảnh, đổi kích thước, chuyển sang ảnh xám 64x64; sau đó gửi dữ liệu qua Wi-Fi.
- **YOLO UNO (ESP32-S3):** Nhận khung hình gồm 4096 byte, chạy mô hình CNN tự xây dựng ở định dạng INT8 bằng TensorFlow Lite Micro, phân loại cử chỉ và điều khiển module OhStem RGB 4 LED.
- **IoT Gateway/CoreIoT:** Chỉ nhận dữ liệu telemetry như cử chỉ, độ tin cậy, thời gian suy luận và giá trị cảm biến. Không truyền hình ảnh qua MQTT.

## Cấu trúc dự án

```text
YoloUNO-Gesture-AI/
├── dataset/raw/                 # ảnh thu thập; mỗi phiên ghi hình là một thư mục riêng
├── webcam/
│   ├── check_webcam.py
│   ├── collect_dataset.py
│   └── webcam_sender.py
├── training/
│   ├── prepare_split.py
│   ├── train_cnn.py
│   ├── evaluate_model.py
│   └── export_int8.py
├── models/                      # các tệp mô hình được tạo sau khi huấn luyện
├── firmware/                    # tài liệu tích hợp và mã chẩn đoán
├── gateway/integration/         # quy ước dữ liệu telemetry MQTT/CoreIoT
├── docs/
└── requirements.txt
```

## 1. Tạo môi trường Python

Khuyến nghị sử dụng Python 3.10 hoặc 3.11 bản 64-bit. Mở PowerShell tại thư mục dự án và chạy:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu không cài được TensorFlow với phiên bản Python hiện tại, hãy dùng Python 3.11 x64 và tạo lại môi trường ảo.

## 2. Kiểm tra webcam

```powershell
python webcam/check_webcam.py
```

Chương trình sẽ in ra độ phân giải thực tế và hiển thị cửa sổ xem trước. Chương trình yêu cầu webcam chạy ở 1280x720, nhưng driver của camera có thể tự chọn một chế độ khác mà thiết bị hỗ trợ. Xem thêm `docs/WEBCAM_AND_NETWORK.md`.

## 3. Thu thập dataset

```powershell
python webcam/collect_dataset.py
```

Các phím điều khiển:

- Nhấn `1`: chọn lớp `open_palm` (xòe bàn tay).
- Nhấn `2`: chọn lớp `fist` (nắm tay).
- Nhấn `3`: chọn lớp `thumbs_up` (giơ ngón cái).
- Nhấn `4`: chọn lớp `victory` (ký hiệu chữ V).
- Nhấn `5`: chọn lớp `no_hand` (không có bàn tay trong khung hình).
- Nhấn `SPACE`: lưu một ảnh đã cắt; nhấn `Q` để thoát.

Hãy thu thập nhiều phiên ghi hình riêng biệt cho mỗi lớp (ít nhất 3 phiên; khuyến nghị 5–10 phiên). Thay đổi điều kiện ánh sáng, phông nền, khoảng cách bàn tay, góc xoay, tay trái/tay phải và người thực hiện. Với lớp `no_hand`, giữ nguyên bố cục camera nhưng không đưa bàn tay vào khung hình.

Có thể bắt đầu với khoảng 300–500 ảnh cho mỗi lớp, được thu thập qua nhiều phiên khác nhau. Đây chỉ là số lượng khởi đầu để thử nghiệm, không đảm bảo trước độ chính xác của mô hình.

## 4. Chia tập dữ liệu theo phiên ghi hình

```powershell
python training/prepare_split.py
```

Chương trình sẽ chia toàn bộ phiên ghi hình vào các tập `train`, `validation` và `test`. Cách chia này giúp tránh việc các khung hình gần nhau trong cùng một phiên xuất hiện đồng thời ở nhiều tập dữ liệu. Mỗi lớp cần ít nhất 3 phiên ghi hình.

## 5. Huấn luyện và đánh giá mô hình

```powershell
python training/train_cnn.py
python training/evaluate_model.py
```

Mô hình ban đầu là CNN nhỏ do dự án tự xây dựng, có đầu vào kích thước 64x64x1 và 5 lớp đầu ra. Hãy kiểm tra confusion matrix (ma trận nhầm lẫn) sau khi đánh giá. Nếu kết quả chưa tốt, nên cải thiện dữ liệu thu thập trước khi tăng độ phức tạp của mô hình.

## 6. Xuất mô hình TFLite INT8

```powershell
python training/export_int8.py
```

Lệnh này tạo tệp `models/gesture_model_int8.tflite`. Tệp xuất ra hiện chưa phải mảng C dùng trực tiếp trong firmware. Ở giai đoạn firmware tiếp theo, cần kiểm tra:

- Các toán tử được TensorFlow Lite Micro hỗ trợ.
- Kích thước `tensor arena`.
- Các tham số lượng tử hóa đầu vào/đầu ra.
- Khả năng tương thích khi chạy trên ESP32-S3.

Chỉ chuyển tệp `.tflite` thành mảng byte C/C++ sau khi hoàn tất các bước kiểm tra trên.

## 7. Tích hợp firmware và Gateway

Đọc hai tài liệu sau trước khi tích hợp:

- `firmware/docs/INTEGRATION_PLAN.md`
- `gateway/integration/TELEMETRY.md`

Thư mục firmware được cung cấp chỉ chứa quy ước tích hợp và mã khởi đầu, **không phải firmware hoàn chỉnh để thay thế trực tiếp firmware hiện tại**. Các thành phần Wi-Fi, AsyncWebServer, MQTT, DHT20, FreeRTOS và RGB hiện có sẽ được giữ lại, không ghi đè.

Endpoint HTTP nhận khung hình và task suy luận TensorFlow Lite Micro cần được tích hợp, sau đó kiểm thử với đúng các thư viện đang được sử dụng trong dự án PlatformIO hiện tại.

## Quy ước điều khiển theo cử chỉ

| Lớp nhận diện | Hành vi RGB đề xuất |
|---|---|
| `open_palm` | Xanh lá |
| `fist` | Đỏ |
| `thumbs_up` | Xanh dương |
| `victory` | Vàng |
| `no_hand` / `unknown` | Không phát lệnh mới; có thể tắt LED nếu trạng thái kéo dài quá thời gian quy định |

Sử dụng ngưỡng độ tin cậy (ban đầu là `0.70`) kết hợp với cơ chế xác nhận theo thời gian (*temporal debounce*): chỉ thay đổi đầu ra khi cùng một lớp được nhận diện liên tiếp qua một số khung hình. Lớp `no_hand` không được phát lệnh điều khiển.

## Các giới hạn cần lưu ý

- Dự án không kèm ảnh dataset hoặc mô hình đã huấn luyện; cần tự thu thập dữ liệu và huấn luyện trên máy tính.
- `webcam_sender.py` chỉ nên sử dụng sau khi endpoint nhận khung hình trên firmware đã được triển khai.
- Bắt đầu với tốc độ 2 FPS; chỉ tăng sau khi đo độ trễ từ đầu đến cuối và xác nhận hệ thống hoạt động ổn định.
- Kiểm tra PSRAM thực tế của bo mạch khi chạy bằng `psramFound()` và `ESP.getPsramSize()`, dù tài liệu sản phẩm OhStem công bố dung lượng tối đa 8 MB.
