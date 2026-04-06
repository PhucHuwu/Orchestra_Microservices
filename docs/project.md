**TÀI LIỆU YÊU CẦU DỰ ÁN**

**Orchestra Microservices**

Mô phỏng hệ thống phân tán bằng âm nhạc & IoT

|            |                                         |
|------------|-----------------------------------------|
| Phiên bản: | 1.0                                     |
| Đối tượng: | Sinh viên / Nhóm đồ án môn học          |
| Lĩnh vực:  | Hệ thống phân tán · Message Queue · IoT |

**1. Tổng quan dự án**

**1.1 Ý tưởng cốt lõi**

Dự án xây dựng một hệ thống microservices phân tán, trong đó mỗi service đóng vai trò một nhạc cụ trong giàn hợp xướng. Các service cần phải được đồng bộ hoá thông qua hàng đợi RabbitMQ để chơi nhạc một cách có trật tự, không hỗn loạn.

Điểm đặc biệt: mọi khái niệm phức tạp của hệ thống phân tán đều được \"nghe thấy\" trực tiếp qua âm thanh --- consumer lag làm nhạc bị trễ, service chết khiến một nhạc cụ im lặng, network partition khiến bản nhạc lạc nhịp.

**1.2 Bảng metaphor --- Âm nhạc vs Distributed Systems**

|                             |                                           |
|-----------------------------|-------------------------------------------|
| **Âm nhạc**                 | **Hệ thống phân tán**                     |
| Giàn hợp xướng              | Toàn bộ hệ thống microservices            |
| Nhạc trưởng (Conductor)     | Conductor Service --- điều phối trung tâm |
| Nhạc cụ (Violin, Piano\...) | Microservice độc lập                      |
| Bản nhạc (Sheet music)      | Message schema / Event contract           |
| Nhịp độ (Tempo / BPM)       | Message rate / Throughput                 |
| Lạc nhịp (Out of sync)      | Consumer lag, Race condition              |
| Nhạc cụ im lặng đột ngột    | Service crash / Circuit breaker           |
| Nhạc cụ mới gia nhập        | Dynamic service discovery                 |

**2. Kiến trúc hệ thống**

**2.1 Tổng quan kiến trúc**

Hệ thống được thiết kế theo hướng tối giản chi phí phù hợp với sinh viên: logic microservices có thể chạy trên một hoặc nhiều máy tính local trong cùng mạng LAN (mỗi máy có thể chạy 1 service hoặc nhiều service) qua Docker Compose, kết hợp với một thiết bị IoT giá rẻ đóng vai trò \"loa thông minh\" --- nhận message từ queue và phát âm thanh thật.

|                                                                                       |
|---------------------------------------------------------------------------------------|
| **Nguyên tắc thiết kế**                                                                                      |
| • Toàn bộ microservices chạy local --- không cần thuê server                                                 |
| • Hỗ trợ mô hình đa máy local trong LAN: 1 máy/1 service hoặc 1 máy/nhiều service                           |
| • IoT device chỉ làm 1 việc: lắng nghe queue và phát âm --- không chứa business logic                        |
| • Chi phí phần cứng thực tế: 80.000 -- 200.000 VND (ESP32 + buzzer/loa nhỏ)                                  |
| • Mọi tính năng phân tán vẫn được demo đầy đủ và nghe thấy được                                              |

**2.2 Ba tầng hệ thống**

**Tầng 1 --- Docker Compose (Cụm máy local hoặc một laptop)**

Các services chạy trong container Docker trên một hoặc nhiều máy tính cá nhân (cùng LAN):

- RabbitMQ Broker: single node, bật Management UI tại cổng 15672 để quan sát queue real-time

- Conductor Service: đọc file nhạc MIDI (.mid), publish note event vào đúng queue theo BPM

- Instrument Services (Violin, Piano, Drums, Cello): mỗi service là một consumer độc lập

- Mixer Service: tổng hợp output từ các nhạc cụ, publish vào playback.output queue

- Dashboard: hiển thị consumer lag, queue depth, BPM, trạng thái từng service

**Tầng 2 --- IoT Device (Phần cứng)**

Một thiết bị phần cứng duy nhất kết nối WiFi vào cùng mạng LAN với cụm máy local (hoặc laptop chạy broker):

- Subscribe vào queue playback.output

- Nhận message chứa thông tin note: pitch, duration, volume

- Phát âm thanh ra loa/buzzer tương ứng

- Không chứa bất kỳ business logic nào --- đây là điểm quan trọng để minh hoạ tính tách biệt của microservices

**2.3 Lựa chọn thiết bị IoT**

|                         |                                                                          |                      |
|-------------------------|--------------------------------------------------------------------------|----------------------|
| **Thiết bị**       | **Ưu điểm**                                                   | **Chi phí**      |
| **ESP32 (chốt)**   | WiFi tích hợp, DAC analog, cộng đồng lớn, dễ mua tại VN      | **80--120k VND** |

**3. Đặc tả các services**

**3.1 Conductor Service**

