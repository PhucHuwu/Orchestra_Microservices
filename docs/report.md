# HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG

# KHOA CÔNG NGHỆ THÔNG TIN I

# BÁO CÁO BÀI TẬP LỚN

# MÔN CÁC HỆ THỐNG PHÂN TÁN

## ĐỀ TÀI

**MÔ PHỎNG DÀN NHẠC CÔNG-XÉC-TÔ BẰNG HỆ THỐNG PHÂN TÁN VÀ BẢN ĐIỆN TỬ HÓA ESP - BUZZER - CÔNG TẮC**

| Nội dung | Thông tin |
|---|---|
| Nhóm lớp | 05 |
| Nhóm bài tập lớn | 04 |
| Giảng viên hướng dẫn | PGS.TS. Đỗ Trung Tuấn |
| Sinh viên thực hiện | Trần Hữu Phúc - B22DCCN634; Bùi Ngọc Vũ - B22DCCN910; Lương Tuấn Anh - B22DCCN021; Lương Tiến Đạt - B22DCCN190; Hoàng Minh Tuấn - B22DCCN753 |
| Địa điểm - thời gian | Hà Nội, 2026 |

---

## LỜI CẢM ƠN

Nhóm tác giả xin trân trọng gửi lời cảm ơn sâu sắc đến PGS.TS. Đỗ Trung Tuấn, người đã trực tiếp định hướng chuyên môn, góp ý phương pháp nghiên cứu và hỗ trợ nhóm trong suốt quá trình triển khai đề tài. Các góp ý của thầy không chỉ tập trung vào khía cạnh kỹ thuật của học phần Hệ thống phân tán, mà còn nhấn mạnh yêu cầu khoa học trong cách đặt vấn đề, tổ chức thí nghiệm, diễn giải kết quả và chuẩn hóa văn phong báo cáo.

Nhóm cũng xin gửi lời cảm ơn đến Khoa Công nghệ Thông tin I, Học viện Công nghệ Bưu chính Viễn thông đã tạo điều kiện thuận lợi về môi trường học thuật, trang thiết bị, nguồn tài liệu và cơ hội trao đổi chuyên môn để nhóm hoàn thiện đề tài. Sự hỗ trợ về học liệu và khuôn khổ đánh giá của khoa đã giúp nhóm triển khai đề tài theo hướng liên ngành, kết hợp tư duy hệ thống phân tán với tư duy mô phỏng âm nhạc.

Cuối cùng, nhóm xin cảm ơn các bạn học cùng lớp đã đóng góp nhận xét trong các buổi trình bày thử nghiệm, giúp nhóm điều chỉnh nội dung báo cáo theo hướng rõ ràng, mạch lạc và sát mục tiêu đào tạo.

---

## BẢNG PHÂN CÔNG CÔNG VIỆC

| STT | Thành viên | Nội dung phụ trách | Sản phẩm chính | Mức độ hoàn thành |
|---|---|---|---|---|
| 1 | Trần Hữu Phúc | Điều phối tổng thể đề tài, tích hợp nội dung, kiểm soát tiến độ | Khung kiến trúc, kế hoạch thực nghiệm, rà soát bản thảo | Hoàn thành |
| 2 | Bùi Ngọc Vũ | Thiết kế bản điện tử hóa, kiểm thử kết nối ESP - buzzer - công tắc | Sơ đồ kết nối, tiêu chí kiểm thử phần cứng mô phỏng | Hoàn thành |
| 3 | Lương Tuấn Anh | Xây dựng cơ sở lý luận nhạc lý và mô hình công-xéc-tô | Chương kiến thức nền âm nhạc, bảng đối sánh khái niệm | Hoàn thành |
| 4 | Lương Tiến Đạt | Xây dựng chỉ số quan sát, tổng hợp kết quả thực nghiệm | Bảng đo, ma trận đánh giá, phân tích kết quả | Hoàn thành |
| 5 | Hoàng Minh Tuấn | Chuẩn hóa hình thức báo cáo khoa học, hiệu đính văn phong | Bố cục hoàn chỉnh, danh mục hình bảng, tài liệu tham khảo | Hoàn thành |

---

## NHẬN XÉT TÓM TẮT VỀ ĐÓNG GÓP CỦA NHÓM

Nhóm thực hiện đề tài theo hướng cộng tác phân vai rõ ràng, trong đó phần bản điện tử hóa được xem là hạt nhân của toàn bộ nghiên cứu. Cấu trúc làm việc được tổ chức thành ba lớp: lớp cơ sở lý luận, lớp thiết kế mô phỏng, lớp thực nghiệm đánh giá. Cách tiếp cận này giúp tránh tình trạng báo cáo chỉ thiên về mô tả ý tưởng chung, đồng thời bảo đảm mỗi phần đều có căn cứ kỹ thuật và giá trị minh họa cụ thể.

---

## DANH SÁCH TỪ VIẾT TẮT

| Từ viết tắt | Cụm từ | Ý nghĩa trong báo cáo |
|---|---|---|
| ESP | Bộ điều khiển vi mạch ESP | Bộ điều phối trung tâm của bản điện tử hóa |
| BPM | Nhịp trên phút | Chỉ số tốc độ của bản nhạc mô phỏng |
| MQ | Hàng đợi thông điệp | Cơ chế truyền sự kiện giữa các thành phần |
| API | Giao diện lập trình ứng dụng | Kênh điều khiển trạng thái và truy vấn số liệu |
| LAN | Mạng cục bộ | Môi trường triển khai phân tán nhiều nút máy |
| DLQ | Hàng đợi lỗi | Hàng đợi tiếp nhận thông điệp không xử lý được |
| NFR | Yêu cầu phi chức năng | Nhóm yêu cầu về hiệu năng, tin cậy, quan sát |
| KPI | Chỉ số hiệu quả chính | Chỉ số đánh giá mức hoàn thành mục tiêu mô phỏng |

---

## DANH SÁCH HÌNH ẢNH, BẢNG BIỂU

### Danh sách hình ảnh

- Hình 1: Bức tranh tổng thể đề tài mô phỏng dàn nhạc phân tán
- Hình 2: Mô hình phân vai 5 nút máy trong mạng cục bộ
- Hình 3: Sơ đồ khối bản điện tử hóa trọng tâm
- Hình 4: Sơ đồ kết nối 4 buzzer vào các cổng D2, D16, D19, D23
- Hình 5: Sơ đồ ánh xạ 4 công tắc với 4 nhạc cụ mô phỏng
- Hình 6: Luồng điều phối từ nhạc trưởng tới các nhạc cụ
- Hình 7: Trạng thái hệ khi tất cả công tắc ở chế độ hoạt động
- Hình 8: Trạng thái hệ khi một công tắc bị ngắt
- Hình 9: Trạng thái hệ khi hai công tắc bị ngắt đồng thời
- Hình 10: Trạng thái hệ khi phục hồi lại toàn bộ công tắc
- Hình 11: Biểu đồ biến thiên độ trễ theo mức tải
- Hình 12: Biểu đồ thay đổi độ đầy hòa tấu theo số nhạc cụ bị ngắt
- Hình 13: Giao diện quan sát trạng thái dịch vụ theo thời gian thực
- Hình 14: Quy trình thực nghiệm và thu thập dữ liệu
- Hình 15: Lộ trình phát triển mở rộng bản điện tử hóa

### Danh sách bảng biểu

- Bảng 1: Đối sánh khái niệm âm nhạc và hệ thống phân tán
- Bảng 2: Phân loại hiện tượng phân tán và biểu hiện âm học
- Bảng 3: Thành phần chức năng trong mô hình tổng thể
- Bảng 4: Thông số kỹ thuật bản điện tử hóa
- Bảng 5: Ma trận ánh xạ buzzer - nhạc cụ - công tắc
- Bảng 6: Kịch bản thực nghiệm trọng tâm
- Bảng 7: Bộ chỉ số quan sát định tính và định lượng
- Bảng 8: Kết quả thực nghiệm theo từng kịch bản
- Bảng 9: Đối chiếu mục tiêu và kết quả đạt được
- Bảng 10: Kết quả chưa đạt và phương án cải tiến

---

## LỜI MỞ ĐẦU

### 1. Bối cảnh và lý do chọn đề tài

Hệ thống phân tán là một trong những lĩnh vực cốt lõi của khoa học máy tính hiện đại, nhưng cũng là lĩnh vực gây nhiều khó khăn trong giảng dạy và tiếp thu do mức độ trừu tượng cao. Các khái niệm như đồng bộ, trễ thông điệp, tắc nghẽn hàng đợi, suy giảm dịch vụ cục bộ hay phục hồi sau lỗi thường được trình bày thông qua sơ đồ và chỉ số, trong khi người học thiếu một cơ chế cảm nhận trực quan về tác động thực tế của các hiện tượng này.

Từ thực tế đó, đề tài lựa chọn hướng tiếp cận liên ngành: dùng mô hình dàn nhạc công-xéc-tô để ánh xạ hệ thống phân tán. Điểm nhấn của đề tài không chỉ nằm ở mô hình lý thuyết, mà ở **bản điện tử hóa** có thể thao tác trực tiếp: 1 ESP, 4 buzzer, 4 công tắc, trong đó 4 buzzer kết nối qua cổng D2, D16, D19, D23. Mỗi thao tác bật/tắt công tắc tương ứng với trạng thái hoạt động hoặc ngắt kết nối của một thành phần dịch vụ, từ đó giúp người học “nghe thấy” sự thay đổi của hệ thống.

### 2. Mục tiêu nghiên cứu

Đề tài hướng đến ba mục tiêu chính:

1. Xây dựng mô hình mô phỏng hệ thống phân tán theo phép ẩn dụ dàn nhạc công-xéc-tô, bảo đảm tính học thuật và tính trực quan.
2. Thiết kế bản điện tử hóa làm trọng tâm trình diễn, có thể tái hiện trạng thái bình thường, trạng thái lỗi cục bộ và trạng thái phục hồi.
3. Thiết lập quy trình thực nghiệm có chỉ số quan sát rõ ràng, đối chiếu giữa số liệu kỹ thuật và cảm nhận âm học.

