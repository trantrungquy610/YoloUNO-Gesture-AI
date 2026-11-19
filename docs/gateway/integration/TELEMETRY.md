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
  "gesture_count": 12
}
```

Không gửi các khung hình webcam thông qua MQTT. Chỉ gửi kết quả suy luận và trạng thái thiết bị. Chỉ bổ sung các khóa telemetry mới vào cấu hình ánh xạ MQTT connector và dashboard của ThingsBoard/CoreIoT sau khi thiết bị đã publish các trường dữ liệu đó thành công.