Service trung tâm, chịu trách nhiệm điều phối toàn bộ bản nhạc.

- Đọc file nhạc định dạng MIDI (.mid) làm đầu vào chuẩn

- Chuẩn hóa nội bộ thành JSON event trong pipeline (không nhận JSON từ người dùng ở baseline)

- Parse ra danh sách note event có timestamp theo BPM

- Publish từng note vào đúng exchange/queue của nhạc cụ tương ứng

- Hỗ trợ thay đổi BPM real-time qua queue tempo.control

- Publish heartbeat event định kỳ để các service đồng bộ nhịp

**3.2 Instrument Services**

Mỗi nhạc cụ là một service độc lập, chạy trong Docker container riêng biệt.

|             |                        |                               |
|-------------|------------------------|-------------------------------|
| **Service** | **Queue subscribe**    | **Hành động**                 |
| Violin      | instrument.violin.note | Phát giai điệu chính (melody) |
| Piano       | instrument.piano.note  | Phát hoà âm (harmony)         |
| Drums       | instrument.drums.beat  | Giữ nhịp (rhythm)             |
| Cello       | instrument.cello.note  | Phát bè trầm (bass line)      |

**3.3 Mixer Service**

Nhận output từ tất cả instrument services, tổng hợp và publish vào queue playback.output mà IoT device lắng nghe.

**3.4 Dashboard Service**

Giao diện web hiển thị real-time các chỉ số: consumer lag của từng queue, số note đã xử lý, latency giữa beat được lên lịch và beat thực tế, trạng thái health của từng service.

**3.5 IoT Playback Service (trên thiết bị vật lý)**

Service cực đơn giản, chạy trên ESP32. Toàn bộ logic gói gọn trong vòng lặp: kết nối WiFi, kết nối RabbitMQ qua MQTT plugin, subscribe topic `playback.output`, phát âm thanh. Không có business logic, không biết về Conductor hay các service khác.

**4. Message schema**

**4.1 Note Event**

Format JSON được publish vào queue của từng nhạc cụ:

|                |                  |                                          |
|----------------|------------------|------------------------------------------|
| **Trường**     | **Kiểu dữ liệu** | **Mô tả**                                |
| **note_id**    | string (UUID)    | Định danh duy nhất của note              |
| **instrument** | string           | Tên nhạc cụ: violin, piano, drums, cello |
| **pitch**      | integer (0--127) | Giá trị MIDI pitch (60 = C4)             |
| **duration**   | float (giây)     | Thời gian giữ nốt (ví dụ: 0.5)           |
| **volume**     | integer (0--127) | Độ to (MIDI velocity)                    |
| **beat_time**  | float (giây)     | Thời điểm dự kiến phát theo BPM          |
| **timestamp**  | ISO 8601         | Thời điểm Conductor publish message      |

**4.2 RabbitMQ Exchange & Queue**

- Exchange type: Topic exchange, tên: orchestra.events

- Routing key pattern: instrument.\<name\>.note hoặc instrument.\<name\>.beat

- Queue playback.output: nhận tổng hợp từ Mixer, IoT device subscribe vào đây

- Queue tempo.control: Conductor lắng nghe lệnh thay đổi BPM từ Dashboard

**5. Stack công nghệ**

|                      |                                                 |
|----------------------|-------------------------------------------------|
| **Thành phần**       | **Công nghệ**                                   |
| Message broker       | RabbitMQ 3.x --- Management UI, MQTT plugin     |
| Microservices        | Python 3.11+ với thư viện pika                  |
| Âm thanh (software)  | Không bắt buộc ở backend (playback chính trên ESP32) |
| Container hoá        | Docker & Docker Compose                         |
| IoT firmware (ESP32) | MicroPython + thư viện umqtt                    |
| Dashboard            | FastAPI + WebSocket + Next.js                   |
| File nhạc đầu vào    | MIDI (.mid) - định dạng chuẩn, phổ biến, dễ lấy dữ liệu |
| Monitoring           | RabbitMQ Management API + Prometheus (tùy chọn) |

**6. Kịch bản demo**

Các kịch bản dưới đây được thiết kế để minh hoạ trực quan từng khái niệm của hệ thống phân tán --- người xem sẽ nghe thấy hậu quả của từng sự cố qua loa vật lý.

|                                                                                 |
|---------------------------------------------------------------------------------|
| **Demo 1 --- Consumer lag gây lạc nhịp**                                        |
| Mô phỏng: Làm chậm nhân tạo một Instrument service (sleep delay).               |
| Kết quả nghe thấy: Nhạc cụ đó bị trễ dần, queue tích lũy, toàn bản nhạc bị méo. |
| Khái niệm học được: Consumer lag, back-pressure, queue depth monitoring.        |

|                                                                                    |
|------------------------------------------------------------------------------------|
| **Demo 2 --- Service crash & recovery**                                            |
| Mô phỏng: Dừng (docker stop) một Instrument service giữa chừng.                    |
| Kết quả nghe thấy: Nhạc cụ đó im lặng hoàn toàn; khởi động lại thì message dồn về. |
| Khái niệm học được: Message durability, consumer recovery, dead letter queue.      |