### 3. Đối tượng và phạm vi nghiên cứu

Đối tượng nghiên cứu là mô hình mô phỏng phân tán phục vụ học tập, không phải hệ thống sản xuất thương mại. Phạm vi đề tài tập trung vào:

- Kiến thức nền hệ thống phân tán và nhạc lý;
- Thiết kế kiến trúc mô phỏng;
- Thiết kế và đánh giá bản điện tử hóa trọng tâm;
- Kịch bản thực nghiệm trong môi trường mạng cục bộ.

Đề tài không đi sâu vào triển khai thương mại, không đặt trọng tâm vào tối ưu hạ tầng quy mô lớn, và không thay thế các hệ âm thanh chuyên nghiệp trong trình diễn nghệ thuật.

### 4. Phương pháp nghiên cứu

Đề tài áp dụng phương pháp kết hợp:

- Phân tích tài liệu hệ thống và tài liệu yêu cầu;
- Mô hình hóa khái niệm liên ngành âm nhạc - phân tán;
- Thiết kế thực nghiệm có kiểm soát kịch bản;
- Đánh giá theo bộ chỉ số định tính và định lượng.

### 5. Đóng góp chính của đề tài

Đóng góp quan trọng nhất của đề tài là đề xuất và hiện thực hóa một **học cụ mô phỏng** có khả năng chuyển tải các hiện tượng phân tán bằng tín hiệu âm học trên bản điện tử hóa. Cách tiếp cận này giúp rút ngắn khoảng cách giữa mô hình lý thuyết và cảm nhận thực hành, phù hợp với định hướng đào tạo dựa trên thực nghiệm.

### 6. Cấu trúc báo cáo

Báo cáo gồm bốn chương chính:

- Chương 1: Kiến thức nền về hệ thống phân tán, nhạc lý và công-xéc-tô;
- Chương 2: Phân tích thiết kế hệ thống, nhấn mạnh thiết kế bản điện tử hóa;
- Chương 3: Thực nghiệm, kịch bản đánh giá và kết quả;
- Chương 4: Kết luận, kết quả đạt được, hạn chế và định hướng phát triển.

---

## CHƯƠNG 1. KIẾN THỨC NỀN

Chương này trình bày:

- Bản chất, đặc trưng và các thách thức điển hình của hệ thống phân tán.
- Cơ sở nhạc lý và mô hình công-xéc-tô phục vụ ánh xạ tư duy hệ thống.
- Nền tảng của cơ chế hàng đợi thông điệp và vai trò trong mô phỏng.
- Luận cứ khoa học cho bản điện tử hóa ESP - buzzer - công tắc làm trọng tâm đề tài.
- Các bảng đối sánh giữa hiện tượng kỹ thuật và biểu hiện âm học.

### 1.1. Khái niệm và bản chất của hệ thống phân tán

Hệ thống phân tán được hiểu là một cấu trúc gồm nhiều thành phần tính toán độc lập, triển khai trên các nút khác nhau, liên lạc qua mạng để cùng cung cấp một dịch vụ có ý nghĩa thống nhất. Điểm mấu chốt của hệ phân tán không nằm ở số lượng thành phần, mà nằm ở yêu cầu phối hợp giữa các thành phần trong điều kiện truyền thông không tuyệt đối ổn định.

Về bản chất, một hệ phân tán luôn đối mặt với bài toán cân bằng giữa ba yêu cầu: tính đúng đắn chức năng, tính kịp thời phản hồi và khả năng duy trì dịch vụ khi xảy ra lỗi cục bộ. Chính vì vậy, người thiết kế hệ phân tán phải tư duy theo hướng toàn hệ, thay vì tối ưu đơn lẻ từng thành phần.

Các đặc trưng nền tảng có thể khái quát như sau:

- **Tính đồng thời:** nhiều luồng xử lý diễn ra song song, tạo hiệu quả cao nhưng làm tăng độ phức tạp điều phối;
- **Không có đồng hồ toàn cục tuyệt đối:** thứ tự thời gian quan sát ở mỗi nút có thể khác nhau;
- **Lỗi là trạng thái bình thường:** thành phần có thể ngắt kết nối, quá tải hoặc tạm dừng bất kỳ thời điểm nào;
- **Mạng là kênh phối hợp bắt buộc:** mọi trao đổi chịu ảnh hưởng của trễ, dao động trễ và mất gói;
- **Tính mở rộng:** hệ cần hỗ trợ tăng thành phần mà không phá vỡ cấu trúc vận hành nền;
- **Tính quan sát được:** bắt buộc phải có cơ chế theo dõi trạng thái để phát hiện sai lệch sớm.

Trong bối cảnh đào tạo, khó khăn lớn nhất là sinh viên thường hiểu định nghĩa nhưng khó hình dung diễn biến động của hệ khi thành phần thay đổi trạng thái. Vì lý do này, cách tiếp cận mô phỏng trực quan bằng âm học được xem là phù hợp, vì nó biến trạng thái kỹ thuật thành tín hiệu có thể cảm nhận ngay lập tức.

### 1.2. Các thách thức điển hình trong hệ thống phân tán

#### 1.2.1. Độ trễ và dao động độ trễ

Trong hệ phân tán, độ trễ không phải một hằng số mà là một đại lượng biến thiên theo tải hệ thống, tải mạng và độ sâu hàng đợi. Một hệ có thể phản hồi tốt ở trạng thái tải thấp, nhưng suy giảm nhanh khi tăng tải hoặc khi một nút xử lý chậm bất thường. Dao động độ trễ làm cho việc đánh giá “nhanh” hay “chậm” không thể chỉ dựa trên một mẫu đo đơn lẻ, mà cần quan sát theo chuỗi thời gian.

Đối với đề tài, độ trễ được cảm nhận gián tiếp qua mức “chậm pha” của các bè âm mô phỏng. Khi dao động trễ tăng, người nghe có thể nhận thấy nhịp tổng thiếu chắc chắn, tạo cảm giác rời rạc trong hòa tấu.

#### 1.2.2. Mất đồng bộ

Mất đồng bộ là hiện tượng các thành phần không còn bám cùng một nhịp xử lý chung, dẫn đến sai lệch thời điểm hoàn tất tác vụ. Trong môi trường phân tán, mất đồng bộ có thể xuất phát từ khác biệt năng lực xử lý giữa các nút, khác biệt trạng thái hàng đợi, hoặc thay đổi đột ngột của tải vào.

Mất đồng bộ đặc biệt nguy hiểm với các hệ cần phối hợp theo chu kỳ, bởi một thành phần chậm có thể làm méo chất lượng đầu ra toàn hệ. Theo mô hình âm nhạc, đây là trạng thái “lệch nhịp”, khi từng bè âm không còn hòa khít với nhau.

#### 1.2.3. Tắc nghẽn hàng đợi

Tắc nghẽn hàng đợi xảy ra khi tốc độ tiếp nhận thông điệp cao hơn tốc độ xử lý trong một khoảng thời gian đủ dài. Khi đó, độ sâu hàng đợi tăng, kéo theo tăng thời gian chờ và tăng sai lệch cảm nhận về thứ tự xử lý. Nếu không có cơ chế điều tiết, tắc nghẽn cục bộ có thể lan thành tắc nghẽn chuỗi.

Về mặt sư phạm, đây là hiện tượng rất khó truyền đạt nếu chỉ trình bày bằng đồ thị. Bản điện tử hóa cho phép mô tả tắc nghẽn theo cách dễ hiểu hơn: hòa tấu mất độ liền mạch, xuất hiện cảm giác “đứt quãng” hoặc “đuổi nhịp”.

#### 1.2.4. Lỗi thành phần và phục hồi

Lỗi thành phần là đặc tính không thể loại bỏ hoàn toàn trong hệ phân tán. Một thành phần có thể dừng hoạt động do quá tải, gián đoạn kết nối hoặc lỗi nội tại, trong khi các thành phần khác vẫn tiếp tục vận hành. Điều này tạo nên bản chất “sống chung với lỗi” của hệ phân tán.

Giá trị thực tế của một hệ không nằm ở việc “không bao giờ lỗi”, mà ở khả năng duy trì dịch vụ chấp nhận được khi lỗi xảy ra và khả năng phục hồi nhanh khi thành phần tái gia nhập. Trong đề tài, trạng thái này được mô phỏng trực tiếp qua thao tác tắt/bật công tắc gắn với từng buzzer, giúp quan sát rõ chu kỳ lỗi - suy giảm - phục hồi.

#### 1.2.5. Tính nhất quán và cảm nhận nhất quán

Một thách thức nền tảng khác là đảm bảo tính nhất quán giữa các thành phần quan sát cùng một trạng thái hệ thống. Trong mô hình học tập, đề tài không đặt mục tiêu tối đa hóa nhất quán theo chuẩn sản xuất, nhưng vẫn yêu cầu tính nhất quán cảm nhận: cùng một thao tác ngắt công tắc phải tạo ra biểu hiện trạng thái tương đồng ở nhiều lần thử nghiệm.

#### 1.2.6. Khả năng quan sát và diễn giải sự cố

Nếu thiếu cơ chế quan sát, lỗi phân tán thường biểu hiện gián tiếp và khó truy nguyên. Vì vậy, hệ thống mô phỏng cần đồng thời hiển thị chỉ số kỹ thuật và tín hiệu âm học. Chỉ số kỹ thuật cho biết “hệ đang ở đâu”, còn âm học cho biết “người dùng cảm nhận chất lượng ra sao”. Hai lớp thông tin này bổ trợ nhau để tăng độ tin cậy trong diễn giải sự cố.

### 1.3. Nền tảng âm nhạc phục vụ mô hình hóa

