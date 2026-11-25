# Mở rộng telemetry cho Gateway / CoreIoT

Giữ nguyên các MQTT topic mà firmware được cung cấp đang sử dụng:

- `yolouno/esp32_01/telemetry`
- `yolouno/esp32_01/status`
- `yolouno/esp32_01/command`

Bổ sung các trường sau vào JSON telemetry hiện có (các giá trị trong ví dụ chỉ nhằm minh họa):

```json
{
  "temperature": 26.5,
  "humidity": 48.2,
  "gesture": "open_palm",
  "confidence": 0.96,
  "inference_ms": 42.0,
  "gesture_count": 12,
  "fan_speed_percent": 75
}
```

`gesture` là nhãn dự đoán có độ tin cậy đạt ngưỡng; khi thấp hơn ngưỡng thì firmware gửi `unknown`. `confidence` nằm trong khoảng 0–1, `inference_ms` là thời gian chạy `Invoke()` của mô hình, `gesture_count` tăng khi chuyển sang một cử chỉ hành động tin cậy mới (được mở khóa lại bởi `no_hand` hoặc `unknown`), và `fan_speed_percent` là tốc độ PWM được đặt theo lệnh, trong khoảng 0–100. `gesture_count` bắt đầu lại từ 0 sau khi khởi động lại bo mạch. `fan_speed_percent` chưa phải phản hồi từ cảm biến tốc độ quạt.

Không gửi các khung hình webcam thông qua MQTT. Chỉ gửi kết quả suy luận và trạng thái thiết bị. Trong CoreIoT, ánh xạ `gesture` kiểu String; `confidence` kiểu Double; `inference_ms`, `gesture_count` và `fan_speed_percent` kiểu Long. Widget slider điều khiển quạt gọi RPC `setFanSpeed` với giá trị số nguyên 0–100 trong `params`. Chỉ bổ sung các khóa telemetry mới vào cấu hình ánh xạ MQTT connector và dashboard sau khi thiết bị đã publish các trường đó thành công.
