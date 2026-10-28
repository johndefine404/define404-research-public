# Cùng một cửa hàng, câu trả lời bằng 5 ngôn ngữ có nhất quán không: Thông tin cửa hàng mà AI đưa ra có thay đổi theo ngôn ngữ của câu hỏi?

Đây là bản dịch. Bản gốc làm chuẩn là bản tiếng Hàn, phiên bản 1: https://define404.com/report/003-local404-language-consistency/

Ghi chú dữ liệu Local404. So sánh lại câu trả lời của Claude về 800 nhà hàng thông thường ở Hàn Quốc giữa 5 ngôn ngữ

- Tác giả: Kim Hawon (Define404 Research)
- Ngày: 2026-10-28
- Loại: Ghi chú dữ liệu. Phân tích lại các câu trả lời đã thu thập trong báo cáo số 2 (Local404) với câu hỏi mới. Không hỏi mới và không đánh giá mới.
- Đăng ký trước: commit 7169864 của kho nghiên cứu (2026-10-28 23:39 ICT). Tệp prereg.md chứa giả thuyết và phương pháp phân tích đã được commit trước khi chạy phân tích.
- DOI: https://doi.org/10.5281/zenodo.23739008
- Xung đột lợi ích: Define404, nơi tác giả làm việc, đang chuẩn bị dịch vụ giám sát câu trả lời của AI và chẩn đoán mức độ hiển thị trên AI cho từng cửa hàng. Sản phẩm của công ty không nằm trong đối tượng khảo sát.

## Tóm tắt

Chúng tôi xem xét liệu khi hỏi cùng một AI về cùng một cửa hàng bằng năm ngôn ngữ, lượng thông tin cửa hàng nhận được có như nhau hay không. Chúng tôi dùng nguyên các câu trả lời của Claude mà báo cáo số 2 (Local404) đã thu thập (điều kiện trí nhớ của Haiku 5.5 với 800 cửa hàng, hai điều kiện tìm kiếm web của Haiku 5.5 và Sonnet 5.5 với 100 cửa hàng) cùng nhãn đánh giá. Trong điều kiện trí nhớ, ở 612 cửa hàng có đủ câu trả lời bằng 5 ngôn ngữ, tỷ lệ câu hỏi tiếng Hàn nêu loại hình kinh doanh là 38.2%, trung bình của 4 ngôn ngữ còn lại là 20.6%, chênh lệch 17.6 điểm phần trăm (khoảng tin cậy 95% từ 15.1 đến 20.2), giả thuyết H1 được ủng hộ. Ở hai điều kiện tìm kiếm web (70 cửa hàng), chênh lệch là 3.9 và 3.2 điểm phần trăm, khoảng tin cậy chứa 0. Khi đã nêu loại hình kinh doanh, tỷ lệ đúng theo từng ngôn ngữ nằm trong khoảng 71.6 đến 79.1%, gần như nhau.

### Kết quả chính

- Ở 612 cửa hàng trong điều kiện trí nhớ, hỏi bằng tiếng Hàn thì nêu loại hình kinh doanh 38.2%, trung bình 4 ngôn ngữ còn lại là 20.6%. Chênh lệch 17.6 điểm phần trăm (15.1 đến 20.2), p hiệu chỉnh Holm < 0.001, giả thuyết đăng ký trước H1 được ủng hộ.
- Theo từng ngôn ngữ: tiếng Việt 29.2%, tiếng Trung 24.2%, tiếng Nhật 18.0%, tiếng Anh 10.9%. Tiếng Hàn và tiếng Anh khác nhau nhiều nhất (187 trong 612 cửa hàng, 30.6%).
- Ở 70 cửa hàng trong điều kiện tìm kiếm web, chênh lệch nhỏ: 3.9 điểm phần trăm (-0.9 đến 8.8) và 3.2 điểm phần trăm (-5.1 đến 11.5). Với 70 cửa hàng, không phát hiện được chênh lệch nhỏ.
- Trong các câu trả lời có nêu loại hình kinh doanh, tỷ lệ đúng là tiếng Hàn 77.4%, tiếng Anh 71.6%, tiếng Nhật 76.4%, tiếng Trung 79.1%, tiếng Việt 73.2%. Nêu thường xuyên hơn không có nghĩa là đúng thường xuyên hơn.