Để ánh xạ hệ phân tán sang mô hình âm học một cách chặt chẽ, đề tài sử dụng các khái niệm nhạc lý cơ bản làm hệ quy chiếu. Việc dùng nhạc lý không nhằm mục đích trình diễn nghệ thuật, mà nhằm tạo một ngôn ngữ trung gian giúp giải thích các trạng thái kỹ thuật bằng hiện tượng dễ cảm nhận.

#### 1.3.1. Nhịp độ và cấu trúc thời gian

Nhịp độ (BPM) quyết định mật độ diễn tiến của nốt nhạc theo thời gian. Khi chuyển sang mô hình phân tán, BPM đóng vai trò đại diện cho tốc độ phát sinh và luân chuyển sự kiện. Tăng BPM tương ứng tăng áp lực xử lý lên các thành phần; giảm BPM tương ứng giảm tải và tăng khoảng đệm điều phối.

Ở góc độ sư phạm, BPM là tham số cực kỳ hữu ích vì cho phép người học thấy ngay mối quan hệ giữa “tốc độ” và “độ ổn định” của hệ.

#### 1.3.2. Cao độ, trường độ và cường độ

Ba thành tố cơ bản của nốt nhạc gồm cao độ, trường độ và cường độ. Trong đề tài:

- **Cao độ** có thể xem như đặc trưng nhận diện của từng bè;
- **Trường độ** phản ánh độ dài hiệu ứng của một sự kiện;
- **Cường độ** phản ánh mức ưu tiên cảm nhận của thành phần trong tổng thể hòa âm.

Ánh xạ này giúp người học hiểu rằng một sự kiện trong hệ phân tán không chỉ có “xảy ra hay không”, mà còn có thuộc tính về thời lượng và mức ảnh hưởng tới đầu ra chung.

#### 1.3.2. Bè âm và vai trò phối hợp

Mỗi nhạc cụ trong dàn nhạc đảm nhận một bè âm riêng, có thể là bè chính, bè đối thoại, bè giữ nhịp hoặc bè nền trầm. Mặc dù độc lập về vai trò, các bè chỉ tạo giá trị khi phối hợp chính xác theo cùng nhịp tổng.

Trong hệ phân tán, mỗi thành phần cũng đóng vai trò chuyên biệt và chỉ tạo hiệu quả khi phối hợp đúng nhịp, đúng thứ tự logic. Do đó, khái niệm bè âm là một phép tương đồng mạnh để giải thích tư duy “phân vai nhưng đồng bộ”.

#### 1.3.3. Mất bè và suy giảm chất lượng

Khi một nhạc cụ ngừng phát, dàn nhạc không nhất thiết dừng hoàn toàn nhưng chất lượng tổng thể bị suy giảm. Trường hợp mất nhiều bè đồng thời sẽ làm cấu trúc âm học trở nên nghèo nàn, thiếu cân bằng và khó duy trì cảm giác hoàn chỉnh.

Đây là mô hình trực quan cho hiện tượng lỗi cục bộ trong hệ phân tán: hệ còn hoạt động nhưng chất lượng dịch vụ giảm theo số lượng thành phần lỗi.

#### 1.3.4. Hòa âm, hòa tấu và tính toàn vẹn đầu ra

Hòa âm trong âm nhạc tương ứng với tính toàn vẹn của đầu ra trong hệ thống phân tán. Khi mỗi thành phần hoàn thành đúng phần việc và đúng nhịp, đầu ra chung đạt mức “đầy” và “mạch lạc”. Ngược lại, sai lệch thời gian hoặc mất thành phần làm đầu ra mất cân bằng. Vì vậy, hòa âm là một chỉ báo trực quan cho chất lượng phối hợp hệ thống.

### 1.4. Công-xéc-tô như một mô hình tư duy hệ thống

Công-xéc-tô là hình thức tổ chức âm nhạc có mức kỷ luật phối hợp cao, trong đó vai trò nhạc trưởng, từng nhóm nhạc cụ và quy tắc nhịp được xác định rõ. Đặc điểm này khiến công-xéc-tô trở thành mô hình tư duy rất gần với hệ phân tán.

Về cấu trúc vận hành, mô hình công-xéc-tô thể hiện đầy đủ các lớp logic mà hệ phân tán cần có:

- Có trung tâm điều phối (nhạc trưởng);
- Có nhiều thành phần chuyên biệt (nhạc cụ);
- Có quy tắc phối hợp theo thời gian (nhịp);
- Có yêu cầu đồng bộ và phục hồi khi sai lệch.

Ngoài ra, công-xéc-tô còn phản ánh tốt yếu tố “tự chủ có điều kiện”: mỗi nhạc cụ có không gian biểu đạt riêng nhưng không tách rời chỉ huy chung. Đây cũng chính là nguyên lý tổ chức của các thành phần phân tán: tự chủ về xử lý cục bộ, nhưng tuân thủ quy tắc điều phối tổng thể.

Khung tư duy này giúp chuyển các thuật ngữ kỹ thuật khó tiếp cận sang ngôn ngữ trực quan mà vẫn giữ tính chính xác khoa học, đặc biệt phù hợp với mục tiêu đào tạo ở bậc đại học.

### 1.5. Kiến thức nền về mô hình hàng đợi thông điệp

Trong các hệ phân tán hiện đại, hàng đợi thông điệp là cơ chế trung gian quan trọng để tách rời nhịp hoạt động giữa bên phát và bên nhận. Cách tiếp cận này giúp hệ tăng tính mềm dẻo khi tải biến động, đồng thời giảm phụ thuộc trực tiếp giữa các thành phần.

Các lợi ích nền tảng của mô hình hàng đợi gồm:

- Hấp thụ dao động tải ngắn hạn;
- Hỗ trợ xử lý bất đồng bộ;
- Tăng khả năng chịu lỗi cục bộ;
- Cho phép quan sát sâu trạng thái xử lý qua độ sâu hàng đợi.

Trong đề tài, mô hình hàng đợi là lớp nền logic để bản điện tử hóa phản ánh trạng thái hệ thống. Khi trạng thái xử lý thay đổi ở lớp hàng đợi, biểu hiện âm học ở lớp buzzer thay đổi theo.

### 1.6. Cơ sở lý luận cho bản điện tử hóa trọng tâm

Bản điện tử hóa của đề tài được xây dựng trên nguyên tắc: mô phỏng phải tạo ra tín hiệu cảm nhận tức thời khi hệ thay đổi trạng thái.

Mô hình gồm:

- 1 ESP đóng vai trò điều phối trung tâm;
- 4 buzzer đại diện cho 4 nhạc cụ;
- 4 công tắc tương ứng trạng thái kết nối của 4 nhạc cụ;
- Buzzer kết nối qua các cổng D2, D16, D19, D23.

Điểm mạnh của thiết kế này:

- Chi phí triển khai thấp;
- Dễ tái lập trong môi trường lớp học;
- Quan sát tức thời bằng tai và mắt;

- Dễ mở rộng số kịch bản thử nghiệm.

Không gian giá trị của bản điện tử hóa thể hiện ở ba điểm:

1. **Giá trị trực quan:** người học quan sát ngay tác động của thao tác lỗi.
2. **Giá trị lặp lại:** cùng thao tác có thể tạo kết quả tương đồng qua nhiều phiên.
3. **Giá trị liên kết:** kết nối chặt chẽ giữa khái niệm lý thuyết và hiện tượng cảm nhận.

### 1.7. Đối sánh khái niệm âm nhạc - hệ thống phân tán

**Bảng 1. Đối sánh khái niệm âm nhạc và hệ thống phân tán**

| Khái niệm âm nhạc | Khái niệm hệ thống phân tán | Giải thích ngắn |
|---|---|---|
| Dàn nhạc | Toàn bộ hệ thống | Tập hợp các thành phần phối hợp |
| Nhạc trưởng | Thành phần điều phối | Quyết định nhịp và thứ tự tổng thể |
| Nhạc cụ | Thành phần dịch vụ | Xử lý một phần nhiệm vụ chuyên biệt |
| Bản nhạc | Mẫu sự kiện | Khuôn dạng điều phối chung |
| Nhịp | Tốc độ luồng sự kiện | Mức độ nhanh chậm toàn hệ |
| Lệch nhịp | Trễ xử lý | Sai khác thời gian giữa các thành phần |
| Mất bè | Mất thành phần | Suy giảm chất lượng đầu ra |
| Hòa âm | Tổng hợp kết quả | Đầu ra cuối cùng của hệ |

### 1.8. Phân loại hiện tượng phân tán theo biểu hiện âm học

**Bảng 2. Phân loại hiện tượng phân tán và biểu hiện âm học**

| Hiện tượng phân tán | Dấu hiệu kỹ thuật | Biểu hiện âm học trên bản điện tử hóa |
|---|---|---|
| Tăng trễ | Hàng đợi tăng, phản hồi chậm | Nhịp phát rời rạc, cảm giác chậm pha |
| Mất thành phần đơn lẻ | Một dịch vụ không phản hồi | Mất một bè âm rõ rệt |
| Mất nhiều thành phần | Nhiều dịch vụ ngắt | Hòa âm suy giảm mạnh |
| Phục hồi thành phần | Dịch vụ tái gia nhập | Bè âm trở lại từng phần |
| Dao động tải | Chỉ số biến thiên liên tục | Âm hình thiếu ổn định |
| Tái gia nhập thành phần | Thành phần trở lại trạng thái hoạt động | Bè âm quay lại theo từng mức |
| Suy giảm phối hợp kéo dài | Nhiều chỉ số lệch ngưỡng trong thời gian dài | Hòa tấu mất cảm giác hoàn chỉnh |

### 1.9. Ý nghĩa của chương nền đối với phần thực nghiệm

Chương nền có vai trò như khung tham chiếu để đọc đúng kết quả thực nghiệm. Nếu không có nền tảng khái niệm, người quan sát dễ nhầm giữa hiện tượng âm học bề mặt và nguyên nhân kỹ thuật bên trong. Nhờ hệ quy chiếu đã thiết lập, mỗi thay đổi trên bản điện tử hóa có thể được diễn giải theo đúng logic phân tán, từ đó nâng cao chất lượng nhận xét khoa học.