|                                                                                |
|--------------------------------------------------------------------------------|
| **Demo 3 --- Scale horizontal (competing consumers)**                          |
| Mô phỏng: Chạy 3 instance của Violin service cùng lúc.                         |
| Kết quả nghe thấy: Mỗi instance chỉ nhận 1/3 note --- âm thanh bị rời rạc.     |
| Khái niệm học được: Competing consumers, message ordering, partition strategy. |

|                                                                     |
|---------------------------------------------------------------------|
| **Demo 4 --- Thay đổi BPM real-time**                               |
| Mô phỏng: Gửi message vào tempo.control queue từ Dashboard.         |
| Kết quả nghe thấy: Toàn bộ giàn nhạc tăng/giảm tốc ngay lập tức.    |
| Khái niệm học được: Dynamic configuration, broadcast event pattern. |

|                                                                                        |
|----------------------------------------------------------------------------------------|
| **Demo 5 --- IoT device ngắt kết nối & tự reconnect**                                  |
| Mô phỏng: Ngắt WiFi của ESP32 rồi kết nối lại.                                         |
| Kết quả nghe thấy: Âm thanh dừng, message tích lũy trong queue, khi reconnect phát bù. |
| Khái niệm học được: Message persistence, client reconnect strategy, durable queue.     |

**7. Cấu trúc thư mục dự án**

|                    |                              |
|--------------------|------------------------------|
| **Đường dẫn**      | **Mô tả**                    |
| docker-compose.yml | Định nghĩa toàn bộ services  |
| conductor/         | Conductor Service --- Python |
| services/violin/   | Violin Instrument Service    |
| services/piano/    | Piano Instrument Service     |
| services/drums/    | Drums Instrument Service     |
| services/cello/    | Cello Instrument Service     |
| mixer/             | Mixer Service                |
| dashboard/         | Dashboard web app            |
| iot-device/        | Firmware cho ESP32           |
| scores/            | File nhạc MIDI (.mid) mẫu    |
| docs/              | Tài liệu kỹ thuật chi tiết   |

**8. Yêu cầu phi chức năng**

**8.1 Hiệu năng**

- Độ trễ từ Conductor publish đến IoT phát âm: \< 200ms trong điều kiện LAN bình thường

- RabbitMQ phải xử lý được tối thiểu 100 message/giây

- Dashboard cập nhật metrics mỗi 1 giây

**8.2 Độ tin cậy**

- Tất cả queue phải được khai báo durable --- message không mất khi RabbitMQ restart

- Mỗi service phải có cơ chế tự reconnect khi mất kết nối đến RabbitMQ

- IoT device phải có cơ chế tự reconnect WiFi và AMQP

**8.3 Quan sát được (Observability)**

- Dashboard hiển thị real-time: queue depth, consumer count, message rate của từng queue

- Mỗi service phải log trạng thái kết nối và số message đã xử lý

- RabbitMQ Management UI phải truy cập được tại cổng 15672

**9. Gợi ý lộ trình thực hiện**

|               |               |                                                                                                |
|---------------|---------------|------------------------------------------------------------------------------------------------|
| **Giai đoạn** | **Thời gian** | **Nội dung**                                                                                   |
| **Phase 1**   | Tuần 1--2     | Setup RabbitMQ, viết Conductor Service, định nghĩa message schema, test publish/consume cơ bản |
| **Phase 2**   | Tuần 3--4     | Viết 4 Instrument Services, Mixer Service, chạy thử bản nhạc đơn giản                          |
| **Phase 3**   | Tuần 5        | Xây dựng Dashboard, tích hợp monitoring, test các kịch bản lỗi                                 |
| **Phase 4**   | Tuần 6        | Setup IoT device, kết nối và test phát âm thanh thật, hoàn thiện demo                          |
| **Phase 5**   | Tuần 7        | Viết tài liệu, quay video demo, chuẩn bị báo cáo                                               |

**10. Tiêu chí đánh giá**

|                                                  |                 |              |
|--------------------------------------------------|-----------------|--------------|
| **Tiêu chí**                                     | **Điểm tối đa** | **Ghi chú**  |
| RabbitMQ hoạt động, các queue được cấu hình đúng | 20              | Bắt buộc     |
| Conductor publish đúng note event theo BPM       | 15              | Bắt buộc     |
| Ít nhất 2 Instrument Services hoạt động độc lập  | 15              | Bắt buộc     |
| IoT device nhận message và phát âm thanh thật    | 20              | Quan trọng   |
| Dashboard hiển thị metrics real-time             | 10              | Khuyến khích |
| Demo được ít nhất 3 kịch bản lỗi có chủ đích     | 15              | Quan trọng   |
| Code sạch, có tài liệu và hướng dẫn chạy         | 5               | Bắt buộc     |

--- Hết tài liệu yêu cầu dự án ---