<!-- src: 003-local404-consistency/analysis/out/h1.csv; h2.csv; holm.csv; explore_correctness.csv; explore_pairs.csv -->

## 1 Giới thiệu

Khi một khách nước ngoài hỏi AI bằng ngôn ngữ của mình "Quán này là nhà hàng kiểu gì?", họ có nhận được câu trả lời giống như khi hỏi bằng tiếng Hàn không? Báo cáo số 2 (Local404) đã hỏi tình trạng hoạt động, địa chỉ và loại hình kinh doanh của 800 nhà hàng bằng 5 ngôn ngữ rồi đối chiếu với dữ liệu cấp phép công khai. Các mô hình Claude hầu như không khẳng định tình trạng hoạt động, nên mức độ thống nhất đánh giá giữa các ngôn ngữ (H5 của báo cáo số 2) nằm sát đáy; loại hình kinh doanh xuất hiện trong 18 đến 30% câu trả lời nhưng chỉ được báo cáo theo tổng của từng hệ thống. Câu trả lời có khác nhau theo ngôn ngữ ngay trong cùng một cửa hàng hay không thì chưa được xem xét.

Ghi chú này lấp khoảng trống đó. Chúng tôi không hỏi mới mà dùng nguyên câu trả lời và nhãn đánh giá của báo cáo số 2, nhưng đã ghi câu hỏi và phương pháp phân tích vào kho lưu trữ trước rồi mới phân tích. Có ba câu hỏi. Câu hỏi tiếng Hàn có nêu loại hình kinh doanh thường xuyên hơn các ngôn ngữ khác không (H1, với điều kiện tìm kiếm web là H2). Sự không nhất quán giữa các ngôn ngữ có nhiều hơn ở những cửa hàng đã đăng ký trên Kakao Places không (H3). Cặp ngôn ngữ nào khác nhau, và khi khác nhau thì bên nào đúng (phân tích khám phá).

## 2 Nghiên cứu liên quan

Có nhiều báo cáo cho thấy mô hình ngôn ngữ đa ngữ ghi nhớ cùng một sự kiện khác nhau tùy theo ngôn ngữ. Jiang và cộng sự (2020) báo cáo trên 23 ngôn ngữ rằng ngôn ngữ càng nhiều dữ liệu thì khả năng nhớ lại sự kiện càng cao; Kassner và cộng sự (2021) báo cáo trên 53 ngôn ngữ rằng việc nhớ lại sự kiện có thiên lệch theo ngôn ngữ. Qi và cộng sự (2023) đề xuất chỉ số đo tính nhất quán giữa các ngôn ngữ tách khỏi độ chính xác, còn Chua và cộng sự (2024) báo cáo rằng ngay cả các mô hình lớn mới nhất cũng không chuyển được kiến thức sâu qua các ngôn ngữ. Các nghiên cứu này đo các sự kiện kiểu bách khoa bằng dạng điền chỗ trống hoặc trắc nghiệm. Trong phạm vi chúng tôi kiểm tra, chưa thấy báo cáo nào so sánh câu trả lời tự do về các cơ sở kinh doanh nhỏ ở một khu vực cụ thể giữa các ngôn ngữ trong điều kiện sử dụng thực tế.

## 3 Phương pháp khảo sát

Hình 1. Khảo sát được thực hiện như thế này