### 1.10. Kết luận chương

Chương 1 đã thiết lập cơ sở lý luận đầy đủ cho đề tài: từ bản chất hệ thống phân tán, thách thức điển hình, đến khung nhạc lý và mô hình công-xéc-tô. Trên nền tảng đó, bản điện tử hóa ESP - buzzer - công tắc được chứng minh là phương tiện mô phỏng có tính khoa học, trực quan và phù hợp mục tiêu đào tạo.

---

## CHƯƠNG 2. PHÂN TÍCH THIẾT KẾ HỆ THỐNG

Chương này trình bày:

- Phát biểu bài toán thiết kế theo mục tiêu đào tạo học phần hệ thống phân tán.
- Hệ mục tiêu thiết kế gồm mục tiêu chức năng, mục tiêu sư phạm và mục tiêu vận hành.
- Kiến trúc tổng thể theo lớp, cùng cơ chế liên kết giữa lớp logic và lớp điện tử hóa.
- Thiết kế chi tiết bản điện tử hóa trọng tâm với kết nối D2, D16, D19, D23.
- Luồng chức năng, luồng vận hành học tập, bộ chỉ số quan sát và thang đánh giá.
- Tiêu chí chất lượng thiết kế, phân tích rủi ro và giá trị sư phạm của mô hình.

### 2.1. Phát biểu bài toán

Trong đào tạo hệ thống phân tán, khó khăn lớn không nằm ở việc giới thiệu thuật ngữ mà nằm ở việc giúp người học hiểu đúng cơ chế vận hành khi hệ thống chịu tác động động theo thời gian thực. Nếu chỉ dùng sơ đồ tĩnh hoặc mô tả lý thuyết, người học thường khó nhận ra mối quan hệ nhân - quả giữa sự cố cục bộ và biến đổi chất lượng đầu ra toàn hệ.

Từ đó, bài toán của đề tài được phát biểu như sau: xây dựng một mô hình mô phỏng có khả năng biểu đạt trung thực các hiện tượng phân tán cốt lõi, cho phép thao tác trạng thái lỗi một cách có kiểm soát, đồng thời cung cấp phản hồi trực quan tức thời để người học dễ liên hệ giữa trạng thái kỹ thuật và cảm nhận kết quả.

Các ràng buộc thiết kế chính gồm:

- Môi trường triển khai chủ yếu là lớp học và phòng thực hành;
- Nguồn lực phần cứng và kinh phí có giới hạn;
- Mô hình phải dễ lắp ráp, dễ lặp lại và dễ bảo trì;
- Nội dung phải bám sát mục tiêu học phần Các hệ thống phân tán;
- Bản điện tử hóa phải là trọng tâm biểu diễn, không phải phần phụ minh họa;
- Hệ thống cần hỗ trợ trình bày đồng thời hai lớp thông tin: trạng thái kỹ thuật và biểu hiện âm học.

Từ góc nhìn thiết kế giáo dục, bài toán không yêu cầu mô hình đạt mức phức tạp sản xuất, mà yêu cầu đạt mức rõ ràng học thuật, dễ diễn giải và có tính thực nghiệm cao.

### 2.2. Mục tiêu thiết kế

Mục tiêu thiết kế được chia thành ba lớp: mục tiêu chức năng mô phỏng, mục tiêu sư phạm và mục tiêu vận hành.

#### 2.2.1. Mục tiêu chức năng mô phỏng

Ở lớp chức năng, mô hình phải phản ánh được đúng tinh thần của một hệ thống phân tán theo chuỗi: điều phối trung tâm phát nhịp tổng, các thành phần chuyên biệt xử lý theo vai trò, sau đó đầu ra được hợp thành ở mức toàn hệ. Yêu cầu cốt lõi không phải là tái hiện mọi chi tiết kỹ thuật phức tạp, mà là tái hiện đúng quan hệ phụ thuộc giữa các vai trò trong hệ.

Mô hình cũng phải thể hiện được ba trạng thái quan trọng của hệ phân tán: vận hành ổn định, suy giảm do lỗi cục bộ và phục hồi sau tái gia nhập. Khi một thành phần bị ngắt, hệ vẫn tiếp tục nhưng chất lượng đầu ra giảm; khi thành phần quay lại, hệ cần thể hiện tiến trình trở về trạng thái cân bằng. Đây là điều kiện bắt buộc để đảm bảo mô hình có giá trị học thuật, thay vì chỉ mang tính minh họa trình diễn.

Ngoài ra, mỗi thao tác tác động phải sinh ra phản hồi có thể quan sát tức thời. Nếu thao tác và phản hồi không liên hệ rõ ràng, sinh viên khó hình thành tư duy nguyên nhân - hệ quả, từ đó giảm hiệu quả của toàn bộ bài thực hành.

#### 2.2.2. Mục tiêu sư phạm

Về phương diện sư phạm, mô hình cần hỗ trợ người học nhận diện hiện tượng phân tán trong thời gian ngắn thông qua trải nghiệm nghe - nhìn. Trọng tâm không phải là ghi nhớ định nghĩa, mà là nhận ra sự thay đổi hệ thống khi trạng thái thành phần thay đổi.

Mô hình cần tạo điều kiện để sinh viên tự đặt câu hỏi phân tích: vì sao một thao tác ngắt cục bộ lại làm thay đổi hòa tấu tổng, vì sao phục hồi thành phần không đồng nghĩa phục hồi chất lượng ngay lập tức, và vì sao chỉ số kỹ thuật phải được đọc cùng dữ liệu cảm nhận. Khi người học tự suy luận theo chuỗi này, mức độ nắm kiến thức sẽ bền vững hơn so với hình thức tiếp nhận thụ động.

Đối với giảng viên, mô hình phải đủ chuẩn hóa để tổ chức được các bài thực hành lặp lại theo kịch bản, có tiêu chí đánh giá rõ ràng theo năng lực quan sát, năng lực diễn giải và năng lực tổng hợp kết luận.

#### 2.2.3. Mục tiêu vận hành

Mục tiêu vận hành nhấn mạnh tính thực dụng: mô hình phải có thể triển khai lặp lại trong nhiều buổi học mà không phụ thuộc quá lớn vào người vận hành. Sai khác giữa các phiên cần được kiểm soát ở mức nhỏ để dữ liệu thực nghiệm có thể so sánh.

Quy trình khởi tạo, chạy thử, gây lỗi và khôi phục phải nhất quán, giúp giảm thời gian chuẩn bị trước giờ học và giảm rủi ro sai thao tác khi trình diễn. Đây là điểm rất quan trọng vì trong môi trường lớp học, thời gian thực hành thường ngắn, cần tối đa hóa thời lượng phân tích thay vì xử lý sự cố kỹ thuật.

Cuối cùng, mô hình cần có khả năng mở rộng theo cấp độ học phần: từ bài thực hành nhập môn đến các bài có mức phân tích sâu hơn, bảo đảm giá trị sử dụng lâu dài.

**Bảng 3. Ma trận mục tiêu thiết kế và tiêu chí kiểm chứng**

| Nhóm mục tiêu | Mục tiêu cụ thể | Tiêu chí kiểm chứng |
|---|---|---|
| Chức năng | Mô phỏng đủ chuỗi xử lý phân tán | Quan sát được đầy đủ vai trò điều phối - nhạc cụ - hòa trộn |
| Chức năng | Hỗ trợ lỗi và phục hồi | Ngắt/bật công tắc tạo ra thay đổi trạng thái đúng kỳ vọng |
| Sư phạm | Dễ nhận biết hiện tượng | Người học phân biệt được trạng thái ổn định và suy giảm |
| Sư phạm | Hỗ trợ phân tích hệ thống | Đối chiếu được chỉ số và cảm nhận âm học |
| Vận hành | Tính lặp lại | Kịch bản cho kết quả tương đồng qua nhiều lần chạy |
| Vận hành | Khả năng mở rộng | Có thể bổ sung kịch bản, tăng nhạc cụ mô phỏng |

### 2.3. Kiến trúc tổng thể theo lớp

Kiến trúc của đề tài được tổ chức theo hướng phân lớp để tách biệt trách nhiệm: lớp logic phân tán chịu trách nhiệm xử lý trạng thái hệ thống; lớp điện tử hóa chịu trách nhiệm biểu đạt trực quan cho người học. Cách phân lớp này giúp dễ phân tích, dễ kiểm chứng và dễ nâng cấp.

**Hình 1: Bức tranh tổng thể đề tài mô phỏng dàn nhạc phân tán**

**Hình 2: Mô hình phân vai 5 nút máy trong mạng cục bộ**

#### 2.3.1. Lớp logic phân tán

Lớp logic phân tán là lõi vận hành của mô hình, nơi các trạng thái hệ thống được hình thành và biến đổi theo thời gian. Lớp này bao gồm điều phối trung tâm, các thành phần nhạc cụ mô phỏng, khâu hòa trộn và khâu quan sát. Mỗi khối có vai trò rõ ràng, nhưng giá trị của lớp logic chỉ xuất hiện khi các khối phối hợp đúng theo cùng một nhịp điều phối.

Điều phối trung tâm giữ vai trò xác lập trật tự vận hành; các thành phần nhạc cụ mô phỏng thực hiện xử lý theo chuyên trách; khâu hòa trộn kết hợp tín hiệu riêng thành tín hiệu chung; khâu quan sát cung cấp bằng chứng trạng thái cho phân tích. Nếu thiếu một trong các khối này, mô hình sẽ mất khả năng biểu đạt một phần quan trọng của hệ phân tán.

Đặc điểm của lớp logic:

- Tổ chức theo vai trò chuyên biệt;
- Trao đổi thông điệp theo cấu trúc sự kiện;
- Có khả năng phản ánh trạng thái sống/chết của thành phần;
- Cung cấp dữ liệu quan sát theo thời gian thực.

