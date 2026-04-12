**TAI LIEU YEU CAU DU AN**

**Orchestra Microservices**

Mo phong he thong phan tan bang am nhac (phat truc tiep tren loa may tinh)

|            |                                      |
|------------|--------------------------------------|
| Phien ban: | 1.1                                  |
| Doi tuong: | Sinh vien / Nhom do an mon hoc       |
| Linh vuc:  | He thong phan tan · Message Queue    |

**1. Tong quan du an**

**1.1 Y tuong cot loi**

Du an xay dung mot he thong microservices phan tan, trong do moi service dong vai tro mot nhac cu trong gian hop xuong. Cac service duoc dong bo thong qua RabbitMQ de choi nhac dung nhip va dung thu tu.

Diem dac biet: cac khai niem he thong phan tan duoc "nghe thay" truc tiep qua am thanh tren loa may tinh: consumer lag lam nhac bi tre, service chet khien mot nhac cu im lang, thong luong tang cao gay meo nhip.

**1.2 Bang metaphor - Am nhac vs Distributed Systems**

|                             |                                           |
|-----------------------------|-------------------------------------------|
| **Am nhac**                 | **He thong phan tan**                     |
| Gian hop xuong              | Toan bo he thong microservices            |
| Nhac truong (Conductor)     | Conductor Service - dieu phoi trung tam   |
| Nhac cu (Guitar, Oboe...)   | Microservice doc lap                      |
| Ban nhac (Sheet music)      | Message schema / Event contract           |
| Nhip do (Tempo / BPM)       | Message rate / Throughput                 |
| Lac nhip (Out of sync)      | Consumer lag, Race condition              |
| Nhac cu im lang dot ngot    | Service crash / Circuit breaker           |
| Nhac cu moi gia nhap        | Dynamic service discovery                 |

**2. Kien truc he thong**

**2.1 Tong quan kien truc**

He thong duoc thiet ke theo huong toi gian chi phi phu hop voi sinh vien: logic microservices co the chay tren mot hoac nhieu may tinh local trong LAN (moi may co the chay 1 service hoac nhieu service) qua Docker Compose. Am thanh duoc render tai dashboard backend va phat tren loa may tinh.

|                                                                                       |
|---------------------------------------------------------------------------------------|
| **Nguyen tac thiet ke**                                                               |
| • Toan bo microservices chay local - khong can thue server                            |
| • Ho tro mo hinh da may local trong LAN: 1 may/1 service hoac 1 may/nhieu service    |
| • Khong phu thuoc phan cung IoT                                                       |
| • Moi tinh nang phan tan van duoc demo day du va nghe thay ro rang                    |

**2.2 Hai tang he thong**

**Tang 1 - Docker Compose (Cum may local hoac mot laptop)**

Cac services chay trong container Docker:

- RabbitMQ Broker: single node, bat Management UI tai cong 15672 de quan sat queue real-time.
- Conductor Service: doc file MIDI (.mid), publish note event vao dung queue theo BPM.
- Instrument Services (Guitar, Oboe, Drums, Bass): moi service la mot consumer doc lap.
- Mixer Service: tong hop output tu cac nhac cu, publish vao `playback.output`.
- Dashboard: hien thi consumer lag, queue depth, BPM, trang thai service va phat audio local.

**Tang 2 - Local Playback (Desktop/Web)**

- Dashboard backend render audio tu MIDI/output event.
- Dashboard frontend phat WAV qua audio player tren may tinh.

**3. Dac ta cac services**

**3.1 Conductor Service**

Service trung tam, chiu trach nhiem dieu phoi toan bo ban nhac.

- Doc file nhac dinh dang MIDI (.mid) lam dau vao chuan.
- Parse ra danh sach note event co timestamp theo BPM.
- Publish tung note vao dung exchange/queue cua nhac cu tuong ung.
- Ho tro thay doi BPM real-time qua queue `tempo.control`.
- Publish heartbeat event dinh ky de cac service dong bo nhip.

**3.2 Instrument Services**

Moi nhac cu la mot service doc lap, chay trong Docker container rieng.

|             |                       |                                |
|-------------|-----------------------|--------------------------------|
| **Service** | **Queue subscribe**   | **Hanh dong**                  |
| Guitar      | instrument.guitar.note| Phat giai dieu chinh (melody)  |
| Oboe        | instrument.oboe.note  | Phat be doi thoai              |
| Drums       | instrument.drums.beat | Giu nhip (rhythm)              |
| Bass        | instrument.bass.note  | Phat be tram (bass line)       |

**3.3 Mixer Service**

Nhan output tu tat ca instrument services, tong hop va publish vao queue `playback.output`.

**3.4 Dashboard Service**

Giao dien web hien thi real-time cac chi so: consumer lag cua tung queue, so note da xu ly, latency giua beat duoc len lich va beat thuc te, trang thai health cua tung service.

**3.5 Local Audio Playback**

Dashboard backend nhan luong playback va render WAV bang soundfont + fluidsynth. Audio duoc phat tren loa may tinh thong qua dashboard web.

**4. Message schema**

**4.1 Note Event**

Format JSON duoc publish vao queue cua tung nhac cu:

|                |                  |                                       |
|----------------|------------------|---------------------------------------|
| **Truong**     | **Kieu du lieu** | **Mo ta**                             |
| **note_id**    | string (UUID)    | Dinh danh duy nhat cua note           |
| **instrument** | string           | Ten nhac cu: guitar, oboe, drums, bass |
| **pitch**      | integer (0--127) | Gia tri MIDI pitch (60 = C4)          |
| **duration**   | float (giay)     | Thoi gian giu not                     |
| **volume**     | integer (0--127) | Do to (MIDI velocity)                 |
| **beat_time**  | float (giay)     | Thoi diem du kien phat theo BPM       |
| **timestamp**  | ISO 8601         | Thoi diem Conductor publish message   |