![Lấy lại 4,000 câu trả lời của khảo sát trước, ghi câu hỏi trước, đánh dấu từng câu trả lời có nêu loại hình kinh doanh hay không, rồi so sánh giữa các ngôn ngữ ở 612 cửa hàng có đủ câu trả lời bằng 5 ngôn ngữ](figures/fig1-flow.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/data_inventory.csv -->

### 3.1 Dữ liệu

Không chọn mẫu mới. Đầu vào là mẫu 800 cửa hàng của báo cáo số 2 (400 đang hoạt động, 400 đã đóng cửa), mẫu phụ tìm kiếm web 100 cửa hàng, và một tệp kết quả đánh giá mà báo cáo số 2 đã công bố (judgments.csv, 7,312 dòng). Không dùng nguyên văn câu trả lời. Câu hỏi là một câu hỏi chung về tình trạng hoạt động, địa chỉ và loại hình kinh doanh; tên cửa hàng và quận huyện được giữ nguyên cách viết tiếng Hàn ở mọi ngôn ngữ (phụ lục A của báo cáo số 2).

Bảng 1. Cấu trúc dữ liệu

| Điều kiện | Mô hình | Câu trả lời | Cửa hàng | Câu trả lời loại vì ngành "khác" | Cửa hàng đủ 5 ngôn ngữ |
|---|---|---|---|---|---|
| Điều kiện trí nhớ | Claude Haiku 5.5, không công cụ | 4,000 | 800 | 940 | 612 |
| Điều kiện tìm kiếm (Haiku) | Claude Haiku 5.5, tìm kiếm web | 500 | 100 | 150 | 70 |
| Điều kiện tìm kiếm (Sonnet) | Claude Sonnet 5.5, tìm kiếm web | 500 | 100 | 150 | 70 |
| Điều kiện trí nhớ (Llama) | Llama 3.1 8B, chỉ tiếng Anh, tiếng Nhật, tiếng Hàn | 2,312 | 800 | 539 | 0 |

<!-- src: 003-local404-consistency/analysis/out/data_inventory.csv -->

Llama không có đủ 5 ngôn ngữ nên bị loại khỏi phân tích kiểm định; chỉ xem xét tính nhất quán giữa 3 ngôn ngữ trong đánh giá tình trạng hoạt động như một phân tích khám phá. Nhãn chưa xác định ở ba điều kiện Claude là 0 trường hợp cho cả loại hình kinh doanh và địa chỉ.

### 3.2 Đo lường và đánh giá

Nhãn đánh giá được lấy nguyên từ kết quả đánh giá bằng từ điển và đánh giá có LLM hỗ trợ của báo cáo số 2, không thêm người đánh giá mới. Việc nêu loại hình kinh doanh được mã hóa là 1 nếu nhãn loại hình kinh doanh là đúng hoặc sai, và 0 nếu không có. Các câu trả lời mà báo cáo số 2 đã loại khỏi đánh giá loại hình kinh doanh vì ngành thực tế là "khác" (940 câu trong điều kiện trí nhớ) được coi là thiếu dữ liệu. So sánh ở cấp cửa hàng chỉ dùng những cửa hàng có giá trị ở cả 5 ngôn ngữ (612 cửa hàng trong điều kiện trí nhớ, 70 cửa hàng ở mỗi điều kiện tìm kiếm). Cửa hàng không nhất quán về việc nêu là cửa hàng mà chỉ một phần trong 5 ngôn ngữ nêu loại hình kinh doanh.

### 3.3 Phân tích

Giống với đăng ký trước (commit 7169864). H1 là trung bình của chênh lệch ghép cặp, tính cho từng cửa hàng trong điều kiện trí nhớ bằng việc nêu bằng tiếng Hàn (0/1) trừ đi trung bình việc nêu của 4 ngôn ngữ còn lại, với khoảng tin cậy 95% từ sai số chuẩn gộp theo cửa hàng. H2a (tìm kiếm Sonnet) và H2b (tìm kiếm Haiku) dùng cùng thống kê. H3 so sánh tỷ lệ cửa hàng không nhất quán về việc nêu trong điều kiện trí nhớ giữa cửa hàng đã đăng ký Kakao và chưa đăng ký như hai nhóm độc lập. 4 giá trị p hai phía được hiệu chỉnh Holm như một họ, và giả thuyết được coi là được ủng hộ khi p hiệu chỉnh < 0.05 và dấu của chênh lệch đúng hướng giả thuyết. Các ô có mẫu dưới 40 không được diễn giải, và các phân tích không có trong đăng ký trước được đánh dấu là khám phá. Chênh lệch nhỏ nhất có thể phát hiện đã được ghi trước là khoảng 4 đến 7 điểm phần trăm với 800 cửa hàng trong điều kiện trí nhớ và khoảng 11 đến 20 điểm phần trăm với 100 cửa hàng trong điều kiện tìm kiếm (mức ý nghĩa 5% hai phía, năng lực kiểm định 80%).

## 4 Kết quả

### 4.1 Giả thuyết đăng ký trước

Bảng 2. Kết quả kiểm định giả thuyết đăng ký trước (chênh lệch tính bằng điểm phần trăm, trong ngoặc là khoảng tin cậy 95%)

| Giả thuyết | Điều kiện | So sánh | Cửa hàng | Chênh lệch | p hai phía | p Holm | Kết luận |
|---|---|---|---|---|---|---|---|
| H1 | Điều kiện trí nhớ | Tiếng Hàn 38.2% so với trung bình 4 ngôn ngữ còn lại 20.6% | 612 | 17.6 (15.1 đến 20.2) | < 0.001 | < 0.001 | Được ủng hộ |
| H2a | Điều kiện tìm kiếm (Sonnet) | Tiếng Hàn 45.7% so với trung bình còn lại 41.8% | 70 | 3.9 (-0.9 đến 8.8) | 0.112 | 0.240 | Không được ủng hộ |
| H2b | Điều kiện tìm kiếm (Haiku) | Tiếng Hàn 42.9% so với trung bình còn lại 39.6% | 70 | 3.2 (-5.1 đến 11.5) | 0.447 | 0.447 | Không được ủng hộ |
| H3 | Điều kiện trí nhớ | Tỷ lệ cửa hàng không nhất quán, đã đăng ký Kakao 39.0% (310 cửa hàng) so với chưa đăng ký 46.0% (302 cửa hàng) | 612 | -7.0 (-14.8 đến 0.8) | 0.080 | 0.240 | Không được ủng hộ (ngược hướng) |

<!-- src: 003-local404-consistency/analysis/out/h1.csv; h2.csv; h3.csv; holm.csv -->

H1 được ủng hộ. Với cùng 612 cửa hàng, hỏi bằng tiếng Hàn thì nêu loại hình kinh doanh 38.2%, trung bình 4 ngôn ngữ còn lại là 20.6%. Khoảng tin cậy của chênh lệch ghép cặp 17.6 điểm phần trăm (15.1 đến 20.2) vượt xa mức chênh lệch có thể phát hiện đã ghi trước (4 đến 7 điểm phần trăm). Chênh lệch ghép cặp theo từng ngôn ngữ được nêu ở bảng 3.

Hình 2. Hỏi bằng ngôn ngữ nào thì AI nêu loại hình kinh doanh

![Trong điều kiện trí nhớ, với cùng 612 cửa hàng, tỷ lệ nêu loại hình kinh doanh là tiếng Hàn 38.2%, tiếng Việt 29.2%, tiếng Trung 24.2%, tiếng Nhật 18.0%, tiếng Anh 10.9%. Tiếng Hàn cao hơn trung bình các ngôn ngữ còn lại 17.6 điểm phần trăm](figures/fig2-h1-by-language.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/h1.csv -->

Bảng 3. Tỷ lệ nêu loại hình kinh doanh theo ngôn ngữ trong điều kiện trí nhớ và chênh lệch ghép cặp so với tiếng Hàn (612 cửa hàng, thống kê mô tả ngoài đăng ký trước)

| Ngôn ngữ | Tỷ lệ nêu | Chênh lệch so với tiếng Hàn (điểm phần trăm, CI 95%) |
|---|---|---|
| Tiếng Hàn | 38.2% | Mốc so sánh |
| Tiếng Việt | 29.2% | 9.0 (6.4 đến 11.6) |
| Tiếng Trung | 24.2% | 14.1 (10.5 đến 17.6) |
| Tiếng Nhật | 18.0% | 20.3 (17.0 đến 23.5) |
| Tiếng Anh | 10.9% | 27.3 (23.5 đến 31.1) |

<!-- src: 003-local404-consistency/analysis/out/h1.csv (confirmatory=False 행) -->

H2a và H2b không được ủng hộ. Ở hai điều kiện có bật tìm kiếm web, chênh lệch là 3.9 và 3.2 điểm phần trăm, khoảng tin cậy chứa 0. Tuy nhiên, chênh lệch có thể phát hiện với 70 cửa hàng là khoảng 11 đến 20 điểm phần trăm, nên cần đọc là "không nhìn thấy chênh lệch nhỏ hơn mức này" chứ không phải "không có chênh lệch". Ở cả hai điều kiện tìm kiếm, bản thân tỷ lệ nêu đều cao hơn điều kiện trí nhớ (tập cửa hàng khác nhau nên không phải so sánh ghép cặp).

Hình 3. Bật tìm kiếm web thì sao

![Ở 70 cửa hàng trong điều kiện tìm kiếm web, tỷ lệ nêu loại hình kinh doanh là Sonnet tiếng Hàn 45.7% so với trung bình còn lại 41.8%, Haiku tiếng Hàn 42.9% so với 39.6%. Chênh lệch nằm trong biên độ sai số](figures/fig3-search-no-gap.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/h2.csv -->

H3 đi ngược hướng. Tỷ lệ cửa hàng không nhất quán về việc nêu là 39.0% ở cửa hàng đã đăng ký Kakao (310 cửa hàng) và 46.0% ở cửa hàng chưa đăng ký (302 cửa hàng); cửa hàng đã đăng ký lại thấp hơn 7.0 điểm phần trăm (-14.8 đến 0.8). Điều này khác với tiền đề của đăng ký trước, rằng cửa hàng chưa đăng ký sẽ im lặng ở mọi ngôn ngữ nên dễ nhất quán hơn.

### 4.2 Khám phá: cặp ngôn ngữ nào khác nhau

Trong 612 cửa hàng ở điều kiện trí nhớ, số cửa hàng mà chỉ một phần trong 5 ngôn ngữ nêu loại hình kinh doanh là 260 (42.5%; khoảng tin cậy Wilson 95% từ 38.6 đến 46.4). Ở cửa hàng đang hoạt động (282 cửa hàng) là 51.4% (45.6 đến 57.2), ở cửa hàng đã đóng cửa (330 cửa hàng) là 34.8% (29.9 đến 40.1). Ở điều kiện tìm kiếm, Haiku là 27 trong 70 cửa hàng (38.6%; 28.0 đến 50.3), Sonnet là 26 trong 70 cửa hàng (37.1%; 26.8 đến 48.9).

Bảng 4. Không nhất quán về việc nêu loại hình kinh doanh theo cặp ngôn ngữ (điều kiện trí nhớ, 612 cửa hàng, trong ngoặc là khoảng tin cậy Wilson 95%)

| Cặp ngôn ngữ | Cửa hàng không nhất quán | Chỉ ngôn ngữ trước nêu | Chỉ ngôn ngữ sau nêu |
|---|---|---|---|
| Tiếng Hàn, tiếng Anh | 187 (30.6%; 27.0 đến 34.3) | 177 | 10 |
| Tiếng Hàn, tiếng Trung | 134 (21.9%; 18.8 đến 25.3) | 110 | 24 |
| Tiếng Hàn, tiếng Nhật | 130 (21.2%; 18.2 đến 24.7) | 127 | 3 |
| Tiếng Hàn, tiếng Việt | 69 (11.3%; 9.0 đến 14.0) | 62 | 7 |
| Tiếng Anh, tiếng Trung | 153 (25.0%; 21.7 đến 28.6) | 36 | 117 |
| Tiếng Anh, tiếng Việt | 150 (24.5%; 21.3 đến 28.1) | 19 | 131 |
| Tiếng Anh, tiếng Nhật | 129 (21.1%; 18.0 đến 24.5) | 43 | 86 |
| Tiếng Nhật, tiếng Trung | 124 (20.3%; 17.3 đến 23.6) | 43 | 81 |
| Tiếng Trung, tiếng Việt | 115 (18.8%; 15.9 đến 22.1) | 42 | 73 |
| Tiếng Nhật, tiếng Việt | 105 (17.2%; 14.4 đến 20.3) | 18 | 87 |

<!-- src: 003-local404-consistency/analysis/out/explore_pairs.csv (system=H-mem) -->

Ở các cặp có tiếng Hàn, hầu như luôn chỉ có bên tiếng Hàn nêu. Trong 187 cửa hàng mà tiếng Hàn và tiếng Anh khác nhau, 177 cửa hàng là trường hợp chỉ tiếng Hàn nêu loại hình kinh doanh.

### 4.3 Khám phá: khi đã nêu thì có đúng không

Bảng 5. Tỷ lệ đúng trong các câu trả lời có nêu loại hình kinh doanh (điều kiện trí nhớ, tính theo câu trả lời, khoảng tin cậy 95% gộp theo cửa hàng)

| Ngôn ngữ | Câu trả lời có nêu loại hình kinh doanh | Tỷ lệ đúng |
|---|---|---|
| Tiếng Hàn | 234 | 77.4% (72.0 đến 82.7) |
| Tiếng Anh | 67 | 71.6% (60.8 đến 82.5) |
| Tiếng Nhật | 110 | 76.4% (68.4 đến 84.3) |
| Tiếng Trung | 148 | 79.1% (72.5 đến 85.6) |
| Tiếng Việt | 179 | 73.2% (66.7 đến 79.7) |

<!-- src: 003-local404-consistency/analysis/out/explore_correctness.csv (system=H-mem, kind=match_rate_among_said) -->

Tỷ lệ đúng theo từng ngôn ngữ là 71.6 đến 79.1%, các khoảng tin cậy chồng lên nhau. Trong 210 cửa hàng có từ hai ngôn ngữ trở lên nêu loại hình kinh doanh, chỉ có 4 cửa hàng (1.9%; 0.7 đến 4.8) mà một ngôn ngữ đúng còn ngôn ngữ khác sai. Thống kê theo cặp về việc ngôn ngữ nào là bên đúng chỉ có 2 đến 6 trường hợp mỗi ngôn ngữ, và số câu trả lời có nêu theo từng ngôn ngữ ở hai điều kiện tìm kiếm là 26 đến 32, nên không diễn giải.

Hình 4. Loại hình kinh doanh đã nêu có đúng không

![Trong điều kiện trí nhớ, tỷ lệ đúng trong các câu trả lời có nêu loại hình kinh doanh là tiếng Hàn 77.4%, tiếng Anh 71.6%, tiếng Nhật 76.4%, tiếng Trung 79.1%, tiếng Việt 73.2%. Chênh lệch giữa các ngôn ngữ nhỏ](figures/fig4-correct-when-said.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/explore_correctness.csv -->

### 4.4 Khám phá: địa chỉ và Llama

Địa chỉ hầu như không xuất hiện dù hỏi bằng ngôn ngữ nào. Ở 800 cửa hàng trong điều kiện trí nhớ, tỷ lệ nêu địa chỉ là tiếng Hàn 1.2%, trung bình 4 ngôn ngữ còn lại 1.3%, chênh lệch -0.1 điểm phần trăm (-0.4 đến 0.3); số cửa hàng mà chỉ một phần ngôn ngữ nêu địa chỉ là 7 (0.9%; 0.4 đến 1.8). Ở điều kiện tìm kiếm, trong 100 cửa hàng, Haiku là 11 (11.0%; 6.3 đến 18.6), Sonnet là 8 (8.0%; 4.1 đến 15.0). Số câu trả lời có nêu địa chỉ dưới 40 ở mỗi ngôn ngữ nên không diễn giải độ chính xác. Với Llama 3.1 8B, trong 230 cửa hàng mà đánh giá tình trạng hoạt động bằng tiếng Hàn, tiếng Anh và tiếng Nhật đều đã xác định, 97 cửa hàng (42.2%; 36.0 đến 48.6) có đánh giá khác nhau giữa các ngôn ngữ, và số cửa hàng mà "đang hoạt động" và "đã đóng cửa" đối chọi trực tiếp là 0.

<!-- src: 003-local404-consistency/analysis/out/explore_address.csv; explore_lmem_status.csv -->

## 5 Thảo luận

Trong điều kiện trí nhớ, Claude Haiku nêu loại hình kinh doanh của cùng một cửa hàng thường xuyên nhất khi được hỏi bằng tiếng Hàn và hiếm nhất khi được hỏi bằng tiếng Anh. Việc tiếng Việt đứng thứ hai sau tiếng Hàn khó giải thích chỉ bằng kết quả trước đây rằng ngôn ngữ càng nhiều dữ liệu thì khả năng nhớ lại càng cao (Jiang và cộng sự 2020).

Hình 5. Cùng một cửa hàng, câu trả lời khác nhau theo ngôn ngữ

![Trong 612 cửa hàng ở điều kiện trí nhớ, 260 cửa hàng (42%) có lúc nêu, có lúc không nêu loại hình kinh doanh tùy theo ngôn ngữ; số còn lại thì cả 5 ngôn ngữ đều nêu hoặc đều không nêu](figures/fig5-split-shops.svg)

<!-- src: 003-local404-consistency/analysis/make_figures.py; analysis/out/explore_inconsistency.csv -->

Tần suất nêu khác nhau theo ngôn ngữ, nhưng tỷ lệ đúng thì tương tự. Trong các cửa hàng có từ hai ngôn ngữ trở lên nêu, đánh giá khác nhau chỉ ở 1.9%. Ngôn ngữ thay đổi "có nêu hay không" và hầu như không thay đổi "có đúng hay không". Lý do mà Qi và cộng sự (2023) nêu ra để xem xét tính nhất quán và độ chính xác riêng rẽ cũng thể hiện trong dữ liệu này. Khi bật tìm kiếm web, chênh lệch giữa các ngôn ngữ thu hẹp và tỷ lệ nêu tăng lên. Có thể vì tìm kiếm đã đến cùng một nguồn bất kể ngôn ngữ, nhưng với mẫu 70 cửa hàng, khả năng vẫn còn chênh lệch nhỏ chưa được loại trừ.

Một phần câu trả lời có nêu loại hình kinh doanh trong điều kiện trí nhớ có thể là đoán từ tên cửa hàng. Nếu tên cửa hàng có những từ như "gà rán" hay "quán sashimi", AI có thể nêu loại hình kinh doanh dù không biết cửa hàng đó, và việc đoán này có thể dễ xảy ra hơn với câu hỏi tiếng Hàn. Khả năng này chưa được kiểm chứng bằng dữ liệu lần này.

### Việc cửa hàng có thể làm ngay

- Hãy trực tiếp hỏi AI về cửa hàng của mình bằng ngôn ngữ mà khách nước ngoài dùng. Có 177 trong 612 cửa hàng mà loại hình kinh doanh được nêu khi hỏi bằng tiếng Hàn nhưng không được nêu khi hỏi bằng tiếng Anh.
- Nếu câu trả lời tiếng Hàn sai thì câu trả lời bằng các ngôn ngữ khác nhiều khả năng cũng sai. Trong 210 cửa hàng có từ hai ngôn ngữ trở lên nêu loại hình kinh doanh, chỉ 4 cửa hàng có đánh giá khác nhau.
- AI có bật tìm kiếm web cho chênh lệch theo ngôn ngữ nhỏ (dựa trên 70 cửa hàng). Kết quả khác nhau tùy vào AI ở điều kiện nào đang mô tả cửa hàng.

## 6 Hạn chế

1. Đánh giá là đánh giá bằng từ điển và đánh giá có LLM hỗ trợ của báo cáo số 2. Tỷ lệ thống nhất giữa hai phương pháp trong đánh giá loại hình kinh doanh là 73% (kappa 0.46, bảng 7 của báo cáo số 2), nên cả việc có nêu hay không lẫn việc đúng hay không đều chứa sai số đánh giá.
2. Hai điều kiện tìm kiếm chỉ có 70 cửa hàng nên năng lực kiểm định thấp. Không được ủng hộ không có nghĩa là không có chênh lệch.
3. Không thể phân biệt nguyên nhân câu hỏi tiếng Hàn nêu nhiều hơn là do khác biệt kiến thức theo ngôn ngữ của mô hình, do khác biệt trong câu hỏi (tên cửa hàng và quận huyện viết bằng tiếng Hàn ở mọi ngôn ngữ), hay do đoán loại hình kinh doanh từ tên cửa hàng. Ảnh hưởng của môi trường thu thập và chỉ dẫn trong báo cáo số 2 cũng không tách ra được.
4. Thời điểm thu thập là một thời điểm duy nhất, từ 2026-10-21 đến ngày 24.

## 7 Đạo đức và xung đột lợi ích

Tên và địa chỉ cửa hàng của các hộ kinh doanh cá thể đã được loại khỏi dữ liệu công khai, và ghi chú này không dùng nguyên văn câu trả lời. Define404, nơi tác giả làm việc, đang chuẩn bị dịch vụ giám sát câu trả lời của AI và chẩn đoán mức độ hiển thị trên AI cho từng cửa hàng. Sản phẩm của công ty không nằm trong đối tượng khảo sát. Không có tài trợ bên ngoài.

## 8 Cách tái lập

- Đầu vào: kết quả đánh giá trong kho công khai của báo cáo số 2, 001-local404/analysis/out_final/judgments.csv (SHA-256 37220e4ee92e815a968f91d1b4c80f4b3e84aa0d95e3415fc269bb3fab01bf26). https://github.com/johndefine404/define404-research-public
- Mã thống kê: 001-local404/analysis/stats_lib.py của báo cáo số 2 (SHA-256 206d5e4191f0c436305866daa90ca328b92afde972cb908aefac0f0101ae94fb), dùng nguyên không sửa
- Mã phân tích: 003-local404-consistency/analysis/run_analysis.py. Chạy bằng python analysis/run_analysis.py. Kiểm thử với đầu vào giả: analysis/tests/test_fake_input.py
- Kết quả: h1.csv, h2.csv, h3.csv, holm.csv, explore_*.csv, data_inventory.csv, results.json trong analysis/out/. Các con số trong bản thảo chỉ được chép từ những tệp này
- Hình: analysis/make_figures.py đọc số từ tệp kết quả và tạo report/figures/*.svg
- Đăng ký trước: commit 7169864742847ee54118b42f23ef2285f705e97d của kho nghiên cứu (2026-10-28T23:39:04+07:00). prereg.md được commit trước khi chạy phân tích
- Phụ thuộc: numpy, pandas, scipy (analysis/requirements.txt)

## Tài liệu tham khảo

- Chua, L. và cộng sự (2024). Crosslingual Capabilities and Knowledge Barriers in Multilingual Large Language Models. arXiv:2406.16135. https://arxiv.org/abs/2406.16135
- Jiang, Z., Anastasopoulos, A., Araki, J., Ding, H., Neubig, G. (2020). X-FACTR: Multilingual Factual Knowledge Retrieval from Pretrained Language Models. arXiv:2010.06189. https://arxiv.org/abs/2010.06189
- Kassner, N., Dufter, P., Schütze, H. (2021). Multilingual LAMA: Investigating Knowledge in Multilingual Pretrained Language Models. arXiv:2102.00894. https://arxiv.org/abs/2102.00894
- Qi, J., Fernández, R., Bisazza, A. (2023). Cross-Lingual Consistency of Factual Knowledge in Multilingual Language Models. arXiv:2310.10378. https://arxiv.org/abs/2310.10378
- Define404 Research (2026). Local404: AI có còn nói những cửa hàng trong khu dân cư đã đóng cửa vẫn đang hoạt động không (tiếng Hàn). https://define404.com/report/002-local404-closed-shops/