#### 2.3.2. Lớp điện tử hóa trực quan

Lớp điện tử hóa trực quan là cầu nối giữa dữ liệu kỹ thuật và cảm nhận con người. Thay vì chỉ hiển thị trạng thái bằng số liệu, lớp này chuyển trạng thái thành tín hiệu âm học có thể nghe ngay, qua đó giúp người học nhận ra hiện tượng mà không cần thao tác phân tích phức tạp ở thời điểm đầu.

Vai trò then chốt của lớp này là tính tức thời: khi trạng thái logic thay đổi, biểu hiện âm học phải thay đổi gần như đồng thời. Nhờ vậy, người học hình thành liên hệ trực tiếp giữa thao tác, trạng thái và kết quả.

Đặc điểm của lớp điện tử hóa:

- Mỗi kênh phát âm gắn với một thành phần nhạc cụ mô phỏng;
- Mỗi công tắc đại diện một thao tác ngắt/kết nối thành phần;
- Phản hồi âm học xảy ra tức thời theo trạng thái thao tác;
- Dễ tổ chức trình diễn trước lớp học đông người.

#### 2.3.3. Cơ chế liên kết hai lớp

Hai lớp được liên kết thông qua cơ chế ánh xạ một - một giữa thành phần logic và kênh biểu đạt âm học. Cơ chế này bảo đảm rằng trạng thái ở lớp logic không bị mất nghĩa khi chuyển sang lớp trực quan. Nói cách khác, âm học không phải hiệu ứng trang trí, mà là ảnh chiếu có kiểm chứng của trạng thái kỹ thuật.

Khi một thành phần logic bị ngắt, kênh âm tương ứng phải phản ánh mất tín hiệu. Khi thành phần logic trở lại, kênh âm phải phục hồi theo cùng tiến trình. Nếu quan hệ này không ổn định, mô hình sẽ đánh mất giá trị khoa học vì người học không thể tin cậy mối liên hệ giữa dữ liệu và cảm nhận.

Do đó, cơ chế liên kết hai lớp là điểm trọng yếu để phân biệt mô hình mô phỏng học thuật với mô hình trình diễn cảm tính.

**Bảng 4. Thành phần chức năng trong mô hình tổng thể**

| Nhóm thành phần | Vai trò | Đầu vào | Đầu ra |
|---|---|---|---|
| Điều phối trung tâm | Thiết lập nhịp tổng, phân phát sự kiện | Mẫu bài nhạc, lệnh nhịp | Sự kiện điều phối |
| Nhạc cụ mô phỏng | Xử lý phần việc chuyên biệt | Sự kiện theo nhạc cụ | Tín hiệu thành phần |
| Hòa trộn tổng | Gộp tín hiệu toàn hệ | Tín hiệu từng nhạc cụ | Tín hiệu hòa tấu |
| Quan sát trạng thái | Theo dõi chỉ số và sức khỏe hệ | Dữ liệu vận hành | Bảng chỉ số thời gian thực |
| Bản điện tử hóa | Hiển thị trực quan trạng thái | Trạng thái nhạc cụ | Âm báo và trạng thái công tắc |

### 2.4. Thiết kế bản điện tử hóa trọng tâm

Phần bản điện tử hóa được phát triển theo nguyên tắc “một thành phần logic - một kênh mô phỏng - một thao tác kiểm thử”. Thiết kế này nhằm bảo đảm mọi hiện tượng được tái hiện minh bạch và hạn chế tối đa diễn giải mơ hồ.

#### 2.4.1. Cấu trúc phần tử và ánh xạ vai trò

Mô hình bao gồm:

- 1 bộ điều khiển ESP giữ vai trò nhạc trưởng;
- 4 buzzer giữ vai trò 4 nhạc cụ mô phỏng;
- 4 công tắc giữ vai trò thao tác lỗi/phục hồi;
- 4 cổng tín hiệu D2, D16, D19, D23 ứng với 4 kênh âm học.

**Hình 3: Sơ đồ khối bản điện tử hóa trọng tâm**

**Hình 4: Sơ đồ kết nối 4 buzzer vào các cổng D2, D16, D19, D23**

**Hình 5: Sơ đồ ánh xạ 4 công tắc với 4 nhạc cụ mô phỏng**

Điểm quan trọng của cấu trúc này là tính đối xứng: mỗi nhạc cụ mô phỏng luôn có cặp kênh tín hiệu và công tắc riêng, giúp đánh giá độc lập trước khi đánh giá tương tác liên thành phần. Nhờ cấu trúc đối xứng, người vận hành có thể tiến hành kiểm thử tuần tự theo từng kênh, sau đó mới mở rộng sang kiểm thử đa kênh mà không làm mất dấu nguyên nhân.

Về mặt phương pháp, cấu trúc đối xứng còn giúp chuẩn hóa biên bản thực nghiệm. Mỗi kênh có cùng logic ghi nhận nên dữ liệu dễ so sánh ngang, hạn chế sai lệch do khác biệt cách mô tả giữa các thành viên.

#### 2.4.2. Nguyên tắc thiết kế thao tác

Thiết kế thao tác tuân thủ bốn nguyên tắc:

1. **Tính đơn trị của thao tác:** một thao tác chỉ tác động một trạng thái ưu tiên.
2. **Tính phản hồi tức thời:** trạng thái thay đổi phải quan sát ngay sau thao tác.
3. **Tính khôi phục kiểm soát:** có thể quay lại trạng thái chuẩn theo quy trình ngược.
4. **Tính lặp lại:** cùng thao tác cho cùng xu hướng kết quả qua nhiều phiên.

Bốn nguyên tắc trên bảo đảm rằng mỗi thao tác có giá trị kiểm chứng. Nếu thiếu tính đơn trị, người học không biết thay đổi đến từ thao tác nào. Nếu thiếu phản hồi tức thời, mối liên hệ nguyên nhân - hệ quả bị mờ. Nếu thiếu khả năng khôi phục, mô hình khó chạy nhiều kịch bản trong một buổi. Nếu thiếu tính lặp lại, kết quả khó dùng cho đánh giá học thuật.

#### 2.4.3. Ràng buộc kỹ thuật của bản điện tử hóa

Để bảo đảm độ tin cậy mô phỏng, bản điện tử hóa đặt ra các ràng buộc:

- Kết nối kênh phải ổn định trong suốt phiên thực nghiệm;
- Trạng thái công tắc phải rõ ràng, tránh nhập nhằng giữa bật/tắt;
- Âm báo của từng kênh phải đủ phân biệt khi phát đồng thời;
- Mọi thay đổi phải được ghi nhận vào biểu mẫu quan sát.

Những ràng buộc này nhằm giữ độ tin cậy của dữ liệu thực nghiệm. Trong bài thực hành giáo dục, độ chính xác tuyệt đối không phải mục tiêu duy nhất; tính nhất quán giữa các lần chạy mới là điều kiện để người học rút ra kết luận có giá trị.

**Bảng 5. Thông số kỹ thuật bản điện tử hóa**

| Thành phần | Số lượng | Vai trò mô phỏng | Yêu cầu vận hành |
|---|---:|---|---|
| ESP | 1 | Điều phối trung tâm | Ổn định nguồn, tín hiệu ra nhất quán |
| Buzzer | 4 | 4 nhạc cụ | Phát tín hiệu rõ, dễ phân biệt |
| Công tắc | 4 | Ngắt/kết nối nhạc cụ | Phản hồi đóng/mở dứt khoát |
| Cổng D2 | 1 | Kênh buzzer 1 | Ánh xạ nhạc cụ 1 |
| Cổng D16 | 1 | Kênh buzzer 2 | Ánh xạ nhạc cụ 2 |
| Cổng D19 | 1 | Kênh buzzer 3 | Ánh xạ nhạc cụ 3 |
| Cổng D23 | 1 | Kênh buzzer 4 | Ánh xạ nhạc cụ 4 |

**Bảng 6. Ma trận ánh xạ buzzer - nhạc cụ - công tắc**

| Kênh | Cổng buzzer | Công tắc điều khiển | Vai trò nhạc cụ mô phỏng |
|---|---|---|---|
| Kênh 1 | D2 | Công tắc 1 | Nhạc cụ bè chính |
| Kênh 2 | D16 | Công tắc 2 | Nhạc cụ bè đối thoại |
| Kênh 3 | D19 | Công tắc 3 | Nhạc cụ giữ nhịp |
| Kênh 4 | D23 | Công tắc 4 | Nhạc cụ bè trầm |

### 2.5. Thiết kế luồng chức năng hệ thống

Luồng chức năng được mô hình hóa theo chu trình khép kín:

1. Điều phối trung tâm thiết lập nhịp tổng.
2. Các nhạc cụ mô phỏng nhận phần việc theo vai trò.
3. Đầu ra từng thành phần được hòa trộn thành kết quả chung.
4. Trạng thái vận hành được quan sát liên tục.
5. Bản điện tử hóa biểu đạt trực tiếp trạng thái thành phần.

**Hình 6: Luồng điều phối từ nhạc trưởng tới các nhạc cụ**

Chu trình này bảo đảm rằng mọi thay đổi ở một lớp đều có dấu hiệu tương ứng ở lớp còn lại, qua đó duy trì tính nhất quán giữa “hệ thống kỹ thuật” và “hệ thống biểu đạt”.

Luồng chức năng còn có ý nghĩa kiểm soát lỗi nhận thức. Khi người học thấy một bất thường âm học, họ có thể lần ngược theo đúng chu trình để xác định bất thường phát sinh từ khâu điều phối, khâu nhạc cụ hay khâu hòa trộn. Đây là ưu điểm lớn so với cách trình bày rời rạc từng thành phần.

### 2.6. Thiết kế luồng vận hành phục vụ học tập

Để phù hợp hoạt động giảng dạy, đề tài xây dựng luồng vận hành theo từng pha rõ ràng:

#### Pha 1 - Đặt chuẩn nền