**4.2 RabbitMQ Exchange & Queue**

- Exchange type: Topic exchange, ten: `orchestra.events`.
- Routing key pattern: `instrument.<name>.note` hoac `instrument.<name>.beat`.
- Queue `playback.output`: nhan tong hop tu Mixer, dashboard backend subscribe/render local.
- Queue `tempo.control`: Conductor lang nghe lenh thay doi BPM tu Dashboard.

**5. Stack cong nghe**

|                      |                                                   |
|----------------------|---------------------------------------------------|
| **Thanh phan**       | **Cong nghe**                                     |
| Message broker       | RabbitMQ 3.x - Management UI                      |
| Microservices        | Python 3.11+ voi thu vien pika                    |
| Am thanh (software)  | Dashboard backend render WAV + web audio player   |
| Container hoa        | Docker & Docker Compose                           |
| Dashboard            | FastAPI + WebSocket + Next.js                     |
| File nhac dau vao    | MIDI (.mid)                                       |
| Monitoring           | RabbitMQ Management API + Prometheus (tuy chon)   |

**6. Kich ban demo**

|                                                                                 |
|---------------------------------------------------------------------------------|
| **Demo 1 - Consumer lag gay lac nhip**                                          |
| Mo phong: Lam cham nhan tao mot Instrument service (sleep delay).               |
| Ket qua nghe thay: Nhac cu do bi tre dan, queue tich luy, toan ban nhac bi meo. |

|                                                                                    |
|------------------------------------------------------------------------------------|
| **Demo 2 - Service crash & recovery**                                              |
| Mo phong: Dung (docker stop) mot Instrument service giua chung.                    |
| Ket qua nghe thay: Nhac cu do im lang; khoi dong lai thi message don ve.           |

|                                                                                |
|--------------------------------------------------------------------------------|
| **Demo 3 - Scale horizontal (competing consumers)**                          |
| Mo phong: Chay 3 instance cua Guitar service cung luc.                        |
| Ket qua nghe thay: Moi instance chi nhan mot phan note, am thanh bi roi rac. |

|                                                                     |
|---------------------------------------------------------------------|
| **Demo 4 - Thay doi BPM real-time**                                 |
| Mo phong: Gui message vao queue `tempo.control` tu Dashboard.       |
| Ket qua nghe thay: Toan bo gian nhac tang/giam toc ngay lap tuc.    |

**7. Cau truc thu muc du an**

|                  |                             |
|------------------|-----------------------------|
| **Duong dan**    | **Mo ta**                   |
| docker-compose.yml | Dinh nghia toan bo services |
| conductor/       | Conductor Service - Python  |
| services/guitar/ | Guitar Instrument Service   |
| services/oboe/   | Oboe Instrument Service     |
| services/drums/  | Drums Instrument Service    |
| services/bass/   | Bass Instrument Service     |
| mixer/           | Mixer Service               |
| dashboard/       | Dashboard web app           |
| scores/          | File nhac MIDI mau          |
| docs/            | Tai lieu ky thuat           |

**8. Yeu cau phi chuc nang**

**8.1 Hieu nang**

- Do tre tu Conductor publish den dashboard playback: < 200ms trong dieu kien LAN binh thuong.
- RabbitMQ phai xu ly duoc toi thieu 100 message/giay.
- Dashboard cap nhat metrics moi 1 giay.

**8.2 Do tin cay**

- Tat ca queue phai duoc khai bao durable.
- Moi service phai co co che tu reconnect khi mat ket noi den RabbitMQ.

**8.3 Quan sat duoc (Observability)**

- Dashboard hien thi real-time: queue depth, consumer count, message rate cua tung queue.
- Moi service log trang thai ket noi va so message da xu ly.
- RabbitMQ Management UI phai truy cap duoc tai cong 15672.

**9. Goi y lo trinh thuc hien**

|               |               |                                                                                               |
|---------------|---------------|-----------------------------------------------------------------------------------------------|
| **Giai doan** | **Thoi gian** | **Noi dung**                                                                                  |
| **Phase 1**   | Tuan 1--2     | Setup RabbitMQ, viet Conductor Service, dinh nghia message schema, test publish/consume co ban |
| **Phase 2**   | Tuan 3--4     | Viet 4 Instrument Services, Mixer Service, chay thu ban nhac don gian                        |
| **Phase 3**   | Tuan 5        | Xay dung Dashboard, tich hop monitoring, test cac kich ban loi                               |
| **Phase 4**   | Tuan 6        | Toi uu local playback, hoan thien demo                                                       |
| **Phase 5**   | Tuan 7        | Viet tai lieu, quay video demo, chuan bi bao cao                                             |

**10. Tieu chi danh gia**

|                                                |                 |              |
|------------------------------------------------|-----------------|--------------|
| **Tieu chi**                                   | **Diem toi da** | **Ghi chu**  |
| RabbitMQ hoat dong, cac queue duoc cau hinh dung | 20              | Bat buoc     |
| Conductor publish dung note event theo BPM     | 15              | Bat buoc     |
| It nhat 2 Instrument Services hoat dong doc lap| 15              | Bat buoc     |
| Local playback phat dung am thanh theo message | 20              | Quan trong   |
| Dashboard hien thi metrics real-time           | 10              | Khuyen khich |
| Demo duoc it nhat 3 kich ban loi co chu dich   | 15              | Quan trong   |
| Code sach, co tai lieu va huong dan chay       | 5               | Bat buoc     |

--- Het tai lieu yeu cau du an ---
