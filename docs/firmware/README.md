# Tài liệu khởi đầu tích hợp firmware

Thư mục này chủ yếu chứa tài liệu tích hợp và các hằng số dùng chung, không phải một bộ firmware hoàn chỉnh để thay thế firmware hiện tại. Hãy đọc `docs/INTEGRATION_PLAN.md` trước khi chỉnh sửa dự án PlatformIO đang sử dụng.

Trong firmware được cung cấp đã có task điều khiển RGB và AsyncWebServer chạy ở cổng 8080. Hãy tích hợp dựa trên các thành phần sẵn có này, tránh tạo thêm web server trùng lặp hoặc để nhiều task cùng điều khiển NeoPixel độc lập.