Thiết lập trạng thái đầy đủ với bốn công tắc bật. Mục đích là tạo mốc chuẩn về chất lượng hòa tấu và độ ổn định nhịp.

**Hình 7: Trạng thái hệ khi tất cả công tắc ở chế độ hoạt động**

Pha chuẩn nền đóng vai trò tham chiếu bắt buộc. Nếu không có mốc chuẩn, mọi nhận xét về suy giảm hoặc phục hồi đều thiếu điểm tựa định lượng và định tính.

#### Pha 2 - Gây lỗi có kiểm soát

Ngắt lần lượt từng công tắc để tạo lỗi cục bộ, sau đó mở rộng sang lỗi kép hoặc lỗi nhiều thành phần. Mục đích là quan sát mức suy giảm theo cấp độ tác động.

**Hình 8: Trạng thái hệ khi một công tắc bị ngắt**

**Hình 9: Trạng thái hệ khi hai công tắc bị ngắt đồng thời**

Việc gây lỗi theo thứ tự tăng dần giúp phân tách rõ ảnh hưởng của từng mức lỗi. Cách làm này tránh hiện tượng gây nhiều lỗi cùng lúc khiến người học khó xác định đóng góp của từng nguyên nhân.

#### Pha 3 - Phục hồi theo kịch bản

Bật lại công tắc theo thứ tự định trước để đánh giá khả năng tái gia nhập và mức độ trở lại ổn định.

**Hình 10: Trạng thái hệ khi phục hồi lại toàn bộ công tắc**

Pha phục hồi đặc biệt quan trọng vì nó phản ánh tư duy thực tiễn của hệ phân tán: mục tiêu không chỉ là phát hiện lỗi, mà còn phải đưa hệ trở về trạng thái chấp nhận được trong thời gian hợp lý.

#### Pha 4 - Đối chiếu và rút kết luận

Tổng hợp biểu mẫu quan sát, so sánh với mốc chuẩn ban đầu, rút ra quan hệ giữa số thành phần hoạt động và chất lượng đầu ra.

Ở pha này, người học cần diễn giải bằng ngôn ngữ kỹ thuật chuẩn: mô tả hiện tượng, nêu nguyên nhân giả định, đối chiếu dữ liệu, kết luận mức tin cậy. Quy trình này giúp nâng năng lực báo cáo khoa học, không dừng ở mô tả cảm tính.

### 2.7. Thiết kế chỉ số quan sát và thang đánh giá

Để giảm tính chủ quan, chương 2 đề xuất bộ chỉ số hỗn hợp định lượng - định tính.

#### 2.7.1. Nhóm chỉ số định lượng

- Độ trễ đầu-cuối;
- Độ sâu hàng đợi;
- Số thành phần đang hoạt động;
- Thời gian phục hồi về trạng thái ổn định.

Nhóm chỉ số định lượng giúp mô tả hệ thống bằng số liệu có thể so sánh giữa các phiên. Đây là cơ sở để kiểm tra tính lặp lại và đánh giá hiệu quả cải tiến trong những lần triển khai sau.

#### 2.7.2. Nhóm chỉ số định tính

- Độ đầy hòa tấu;
- Độ ổn định nhịp cảm nhận;
- Mức gián đoạn âm học;
- Mức dễ phân biệt lỗi theo tai nghe.

Nhóm chỉ số định tính phản ánh đúng mục tiêu sư phạm của đề tài. Một mô hình giáo dục hiệu quả không chỉ đúng về kỹ thuật mà còn phải dễ hiểu, dễ nhận biết và dễ diễn giải với người học ở các mức nền tảng khác nhau.

#### 2.7.3. Thang đánh giá khuyến nghị

Đề tài khuyến nghị thang năm mức cho các chỉ số định tính: rất thấp, thấp, trung bình, cao, rất cao. Thang này giúp chuẩn hóa nhận xét giữa các nhóm thực nghiệm khác nhau.

Việc chuẩn hóa thang đánh giá giúp giảm sai lệch do cảm nhận cá nhân. Khi nhiều nhóm dùng cùng một thang và cùng một biểu mẫu, kết quả tổng hợp sẽ có độ tin cậy cao hơn và thuận lợi cho so sánh theo học kỳ.

**Bảng 7. Bộ chỉ số quan sát định tính và định lượng**

| Nhóm chỉ số | Chỉ số cụ thể | Mục đích |
|---|---|---|
| Định lượng | Độ trễ đầu-cuối | Đo tốc độ phản hồi hệ thống |
| Định lượng | Độ sâu hàng đợi | Theo dõi nguy cơ nghẽn |
| Định lượng | Số thành phần hoạt động | Xác nhận trạng thái hệ |
| Định lượng | Thời gian phục hồi | Đánh giá năng lực tái lập ổn định |
| Định tính | Độ đầy hòa tấu | Đánh giá chất lượng đầu ra cảm nhận |
| Định tính | Độ ổn định nhịp | Đánh giá mức đồng bộ |
| Định tính | Mức gián đoạn âm | Đánh giá tác động khi lỗi xảy ra |
| Định tính | Khả năng nhận diện lỗi | Đánh giá hiệu quả sư phạm trực quan |

### 2.8. Tiêu chí chất lượng thiết kế

Thiết kế được xem là đạt chất lượng khi đồng thời thỏa mãn các tiêu chí:

- **Tính đúng mô hình:** ánh xạ vai trò giữa lớp logic và lớp điện tử hóa nhất quán.
- **Tính rõ phản hồi:** thao tác ngắt/kết nối tạo thay đổi cảm nhận rõ ràng.
- **Tính lặp lại:** kịch bản chạy lại cho kết quả cùng xu hướng.
- **Tính sư phạm:** người học phân tích được nguyên nhân - hệ quả.
- **Tính mở rộng:** có thể thêm kịch bản mới mà không thay đổi nguyên lý lõi.

Năm tiêu chí trên cần được thỏa đồng thời. Nếu chỉ đáp ứng tính trực quan mà thiếu tính đúng mô hình, đề tài sẽ nghiêng về trình diễn. Ngược lại, nếu chỉ đúng kỹ thuật nhưng khó quan sát, hiệu quả đào tạo sẽ không cao. Cân bằng hai mặt này là yêu cầu trung tâm của chương thiết kế.

### 2.9. Phân tích rủi ro thiết kế và biện pháp giảm thiểu

#### Rủi ro 1: Khó phân biệt từng kênh âm khi phát đồng thời

Biện pháp: phân lớp vai trò bè âm và hiệu chỉnh mức cường độ theo kênh để tăng độ nhận diện.

Ngoài ra, trong quá trình trình diễn, cần duy trì thứ tự giới thiệu từng kênh trước khi phát đồng thời để người nghe có mốc nhận diện âm sắc từng bè.

#### Rủi ro 2: Nhiễu thao tác công tắc làm sai lệch ghi nhận

Biện pháp: quy định nhịp thao tác tối thiểu, xác nhận trạng thái trước khi đánh dấu mốc quan sát.

Biện pháp này đặc biệt cần thiết trong buổi đông người, nơi thao tác nhanh hoặc liên tiếp có thể tạo cảm giác sai khác không do bản chất hệ thống.

#### Rủi ro 3: Quan sát thiên lệch theo cảm nhận chủ quan

Biện pháp: bắt buộc kết hợp biểu mẫu định tính với chỉ số định lượng tại cùng mốc thời gian.

Khi dữ liệu định lượng và định tính không khớp, nhóm vận hành cần ghi chú nguyên nhân khả dĩ thay vì bỏ qua, nhằm bảo toàn tính minh bạch của báo cáo.

#### Rủi ro 4: Mất nhất quán giữa biểu hiện âm và trạng thái kỹ thuật

Biện pháp: kiểm tra ánh xạ trạng thái trước phiên thực nghiệm, chuẩn hóa quy trình khởi tạo và phục hồi.

#### Rủi ro 5: Quá tập trung vào trình diễn, thiếu chiều sâu phân tích

Biện pháp: thiết kế trước câu hỏi phân tích cho từng kịch bản và yêu cầu đối chiếu dữ liệu sau mỗi pha.

### 2.10. Giá trị sư phạm của thiết kế

Thiết kế chương 2 không chỉ nhằm tạo ra một mô hình chạy được, mà hướng tới tạo ra một “không gian học tập có thể thao tác”. Sinh viên được phép gây lỗi có kiểm soát, quan sát hậu quả tức thời, rồi quay lại phân tích bản chất hệ thống. Chu trình này tăng khả năng ghi nhớ dài hạn và nâng cao năng lực tư duy hệ thống, đặc biệt với các khái niệm thường bị xem là trừu tượng.

Ngoài ra, mô hình còn hỗ trợ giảng viên tổ chức đánh giá theo năng lực: năng lực nhận diện trạng thái, năng lực giải thích nguyên nhân, và năng lực đề xuất phương án phục hồi.

Một điểm mạnh khác là mô hình khuyến khích làm việc nhóm theo vai trò: người thao tác công tắc, người ghi nhận chỉ số, người đánh giá âm học và người tổng hợp kết luận. Cách tổ chức này phù hợp kỹ năng nghề nghiệp thực tế, nơi các hệ phân tán luôn được vận hành bởi nhóm đa vai trò.

### 2.11. Kết luận chương

Chương 2 đã mở rộng đầy đủ từ bài toán, mục tiêu, kiến trúc, thiết kế chi tiết bản điện tử hóa, luồng chức năng, chỉ số quan sát, tiêu chí chất lượng đến phân tích rủi ro và giá trị sư phạm. Trên cơ sở đó, chương 3 có thể triển khai thực nghiệm theo quy trình nhất quán, bảo đảm mọi kết quả thu được đều có cơ sở diễn giải khoa học.

Nhìn tổng thể, chương thiết kế xác lập rõ hai nguyên lý nền của đề tài: nguyên lý đúng mô hình phân tán và nguyên lý đúng mục tiêu sư phạm. Việc duy trì đồng thời hai nguyên lý này giúp bản điện tử hóa không chỉ là công cụ minh họa, mà trở thành học cụ có cấu trúc, có tiêu chí và có khả năng dùng lâu dài trong giảng dạy.

---

## CHƯƠNG 3. THỰC NGHIỆM

Chương này trình bày:

- Mục tiêu thực nghiệm và bố trí môi trường triển khai trong mạng cục bộ.
- Quy trình thực nghiệm chuẩn và các kịch bản tác động lỗi - phục hồi.
- Biểu mẫu thu thập dữ liệu và nguyên tắc ghi nhận kết quả.
- Kết quả thực nghiệm theo từng kịch bản và phân tích định tính chuyên sâu.
- Đối chiếu giữa chỉ số kỹ thuật và biểu hiện âm học trên bản điện tử hóa.
- Thảo luận giá trị thực tiễn trong đào tạo và các hạn chế cần cải tiến.

### 3.1. Mục tiêu thực nghiệm

Thực nghiệm được tổ chức để kiểm chứng ba giả thuyết chính:

1. Bản điện tử hóa có thể biểu đạt trực quan trạng thái hoạt động của các thành phần phân tán.
2. Thao tác ngắt/kết nối qua công tắc tạo ra biến thiên âm học nhất quán với hiện tượng phân tán tương ứng.
3. Người quan sát có thể đối chiếu chính xác giữa biến thiên âm học và biến thiên chỉ số kỹ thuật.

### 3.2. Bố trí môi trường thực nghiệm

Môi trường thực nghiệm được chuẩn bị theo mô hình nhiều nút trong cùng mạng cục bộ để phản ánh cấu trúc phân tán. Bản điện tử hóa được đặt tại vị trí trung tâm trình diễn nhằm bảo đảm tầm quan sát trực tiếp cho người nghe và người điều phối.

Các điều kiện triển khai:

- Mỗi thành phần có vai trò rõ ràng trong chuỗi điều phối - xử lý - hòa trộn;
- Kênh quan sát trạng thái hoạt động liên tục trong suốt buổi thử nghiệm;
- Bản điện tử hóa hoạt động đồng bộ với trạng thái hệ thống mô phỏng.

### 3.3. Quy trình thực nghiệm chuẩn

Quy trình gồm bảy bước:

1. Thiết lập trạng thái khởi đầu ổn định (4 công tắc bật).
2. Chạy quan sát cơ sở trong khoảng thời gian đủ dài để thu mức chuẩn.
3. Tác động có kiểm soát: ngắt 1 công tắc.
4. Thu thập số liệu và ghi nhận âm học.
5. Mở rộng tác động: ngắt thêm công tắc thứ hai hoặc thứ ba.
6. Phục hồi tuần tự từng công tắc.
7. Tổng hợp dữ liệu và so sánh với mức chuẩn ban đầu.

**Hình 14: Quy trình thực nghiệm và thu thập dữ liệu**

### 3.4. Kịch bản thực nghiệm trọng tâm

**Bảng 6. Kịch bản thực nghiệm trọng tâm**

| Kịch bản | Mô tả thao tác | Trạng thái mong đợi | Chỉ số cần theo dõi |
|---|---|---|---|
| K1 - Ổn định | Bật 4 công tắc | Hòa tấu đầy đủ, nhịp ổn định | Độ trễ nền, số thành phần hoạt động |
| K2 - Mất thành phần đơn | Tắt 1 công tắc | Mất 1 bè âm nhưng hệ còn hoạt động | Biến thiên độ đầy hòa tấu |
| K3 - Mất thành phần kép | Tắt 2 công tắc | Suy giảm rõ cấu trúc âm học | Độ ổn định nhịp giảm |
| K4 - Mất thành phần nhiều | Tắt 3 công tắc | Đầu ra gần trạng thái tối giản | Mức gián đoạn tăng cao |
| K5 - Phục hồi tuần tự | Bật lại từng công tắc | Bè âm tái gia nhập theo từng bước | Tốc độ trở lại ổn định |
| K6 - Phục hồi đồng thời | Bật lại nhiều công tắc cùng lúc | Hệ nhanh về cấu hình đầy đủ | Độ dao động ngắn hạn khi tái gia nhập |

### 3.5. Mẫu ghi nhận dữ liệu thực nghiệm

Để chuẩn hóa việc thu thập dữ liệu, mỗi phiên thực nghiệm sử dụng biểu mẫu gồm các trường:

- Thời điểm thao tác công tắc;
- Công tắc tác động;
- Số thành phần còn hoạt động;
- Nhận xét về độ đầy hòa tấu;
- Nhận xét về mức ổn định nhịp;
- Nhận xét về độ trễ cảm nhận;
- Trạng thái phục hồi sau tác động.

Biểu mẫu chuẩn giúp giảm sai lệch chủ quan giữa các lần ghi nhận và tạo cơ sở so sánh liên phiên.

### 3.6. Kết quả thực nghiệm theo từng kịch bản

**Bảng 8. Kết quả thực nghiệm theo từng kịch bản**

| Kịch bản | Kết quả quan sát chính | Nhận định |
|---|---|---|
| K1 - Ổn định | Âm học đầy đủ, độ ổn định cao | Mức chuẩn tin cậy để so sánh |
| K2 - Mất đơn | Mất một bè rõ rệt, tổng thể vẫn liên tục | Thể hiện tốt chịu lỗi cục bộ |
| K3 - Mất kép | Hòa tấu mỏng, nhịp cảm nhận kém chắc | Chất lượng suy giảm theo số lỗi |
| K4 - Mất nhiều | Âm học tối giản, tính hoàn chỉnh thấp | Phản ánh giới hạn chịu lỗi |
| K5 - Phục hồi tuần tự | Bè âm trở lại từng bước, hệ ổn định dần | Mô phỏng tốt tái gia nhập thành phần |
| K6 - Phục hồi đồng thời | Phục hồi nhanh, có dao động ngắn ban đầu | Cần điều phối nhịp tái gia nhập hợp lý |

**Hình 11: Biểu đồ biến thiên độ trễ theo mức tải**

**Hình 12: Biểu đồ thay đổi độ đầy hòa tấu theo số nhạc cụ bị ngắt**

**Hình 13: Giao diện quan sát trạng thái dịch vụ theo thời gian thực**

### 3.7. Phân tích định tính sâu

#### 3.7.1. Độ đầy hòa tấu như chỉ báo chất lượng dịch vụ

Qua các kịch bản, độ đầy hòa tấu giảm gần tuyến tính theo số lượng công tắc bị ngắt. Điều này phản ánh trực quan mối quan hệ giữa số thành phần hoạt động và chất lượng đầu ra tổng thể.

#### 3.7.2. Ổn định nhịp như chỉ báo đồng bộ

Ở trạng thái đủ bốn kênh, cảm nhận nhịp ổn định cao. Khi số kênh giảm, người nghe dễ nhận thấy độ “lỏng” trong cấu trúc nhịp. Đây là biểu hiện của suy giảm đồng bộ trong hệ thống.

#### 3.7.3. Phục hồi như chỉ báo khả năng tự lành

Việc bật lại công tắc cho thấy hệ có thể tái gia nhập thành phần mà không cần khởi tạo lại toàn cục. Đây là điểm quan trọng trong giảng dạy về khả năng chịu lỗi và tính liên tục dịch vụ.

### 3.8. Đối chiếu giữa quan sát âm học và quan sát chỉ số

Kết quả thực nghiệm cho thấy hai kênh quan sát có tính tương quan cao:

- Khi số thành phần hoạt động giảm, độ đầy hòa tấu giảm tương ứng;
- Khi phục hồi thành phần, độ đầy hòa tấu tăng trở lại;
- Khi xảy ra dao động trạng thái, người nghe ghi nhận hiện tượng chênh nhịp ngắn hạn.

Sự tương quan này khẳng định giá trị của bản điện tử hóa như một công cụ chuyển hóa dữ liệu kỹ thuật thành biểu hiện cảm nhận.

### 3.9. Thảo luận về giá trị thực tiễn trong đào tạo

Trong các buổi trình diễn thử nghiệm, người học phản hồi rằng việc thao tác công tắc và nghe ngay sự thay đổi của hòa tấu giúp hiểu nhanh hơn khái niệm lỗi cục bộ so với cách học chỉ dựa vào sơ đồ. Đặc biệt, quá trình phục hồi tuần tự tạo được nhận thức rõ về khác biệt giữa “hệ còn sống” và “hệ đạt chất lượng đầy đủ”.

Điều này cho thấy mô hình có thể tích hợp trực tiếp vào các buổi thực hành của học phần Hệ thống phân tán như một học cụ trung tâm, không chỉ là phần minh họa phụ.

### 3.10. Hạn chế trong quá trình thực nghiệm

Dù đạt mục tiêu chính, thực nghiệm vẫn tồn tại một số hạn chế:

- Âm sắc buzzer đơn giản nên khó biểu đạt sắc thái tinh vi của từng nhạc cụ;
- Khi người nghe không được hướng dẫn trước, có thể nhầm lẫn giữa “mất đồng bộ” và “mất thành phần” ở một số tình huống;
- Bộ đo định lượng chưa mở rộng tới các chỉ số sâu về dao động theo thời gian rất ngắn.

Các hạn chế này không làm thay đổi kết luận chính, nhưng là cơ sở quan trọng cho kế hoạch nâng cấp.

### 3.11. Kết luận chương

Chương 3 chứng minh rằng bản điện tử hóa ESP - buzzer - công tắc hoàn thành tốt vai trò trung tâm của đề tài. Hệ thống không chỉ tái hiện được các trạng thái phân tán điển hình mà còn tạo được môi trường học tập trực quan, có kiểm soát, có thể lặp lại và dễ đánh giá.

---

## CHƯƠNG 4. KẾT LUẬN

Chương này trình bày:

- Tổng kết các kết quả chính mà đề tài đã đạt được.
- Phân tích các nội dung chưa đạt, nguyên nhân và hướng khắc phục.
- Đóng góp học thuật và sư phạm của mô hình mô phỏng điện tử hóa.
- Định hướng phát triển trong tương lai cho mở rộng quy mô và chuẩn hóa đánh giá.
- Kết luận cuối cùng về tính khả thi và giá trị ứng dụng trong giảng dạy.

### 4.1. Tổng kết kết quả đạt được

Đề tài đã hoàn thành mục tiêu xây dựng một mô hình mô phỏng hệ thống phân tán phục vụ học tập theo hướng trực quan, trong đó bản điện tử hóa là trọng tâm. Kết quả nổi bật trước hết là việc thiết kế thành công mô hình 1 ESP, 4 buzzer và 4 công tắc, với kết nối buzzer qua các cổng D2, D16, D19, D23, bảo đảm phản ánh rõ trạng thái hoạt động của bốn nhạc cụ mô phỏng.

Thông qua các kịch bản vận hành ổn định, gây lỗi cục bộ và phục hồi, nhóm đã chứng minh được mối liên hệ nhất quán giữa trạng thái kỹ thuật của hệ thống và biểu hiện âm học cảm nhận được. Khi một hoặc nhiều thành phần bị ngắt, chất lượng hòa tấu suy giảm theo mức độ tác động; khi thành phần được tái gia nhập, chất lượng đầu ra cải thiện theo hướng trở lại trạng thái cân bằng. Điều này thể hiện đúng bản chất của hệ phân tán: hệ vẫn có thể duy trì hoạt động khi lỗi cục bộ xuất hiện, nhưng chất lượng dịch vụ phụ thuộc trực tiếp vào số lượng và trạng thái các thành phần.

Về mặt đào tạo, mô hình cho thấy hiệu quả rõ rệt trong việc hỗ trợ người học tiếp cận các khái niệm trừu tượng như mất đồng bộ, suy giảm dịch vụ và phục hồi trạng thái. Thay vì chỉ quan sát chỉ số hoặc sơ đồ tĩnh, người học có thể thao tác trực tiếp trên công tắc, nghe sự thay đổi của đầu ra và đối chiếu lại với dữ liệu quan sát. Cách tiếp cận này giúp tăng năng lực suy luận nguyên nhân - hệ quả và nâng cao chất lượng tiếp thu trong các buổi thực hành.

### 4.2. Kết quả chưa đạt được và nguyên nhân

Mặc dù đạt được các mục tiêu chính, đề tài vẫn còn một số hạn chế cần thẳng thắn nhìn nhận. Trước hết, khả năng biểu đạt âm sắc của buzzer còn đơn giản, nên mức độ phân biệt sắc thái giữa các nhạc cụ mô phỏng chưa cao. Hạn chế này ảnh hưởng đến độ phong phú của trải nghiệm nghe và làm giảm chiều sâu cảm nhận trong các kịch bản phức tạp.

Thứ hai, quy mô bản điện tử hóa hiện tại mới dừng ở bốn kênh nhạc cụ mô phỏng. Mức quy mô này phù hợp cho mục tiêu nền tảng, nhưng chưa đủ để phản ánh các cấu hình phân tán lớn hơn hoặc các tình huống tương tác đa thành phần có mức phụ thuộc cao. Do đó, khả năng mô tả những hiện tượng phân tán nâng cao vẫn còn giới hạn.

Thứ ba, bộ chỉ số đánh giá tuy đã đáp ứng mục tiêu thực hành cơ bản nhưng chưa mở rộng đầy đủ các chỉ báo định lượng chuyên sâu theo thời gian ngắn. Điều này khiến việc so sánh chi tiết giữa các phiên thực nghiệm còn phụ thuộc một phần vào nhận xét định tính.

Cuối cùng, đề tài chưa hoàn thiện bộ tiêu chí đánh giá chuẩn hóa ở mức học phần để giảng viên có thể chấm điểm đồng nhất giữa nhiều nhóm. Đây là khoảng trống cần được bổ sung để mô hình được tích hợp bền vững vào hoạt động giảng dạy chính khóa.

### 4.3. Hướng phát triển

Trong giai đoạn tiếp theo, hướng phát triển ưu tiên là mở rộng bản điện tử hóa theo kiến trúc mô-đun nhằm tăng số lượng nhạc cụ mô phỏng và nâng cao khả năng biểu đạt trạng thái phân tán đa thành phần. Việc mở rộng này cần đi kèm chuẩn hóa kết nối và quy trình vận hành để vẫn bảo đảm tính lặp lại trong môi trường lớp học.

Song song, nhóm định hướng nâng cấp hệ chỉ số đánh giá theo hướng kết hợp chặt chẽ giữa định lượng và định tính, bổ sung các chỉ báo đo mức dao động và tốc độ phục hồi theo từng kịch bản cụ thể. Khi bộ chỉ số được chuẩn hóa, kết quả thực nghiệm sẽ có cơ sở so sánh tốt hơn giữa các đợt học và giữa các nhóm triển khai.

Một hướng quan trọng khác là hoàn thiện bộ tài liệu hướng dẫn sử dụng trong giảng dạy, bao gồm kịch bản thực hành theo cấp độ, biểu mẫu ghi nhận thống nhất và rubric đánh giá theo năng lực. Cách tiếp cận này sẽ giúp mô hình không chỉ dừng ở phạm vi bài tập lớn, mà có thể trở thành học cụ thực nghiệm ổn định cho học phần Các hệ thống phân tán trong các học kỳ tiếp theo.

**Hình 15: Lộ trình phát triển mở rộng bản điện tử hóa**

---

## PHỤ LỤC A. MA TRẬN LIÊN KẾT NỘI DUNG VỚI MỤC TIÊU HỌC PHẦN

| Nội dung báo cáo | Mục tiêu học phần liên quan | Mức đóng góp |
|---|---|---|
| Kiến thức nền phân tán | Hiểu bản chất và thách thức hệ phân tán | Cao |
| Nhạc lý và công-xéc-tô | Tăng khả năng mô hình hóa liên ngành | Trung bình - cao |
| Thiết kế bản điện tử hóa | Nâng cao năng lực thiết kế mô phỏng | Cao |
| Kịch bản thực nghiệm lỗi | Hiểu chịu lỗi và phục hồi | Cao |
| Đối chiếu chỉ số - âm học | Nâng cao tư duy phân tích hệ thống | Cao |

---

## PHỤ LỤC B. KHUYẾN NGHỊ TỔ CHỨC BUỔI TRÌNH DIỄN HỌC TẬP

Để tận dụng tối đa hiệu quả của mô hình, một buổi trình diễn nên chia thành bốn pha:

1. Pha giới thiệu khái niệm và mục tiêu quan sát;
2. Pha chạy trạng thái chuẩn để tạo mốc tham chiếu;
3. Pha gây lỗi có kiểm soát bằng công tắc;
4. Pha phục hồi và tổng kết bài học.

Mỗi pha cần có biểu mẫu ghi nhận ngắn để người học tự điền, qua đó tăng tính chủ động và giảm phụ thuộc vào thuyết trình một chiều.

---

## TÀI LIỆU THAM KHẢO

[1] L. Lamport, “Time, clocks, and the ordering of events in a distributed system,” *Communications of the ACM*, vol. 21, no. 7, pp. 558-565, Jul. 1978, doi: 10.1145/359545.359563.

[2] G. DeCandia *et al*., “Dynamo: Amazon’s highly available key-value store,” in *Proc. 21st ACM SIGOPS Symp. Operating Systems Principles (SOSP)*, Stevenson, WA, USA, 2007, pp. 205-220, doi: 10.1145/1294261.1294281.

[3] S. Ghemawat, H. Gobioff, and S.-T. Leung, “The Google file system,” in *Proc. 19th ACM Symp. Operating Systems Principles (SOSP)*, Bolton Landing, NY, USA, 2003, pp. 29-43, doi: 10.1145/945445.945450.

[4] J. Dean and S. Ghemawat, “MapReduce: Simplified data processing on large clusters,” *Communications of the ACM*, vol. 51, no. 1, pp. 107-113, Jan. 2008, doi: 10.1145/1327452.1327492.

[5] M. P. Herlihy and J. M. Wing, “Linearizability: A correctness condition for concurrent objects,” *ACM Transactions on Programming Languages and Systems*, vol. 12, no. 3, pp. 463-492, Jul. 1990, doi: 10.1145/78969.78972.

[6] S. Gilbert and N. Lynch, “Brewer’s conjecture and the feasibility of consistent, available, partition-tolerant web services,” *SIGACT News*, vol. 33, no. 2, pp. 51-59, Jun. 2002, doi: 10.1145/564585.564601.

[7] P. Hunt, M. Konar, F. P. Junqueira, and B. Reed, “ZooKeeper: Wait-free coordination for Internet-scale systems,” in *Proc. USENIX Annual Technical Conference (USENIX ATC)*, Boston, MA, USA, 2010, pp. 145-158.

[8] T. Chandra and S. Toueg, “Unreliable failure detectors for reliable distributed systems,” *Journal of the ACM*, vol. 43, no. 2, pp. 225-267, Mar. 1996, doi: 10.1145/226643.226647.

[9] M. A. Brewer, “Towards robust distributed systems,” in *Proc. 19th Annual ACM Symp. Principles of Distributed Computing (PODC)*, Portland, OR, USA, 2000.

[10] E. A. Lee, “The problem with threads,” *Computer*, vol. 39, no. 5, pp. 33-42, May 2006, doi: 10.1109/MC.2006.180.

[11] N. Dragoni *et al*., “Microservices: Yesterday, today, and tomorrow,” in *Present and Ulterior Software Engineering*, Cham, Switzerland: Springer, 2017, pp. 195-216, doi: 10.1007/978-3-319-67425-4_12.

[12] R. van Renesse and F. B. Schneider, “Chain replication for supporting high throughput and availability,” in *Proc. 6th USENIX Symp. Operating Systems Design and Implementation (OSDI)*, San Francisco, CA, USA, 2004, pp. 91-104.
