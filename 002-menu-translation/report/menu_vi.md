# Hỏi AI tên tiếng nước ngoài của món Hàn, câu trả lời trùng với chuẩn của chính phủ đến mức nào

Đây là bản dịch. Bản gốc là bản tiếng Hàn, phiên bản 1: https://define404.com/report/004-hansik-menu-translation/

Khảo sát hỏi Claude có bật tìm kiếm web tên tiếng Anh và tiếng Nhật của 180 món ăn Hàn Quốc, rồi đối chiếu với cách viết chuẩn của Viện Xúc tiến Ẩm thực Hàn Quốc (Korean Food Promotion Institute)

- Tác giả: Define404 Research
- Ngày: 2026-10-29
- Đăng ký trước: commit 9f84ace của kho nghiên cứu (2026-10-28 23:41 ICT)
- DOI: https://doi.org/10.5281/zenodo.23739014
- Xung đột lợi ích: Define404, nơi tác giả làm việc, đang chuẩn bị dịch vụ kiểm tra bằng AI cho cửa hàng nhỏ và đang cân nhắc đưa việc kiểm tra cách viết tiếng nước ngoài trên thực đơn vào danh mục. Sản phẩm của chính Define404 không nằm trong đối tượng khảo sát.

## Tóm tắt

Chúng tôi khảo sát xem khi chủ quán hỏi trợ lý AI tên tiếng Anh, tiếng Nhật của món Hàn, câu trả lời có trùng với cách viết chuẩn mà chính phủ đã công bố hay không. Đáp án chuẩn là 778 mục trong bảng "Cách viết tên món ăn Hàn Quốc bằng tiếng nước ngoài" trên Cổng Hansik của Viện Xúc tiến Ẩm thực Hàn Quốc. Chúng tôi chia tầng theo 11 nhóm món để rút 180 món, rồi đặt trong tình huống chủ quán đang làm thực đơn, hỏi Claude Sonnet 5.5 có bật tìm kiếm web 180 câu tiếng Anh và 180 câu tiếng Nhật. Từ mỗi câu trả lời, chúng tôi lấy ra một tên món và đối chiếu với chuẩn theo quy tắc. Sau chuẩn hóa, tỷ lệ câu trả lời trùng hoàn toàn với chuẩn (khớp chặt) là 18.3% ở tiếng Anh và 18.3% ở tiếng Nhật, bằng nhau. Giả thuyết chính rằng tiếng Anh cao hơn tiếng Nhật không được ủng hộ. Khi tính cả câu trả lời gần giống (khớp lỏng trở lên), hai bên tách xa: tiếng Anh 75.0%, tiếng Nhật 40.0%. Chỉ 2 trong 360 câu trả lời dẫn trang web chuẩn của chính phủ làm nguồn, nên giả thuyết phụ không được diễn giải.

### Kết quả chính

- Câu trả lời viết đúng hệt chuẩn của chính phủ: tiếng Anh 33 trên 180 (18.3%; khoảng tin cậy 95% 13.4~24.6), tiếng Nhật cũng 33 trên 180 (18.3%; 13.4~24.6). Chênh lệch theo cặp giữa hai ngôn ngữ là 0.0%p (-8.2~8.2).
- Tính cả câu trả lời gần giống chuẩn: tiếng Anh 135 trên 180 (75.0%; 68.2~80.8), tiếng Nhật 72 (40.0%; 33.1~47.3). Ở tiếng Nhật, sáu phần mười (60.0%; 52.7~66.9) là tên khác với chuẩn.
- Câu trả lời dẫn trang web của Viện Xúc tiến Ẩm thực Hàn Quốc làm nguồn: 2 trên 360 (0.6%; 0.2~2.0). Tiếng Anh 2, tiếng Nhật 0.
- Quy tắc đã đăng ký bỏ phần trong ngoặc và chỉ so tên chính. Nếu xem cả phần giải thích trong ngoặc, câu trả lời có chứa tên chuẩn là 37.2% ở tiếng Anh (30.5~44.5) và 28.3% ở tiếng Nhật (22.3~35.3) (phân tích khám phá bổ sung sau khi xem kết quả).

<!-- src: 002-menu-translation/analysis/out/results.json#preregistered.rates_en, rates_ja, H1_en_minus_ja_strict_paired; exploratory.cites_hansik_rate; 002-menu-translation/analysis/out/explore_contains.csv -->

## 1 Giới thiệu

Khách nước ngoài tăng lên, quán ăn trong khu phố cũng làm thực đơn tiếng Anh, tiếng Nhật. Thực đơn chỉ có vài món nên thuê công ty dịch thì không đáng, vì vậy chủ quán hỏi trợ lý AI "món này viết tiếng Anh thế nào". Để thống nhất cách viết tiếng nước ngoài trên thực đơn, chính phủ đã công bố cách viết chuẩn dưới tên Bộ Nông nghiệp, Thực phẩm và Nông thôn và Viện Xúc tiến Ẩm thực Hàn Quốc. Nếu AI đưa ra tên khác với chuẩn đó, chủ quán sẽ làm ra thực đơn lệch chuẩn mà không biết.

Khảo sát này đưa khoảng cách đó về dạng đo được. Chúng tôi lấy cách viết chuẩn do Viện Xúc tiến Ẩm thực Hàn Quốc công bố làm đáp án, hỏi cùng một món bằng tiếng Anh và tiếng Nhật, rồi đối chiếu câu trả lời với chuẩn theo quy tắc. Chọn mẫu, đặt câu hỏi, chấm và phân tích đều được viết thành mã, nên có thể chạy lại đúng quy trình. Giả thuyết và kế hoạch phân tích đã được commit vào kho nghiên cứu để đăng ký trước khi thu thập.

Khảo sát này chỉ đo việc câu trả lời có trùng với cách viết chuẩn của chính phủ hay không. Câu trả lời khác chuẩn không hẳn là dịch sai. Nhưng chuẩn là căn cứ chính phủ công bố để thống nhất cách viết thực đơn, nên nếu chủ quán đưa nguyên câu trả lời của AI lên thực đơn thì thực đơn sẽ có cách viết lệch chuẩn.

Đóng góp gồm ba điểm. Thứ nhất, đây là phép đo đầu tiên đối chiếu câu trả lời của AI về tên món Hàn với chuẩn chính thức của chính phủ (trong phạm vi đã kiểm tra ở Mục 2). Thứ hai, tiếng Anh và tiếng Nhật được so sánh theo cặp trên cùng một món. Thứ ba, mã thu thập nguồn, rút mẫu cố định seed, chấm theo quy tắc và phân tích được công khai, nên có thể lặp lại cùng khảo sát với AI khác hoặc ở thời điểm khác.

## 2 Nghiên cứu liên quan

Chỉ liệt kê các nghiên cứu đã mở nguyên văn để kiểm tra (ngày kiểm tra 2026-10-28).

Yao và cộng sự (2024) xây dựng kho ngữ liệu song song chứa các mục đặc thù văn hóa cho 6 cặp ngôn ngữ và báo cáo rằng mô hình ngôn ngữ lớn dùng kiến thức văn hóa trong dịch thuật tốt hơn dịch máy nơ-ron[1]. Thực đơn Hàn Quốc không được xét riêng. Zhang và cộng sự (2024) xây dựng bộ dữ liệu thực đơn Trung-Anh và đề xuất cách tự động nhận diện mục đặc thù văn hóa cùng chiến lược dịch[2]. Chỉ xét thực đơn tiếng Trung. Yuan và cộng sự (2026) đề xuất bộ dữ liệu dịch có nhận thức văn hóa dựa trên tiểu thuyết và khung đánh giá; phần tóm tắt không nói có bao gồm tiếng Hàn hay không[3]. Zeng và cộng sự (2026) đánh giá 12 mô hình đa phương thức trên 10 ngôn ngữ bằng 4,870 câu hỏi trắc nghiệm về ảnh thực đơn và nấu ăn[4]. Không đối chiếu đáp án dịch với chuẩn của chính phủ. Lee (2025) so sánh ChatGPT và Papago khi dịch Hàn-Anh 590 cặp lời thoại phim truyền hình, không xét tên món ăn[5].

Không bài nào trong năm bài đo xem trợ lý AI có bật tìm kiếm web đưa ra cách viết trùng chuẩn chính thức của chính phủ cho tên món Hàn đến mức nào. Khảo sát này lấp khoảng trống đó.

<!-- src: 002-menu-translation/gate.md#3 -->

## 3 Phương pháp

Hình 1. Chúng tôi đã khảo sát như thế này

![Trình tự: rút 180 món Hàn, hỏi bằng tiếng Anh và tiếng Nhật, đối chiếu 360 câu trả lời của Claude có tìm kiếm web với cách viết chuẩn của chính phủ rồi chia thành giống hệt, gần giống, khác](figures/fig1-flow.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/results.json -->

### 3.1 Nguồn đáp án và mẫu

Nguồn đáp án là bảng "Cách viết tên món ăn Hàn Quốc bằng tiếng nước ngoài" trên Cổng Hansik của Viện Xúc tiến Ẩm thực Hàn Quốc (hansik.or.kr, thu thập ngày 2026-10-28, 778 mục). Các cột gồm số thứ tự, tên món, phiên âm La-tinh, tiếng Anh, tiếng Nhật, tiếng Trung giản thể và phồn thể; nguồn được ghi là Bộ Nông nghiệp, Thực phẩm và Nông thôn, Viện Xúc tiến Ẩm thực Hàn Quốc, Bộ Văn hóa, Thể thao và Du lịch, Viện Quốc ngữ Quốc gia, Tổng cục Du lịch Hàn Quốc và Cục Phát triển Nông thôn. Không có ô trống hay tên món trùng lặp nên không bỏ hàng nào. SHA-256 của tệp thu thập nằm ở Mục 8.

Các tầng là 11 nhóm món, xác định theo từ cuối của tên món tiếng Hàn. Mỗi tầng được phân bổ theo tỷ lệ tổng thể nhưng tối thiểu 5 món, tổng cộng rút 180 món. Ứng viên trong tầng được xếp theo số thứ tự, xáo bằng seed 20261028 rồi lấy từ đầu. Cỡ mẫu được đặt là 180 để đủ 175 món cần thiết nhằm phát hiện chênh lệch theo cặp 15%p giữa hai ngôn ngữ ở giả thuyết chính với mức ý nghĩa 5% (một phía) và lực kiểm định 80%. Phương sai của chênh lệch theo cặp lấy giá trị xấu nhất: câu trả lời hai ngôn ngữ không tương quan và tỷ lệ 0.5.

Bảng 1. Cấu trúc mẫu (nhóm món xác định theo quy tắc từ cuối tên món nên có thể khác phân loại chính thức)

| Nhóm món | Tổng thể | Mẫu |
|---|---|---|
| Nướng, xào, chiên | 174 | 40 |
| Rau trộn, kimchi, món phụ | 133 | 30 |
| Canh, súp | 106 | 24 |
| Cơm, cháo | 92 | 21 |
| Hấp, kho, thịt luộc | 74 | 17 |
| Mì | 51 | 11 |
| Khác | 44 | 10 |
| Lẩu, canh đặc | 39 | 9 |
| Bánh gạo, bánh kẹo truyền thống, đồ uống | 38 | 8 |
| Suất ăn, mâm cơm | 7 | 5 |
| Tương, gia vị | 20 | 5 |
| Tổng | 778 | 180 |

<!-- src: 002-menu-translation/prereg.md#3; 002-menu-translation/sampling/sample_v1_log.txt -->

### 3.2 Câu hỏi

Mỗi món, mỗi ngôn ngữ một câu hỏi: 180 câu tiếng Anh và 180 câu tiếng Nhật. Câu hỏi được viết theo tình huống chủ quán Hàn Quốc ở Hàn Quốc đang làm thực đơn tiếng nước ngoài, yêu cầu viết một tên món ở dòng đầu theo dạng "NAME: ..." rồi giải thích bằng một hai câu. Tên món được đưa vào nguyên dạng tiếng Hàn ở cả hai ngôn ngữ. Câu hỏi không chứa các từ chuẩn, Viện Xúc tiến Ẩm thực Hàn Quốc hay hướng dẫn. Mẫu câu hỏi ở Phụ lục A (collect/question_templates.json v1.0).

Mỗi ngôn ngữ được xáo bằng seed 20261028 và chia thành 18 lô, mỗi lô 10 câu. Một lô chỉ gồm một ngôn ngữ và các món khác nhau.

### 3.3 Hệ thống trả lời

Bảng 2. Hệ thống trả lời

| Mô hình | Điều kiện | Số câu | Câu trả lời hợp lệ |
|---|---|---|---|
| Claude Sonnet 5.5 | Tìm kiếm web, bắt buộc tìm kiếm ở mỗi câu | 360 (tiếng Anh 180, tiếng Nhật 180) | 360 |

<!-- src: 002-menu-translation/log.md; 002-menu-translation/analysis/out/results.json#n_items -->

Bên trả lời được gọi dưới dạng tác tử con và không được cho biết mục đích khảo sát cũng như đáp án. Đầu phần chỉ dẫn nêu rõ nhiệm vụ không liên quan đến hội thoại trước và phải trả lời bằng ngôn ngữ của câu hỏi. Các lô chạy song song 3 lô một lần, thu thập diễn ra từ đêm 2026-10-28 sang ngày 29. Cả 360 câu đều nhận được trả lời và không câu nào bỏ qua tìm kiếm. Một câu ghi trong trả lời rằng lần tìm kiếm thứ hai bị chặn vì giới hạn, nhưng lần đầu đã chạy nên vẫn tính là hợp lệ. Không chạy thử riêng; chúng tôi kiểm tra định dạng ở 2 lô đầu rồi dùng luôn các câu trả lời đó làm dữ liệu chính.

### 3.4 Chấm

Quy tắc chấm (judge/rules.md v1.0) được cố định trước khi thu thập và chỉ dùng mã chấm tự động theo quy tắc (judge/auto_judge.py). Từ dòng "NAME:" đầu tiên của câu trả lời, lấy ra một ứng viên tên món. Nếu có từ hai ứng viên trở lên như "A / B" thì lấy cái đầu và bỏ phần trong ngoặc. Không có câu trả lời nào trích xuất thất bại nên số câu chấm thủ công là 0.

Với tiếng Anh, ứng viên được chuyển thành chữ thường, chuẩn hóa Unicode (NFKC), bỏ phần trong ngoặc, bỏ dấu câu, bỏ mạo từ và các từ and, with, thống nhất biến thể phiên âm (kimchi/gimchi, tteok/ddeok/dduk, v.v.); nếu sau đó giống hệt cách viết tiếng Anh chuẩn thì là khớp chặt. Nếu hệ số Jaccard của tập từ từ 0.5 trở lên hoặc chứa trọn phiên âm La-tinh của chuẩn thì là khớp lỏng. Còn lại là không khớp. Với tiếng Nhật, sau NFKC, bỏ khoảng trắng, dấu chấm giữa, dấu trường âm, phần trong ngoặc và bỏ qua việc có hay không có âm ngắt (sokuon), nếu giống hệt cách viết tiếng Nhật chuẩn thì là khớp chặt; nếu hệ số Dice trên 2-gram ký tự từ 0.5 trở lên hoặc chứa trọn chuẩn thì là khớp lỏng. Không trả lời hoặc chỉ nói không biết là không đưa ra. Nếu danh sách nguồn của câu trả lời có hansik.or.kr thì ghi là "có dẫn nguồn chuẩn".

Bảng 3. Ví dụ chấm (5 trong 180 món của mẫu, cách viết chuẩn trích từ Cổng Hansik của Viện Xúc tiến Ẩm thực Hàn Quốc)

| Món | Ngôn ngữ | Cách viết chuẩn | Tên món trong câu trả lời của AI | Kết quả chấm |
|---|---|---|---|---|
| 어간장 (eo-ganjang) | Tiếng Anh | Fish Soy Sauce | Fish Soy Sauce (Eo-ganjang) | Khớp chặt |
| 비빔밥 (bibimbap) | Tiếng Nhật | ビビンバ | ビビンバ | Khớp chặt |
| 새우튀김 (saeu-twigim) | Tiếng Anh | Deep-fried Shrimp | Crispy Fried Shrimp | Khớp lỏng |
| 계란찜 (gyeran-jjim) | Tiếng Nhật | 茶碗蒸し | ケランチム(韓国式卵蒸し) | Không khớp |
| 따로국밥 (ttaro-gukbap) | Tiếng Nhật | タロクッパ | タログッパ(別盛りクッパ) | Không khớp |

<!-- src: 002-menu-translation/judge/judged.csv (M134-en, M014-ja, M148-en, M066-ja, M011-ja) -->

### 3.5 Phân tích

Mã phân tích là analysis/run_analysis.py và chỉ dùng thư viện chuẩn. Mọi tỷ lệ đều kèm khoảng tin cậy Wilson 95%. Mỗi món có một câu trả lời cho mỗi ngôn ngữ nên tỷ lệ theo món cũng chính là tỷ lệ theo cụm. Giả thuyết chính H1 tính cho mỗi món (khớp chặt tiếng Anh - khớp chặt tiếng Nhật) rồi báo cáo trung bình chênh lệch theo cặp, sai số chuẩn, khoảng tin cậy và kiểm định một phía. Giả thuyết phụ H2 là chênh lệch tỷ lệ khớp chặt giữa nhóm có dẫn nguồn chuẩn và nhóm không dẫn trong các câu tiếng Anh. Hai giả thuyết được hiệu chỉnh bằng phương pháp Holm. Ô có mẫu dưới 40 không được diễn giải. Phân tích không có trong đăng ký trước được đánh dấu là phân tích khám phá, và phân tích bổ sung sau khi xem kết quả được ghi rõ như vậy.

Đăng ký trước là việc commit prereg.md vào kho nghiên cứu (commit 9f84ace, 2026-10-28 23:41 ICT). Sau khi đăng ký, prereg.md và quy tắc chấm không được sửa.

## 4 Kết quả

### 4.1 Câu trả lời giống hệt chuẩn của chính phủ (H1)

Bảng 4. Phân bố kết quả chấm theo ngôn ngữ (trong ngoặc là khoảng tin cậy Wilson 95%, n mỗi bên là 180)

| Kết quả chấm | Tiếng Anh | Tiếng Nhật |
|---|---|---|
| Khớp chặt | 33 (18.3%; 13.4~24.6) | 33 (18.3%; 13.4~24.6) |
| Khớp lỏng | 102 (56.7%; 49.4~63.7) | 39 (21.7%; 16.3~28.2) |
| Không khớp | 45 (25.0%; 19.2~31.8) | 108 (60.0%; 52.7~66.9) |
| Không đưa ra | 0 (0.0%; 0.0~2.1) | 0 (0.0%; 0.0~2.1) |
| Khớp lỏng trở lên (chặt + lỏng) | 135 (75.0%; 68.2~80.8) | 72 (40.0%; 33.1~47.3) |

<!-- src: 002-menu-translation/analysis/out/results.json#preregistered.rates_en, rates_ja -->

Hình 2. Nếu hỏi 100 món (số câu trả lời được thu về 100 ô và làm tròn)

![Tiếng Anh trong 100: giống hệt 18, gần giống 57, khác 25. Tiếng Nhật: giống hệt 18, gần giống 22, khác 60](figures/fig2-100-menus.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/results.json -->

Tỷ lệ câu trả lời có tên món giống hệt chuẩn của chính phủ sau chuẩn hóa là 18.3% ở tiếng Anh và 18.3% ở tiếng Nhật, bằng nhau. Trung bình chênh lệch theo cặp trên 180 món là 0.0%p (khoảng tin cậy 95% -8.2~8.2), p một phía = 0.500, p hiệu chỉnh Holm = 1.000. H1, rằng tỷ lệ khớp chặt tiếng Anh cao hơn tiếng Nhật, không được ủng hộ. Cả hai ngôn ngữ đều đưa ra tên món ở mọi câu hỏi.

Bảng 5. Kết quả kiểm định các giả thuyết đã đăng ký trước

| Giả thuyết | Kết quả |
|---|---|
| H1 Tiếng Anh > tiếng Nhật (khớp chặt, theo cặp) | 18.3% so với 18.3%. Chênh lệch theo cặp 0.0%p (-8.2~8.2), p một phía = 0.500, Holm p = 1.000. Không được ủng hộ |
| H2 Có dẫn nguồn chuẩn > không dẫn (khớp chặt tiếng Anh) | Có dẫn 2 câu (0/2), không dẫn 178 câu (33/178, 18.5%; 13.5~24.9). Ô có dẫn dưới 40 nên không diễn giải |

<!-- src: 002-menu-translation/analysis/out/results.json#preregistered.H1_en_minus_ja_strict_paired, H2_strict_by_hansik_citation_en -->

### 4.2 Khi tính cả câu trả lời gần giống (khớp lỏng)

Hình 3. Tính cả câu trả lời gần giống thì tiếng Anh tăng mạnh, tiếng Nhật tăng ít

![Câu trả lời viết giống hệt là 18% ở tiếng Anh và 18% ở tiếng Nhật, bằng nhau, nhưng câu trả lời ít nhất gần giống là 75% ở tiếng Anh và 40% ở tiếng Nhật](figures/fig3-strict-vs-loose.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/results.json -->

Tỷ lệ "khớp lỏng trở lên", gồm khớp chặt cộng khớp lỏng, là 75.0% ở tiếng Anh (68.2~80.8) và 40.0% ở tiếng Nhật (33.1~47.3). Câu trả lời tiếng Anh thường có hơn một nửa số từ trùng với chuẩn hoặc chứa phiên âm La-tinh của chuẩn (khớp lỏng 56.7%). Ở tiếng Nhật, tên khác với chuẩn chiếm 60.0% (52.7~66.9), là ô lớn nhất. Các trường hợp như gyeran-jjim (계란찜) ở Bảng 3, chuẩn là bản dịch tiếng Nhật (茶碗蒸し) nhưng câu trả lời viết cách phát âm tiếng Hàn bằng katakana (ケランチム), thuộc nhóm này. Chênh lệch tỷ lệ khớp lỏng trở lên giữa hai ngôn ngữ là phân tích khám phá, không phải giả thuyết đã đăng ký trước.

### 4.3 Câu trả lời có dẫn trang web chuẩn của chính phủ (H2)

Hình 4. Hầu như không có câu trả lời nào dẫn trang web chuẩn của chính phủ làm nguồn

![Xếp 360 câu trả lời thành các chấm thì chỉ 2 câu dẫn trang web của Viện Xúc tiến Ẩm thực Hàn Quốc làm nguồn](figures/fig4-cited-hansik.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/results.json -->

Trong 360 câu trả lời, số câu có trang web của Viện Xúc tiến Ẩm thực Hàn Quốc (hansik.or.kr) trong danh sách nguồn là 2 (0.6%; 0.2~2.0). Tiếng Anh 2 trên 180 (1.1%; 0.3~4.0), tiếng Nhật 0 trên 180 (0.0%; 0.0~2.1). 2 câu đó là câu trả lời tiếng Anh cho dongtae-jeon (동태전) và ttaro-gukbap (따로국밥), cả hai đều khớp lỏng. Nhóm có dẫn chỉ có 2 câu nên H2 không được diễn giải. Tỷ lệ khớp chặt của 178 câu không dẫn là 18.5% (13.5~24.9). Dù mỗi câu đều có tìm kiếm web, câu trả lời hầu như không chạm tới trang web chuẩn của chính phủ.

<!-- src: 002-menu-translation/analysis/out/results.json#exploratory.cites_hansik_rate; 002-menu-translation/analysis/out/explore_contains.csv (all, cites_hansik_or_kr); 002-menu-translation/judge/judged.csv (cites_hansik=1: M145-en, M011-en) -->

### 4.4 Phân tích khám phá

Tỷ lệ khớp chặt tiếng Anh theo nhóm món ở Bảng 6. Ô duy nhất có mẫu từ 40 trở lên là nướng, xào, chiên (40 món), với tỷ lệ khớp chặt 25.0% (14.2~40.2). Các ô còn lại dưới 40 nên không diễn giải.

Bảng 6. Khớp chặt tiếng Anh theo nhóm món (phân tích khám phá, ô dưới 40 không diễn giải)

| Nhóm món | n | Khớp chặt | Tỷ lệ (95% CI) | Diễn giải |
|---|---|---|---|---|
| Nướng, xào, chiên | 40 | 10 | 25.0% (14.2~40.2) | Diễn giải |
| Rau trộn, kimchi, món phụ | 30 | 1 | 3.3% (0.6~16.7) | Dưới 40 |
| Canh, súp | 24 | 8 | 33.3% (18.0~53.3) | Dưới 40 |
| Cơm, cháo | 21 | 5 | 23.8% (10.6~45.1) | Dưới 40 |
| Hấp, kho, thịt luộc | 17 | 6 | 35.3% (17.3~58.7) | Dưới 40 |
| Mì | 11 | 0 | 0.0% (0.0~25.9) | Dưới 40 |
| Khác | 10 | 0 | 0.0% (0.0~27.8) | Dưới 40 |
| Lẩu, canh đặc | 9 | 1 | 11.1% (2.0~43.5) | Dưới 40 |
| Bánh gạo, bánh kẹo truyền thống, đồ uống | 8 | 1 | 12.5% (2.2~47.1) | Dưới 40 |
| Suất ăn, mâm cơm | 5 | 0 | 0.0% (0.0~43.4) | Dưới 40 |
| Tương, gia vị | 5 | 1 | 20.0% (3.6~62.4) | Dưới 40 |

<!-- src: 002-menu-translation/analysis/out/results.json#exploratory.strict_by_category_en -->

Trong 45 câu không khớp tiếng Anh, "không khớp nguyên liệu", tức thiếu từ nguyên liệu chính của chuẩn và thay bằng từ nguyên liệu khác, có 2 câu (4.4%; 1.2~14.8). Phần lớn câu không khớp tiếng Anh khác ở cách diễn đạt chứ không phải nguyên liệu. Đưa ra nhiều tên và trích xuất thất bại đều là 0.

<!-- src: 002-menu-translation/analysis/out/results.json#exploratory.ingredient_mismatch_among_en_mismatch, flags -->

Dưới đây là phân tích khám phá bổ sung sau khi xem kết quả. Quy tắc đã đăng ký bỏ phần trong ngoặc và chỉ so tên chính. Vì vậy câu trả lời có giải thích trong ngoặc như "ケランチム(韓国式卵蒸し)" chỉ được chấm theo tên ngoài ngoặc. Nếu đếm riêng các câu trả lời mà toàn bộ dòng tên món, kể cả phần trong ngoặc, có chứa tên chuẩn thì tiếng Anh là 67 trên 180 (37.2%; 30.5~44.5) và tiếng Nhật là 51 trên 180 (28.3%; 22.3~35.3) (analysis/explore_contains.py).

Hình 5. Nếu xem cả phần giải thích trong ngoặc (phân tích khám phá bổ sung sau khi xem kết quả)

![Chỉ xem tên chính thì câu trả lời giống hệt chuẩn là 18% ở tiếng Anh và 18% ở tiếng Nhật, nhưng tính cả phần giải thích trong ngoặc thì câu trả lời có chứa tên chuẩn là 37% ở tiếng Anh và 28% ở tiếng Nhật](figures/fig5-with-parentheses.svg)

<!-- src: 002-menu-translation/analysis/make_figures.py; 002-menu-translation/analysis/out/explore_contains.csv; 002-menu-translation/analysis/out/results.json -->

## 5 Thảo luận

Khảo sát này có hai điểm cốt lõi. Thứ nhất, xác suất nhận được tên món giống hệt chuẩn của chính phủ là khoảng một phần năm (18.3%) ở cả tiếng Anh lẫn tiếng Nhật, không khác nhau theo ngôn ngữ. Thứ hai, khi tính cả câu trả lời gần giống, tiếng Anh (75.0%) và tiếng Nhật (40.0%) tách xa nhau. Câu trả lời tiếng Anh thường là tên mô tả có từ trùng với chuẩn (khớp lỏng 56.7%). Câu trả lời tiếng Nhật có những tên chuyển cách phát âm tiếng Hàn sang katakana như gyeran-jjim ở Bảng 3, và những câu đó có ít ký tự trùng với bản dịch tiếng Nhật chuẩn. Cùng một AI, cùng món, cùng tình huống, nhưng mức độ gần chuẩn vẫn thay đổi theo ngôn ngữ.

Đọc từ phía cửa hàng thì thế này. Tên món tiếng Anh mà AI đưa ra thường có nghĩa tương đương chuẩn nhưng hiếm khi viết giống hệt. Ở tiếng Nhật, viết giống hệt đã hiếm, viết theo dạng có nghĩa tương đương cũng chưa được một nửa. Tên món khác chuẩn không hẳn là dịch sai, nhưng chủ quán muốn thực đơn theo chuẩn của chính phủ thì không nên chép nguyên câu trả lời của AI mà phải tự kiểm tra chuẩn.

Điều đáng chú ý là tìm kiếm web không chạm tới trang web chuẩn của chính phủ. Mỗi câu đều có tìm kiếm, nhưng câu trả lời dẫn trang web của Viện Xúc tiến Ẩm thực Hàn Quốc làm nguồn chỉ có 2 trong 360. Nhiều câu trả lời ghi rằng không tìm thấy tên tiếng Anh chuẩn chính thức (ví dụ câu trả lời tiếng Anh cho usamgyeop-sukju-bokkeum (우삼겹숙주볶음): "I found no official standard English name for this dish"). Dù chuẩn đã công khai, nếu không lên đầu kết quả tìm kiếm thì AI sẽ tự đặt tên mà không biết chuẩn tồn tại. Chúng tôi không đếm số trường hợp này và cũng không kiểm định nguyên nhân.

Nếu xem cả phần giải thích trong ngoặc, câu trả lời có chứa tên chuẩn tăng lên 37.2% ở tiếng Anh và 28.3% ở tiếng Nhật. Nghĩa là có chừng ấy câu trả lời viết tên chính theo cách riêng rồi thêm tên chuẩn trong ngoặc. Dù vậy, sáu phần mười câu tiếng Anh và bảy phần mười câu tiếng Nhật vẫn không có tên chuẩn ngay cả trong ngoặc. Phân tích này được bổ sung sau khi xem kết quả nên không phải kiểm định giả thuyết.

## 6 Hạn chế

1. Hệ thống trả lời chỉ có một điều kiện là Claude Sonnet 5.5 với tìm kiếm web. Không thể khái quát cho trợ lý AI khác hay điều kiện không có tìm kiếm.
2. Chỉ có một mẫu câu hỏi. Yêu cầu định dạng "NAME:" và bối cảnh chủ quán có thể ảnh hưởng đến câu trả lời, hỏi bằng cách khác có thể cho kết quả khác.
3. Chấm theo quy tắc có hạn chế. Vì bỏ phần trong ngoặc và chỉ so tên chính nên câu trả lời viết tên chuẩn trong ngoặc sẽ thành không khớp hoặc khớp lỏng (khám phá ở Mục 4.4). Ngoài ra, cùng nghĩa nhưng khác từ cũng là không khớp. Trường hợp ttaro-gukbap ở Bảng 3 (タロクッパ so với タログッパ) thành không khớp chỉ vì lệch một ký tự. Ngưỡng khớp lỏng (Jaccard và Dice 0.5) được định trước khi thu thập nhưng là giá trị tùy chọn.
4. Cách viết chuẩn chỉ là một căn cứ chính thức, không phải đáp án duy nhất. Chất lượng dịch của các câu trả lời khác chuẩn không được khảo sát này đo.
5. Nhóm món được xác định theo quy tắc từ cuối tên món nên có thể khác phân loại chính thức, và chỉ một ô theo nhóm có mẫu từ 40 trở lên.
6. Tác tử trả lời chạy trong môi trường Claude Code (gồm cả cài đặt người dùng và bộ nhớ), và một tác tử trả lời liên tiếp 10 câu nên có thể có hiệu ứng ngữ cảnh.
7. Khảo sát được thực hiện tại một thời điểm, từ 2026-10-28 đến ngày 29. Nếu mô hình và kết quả tìm kiếm thay đổi thì kết quả cũng có thể thay đổi.

## 7 Đạo đức và xung đột lợi ích

- Không xử lý thông tin cá nhân. Câu hỏi và câu trả lời không có tên người, tên quán hay địa chỉ.
- Bản quyền nguồn đáp án thuộc Viện Xúc tiến Ẩm thực Hàn Quốc (chính sách bản quyền của Cổng Hansik, kiểm tra ngày 2026-10-28: bản quyền thuộc Viện Xúc tiến Ẩm thực Hàn Quốc, dùng vì mục đích thu lợi phải thỏa thuận trước, bắt buộc ghi nguồn). Vì vậy chúng tôi không phân phối lại bảng nguồn và cách viết chuẩn của 180 món trong mẫu, mà cho phép tái lập qua mã thu thập và mã băm tệp. Trong bài chỉ trích dẫn 5 ví dụ có ghi nguồn.
- Define404, nơi tác giả làm việc, đang chuẩn bị dịch vụ kiểm tra bằng AI cho cửa hàng nhỏ và đang cân nhắc đưa việc kiểm tra cách viết tiếng nước ngoài trên thực đơn vào danh mục. Sản phẩm của chính Define404 không nằm trong đối tượng khảo sát, và khảo sát này không có tài trợ bên ngoài.
- Việc thu thập câu trả lời được thực hiện trong gói thuê bao Claude của tác giả, không phát sinh chi phí thêm.

## 8 Cách tái lập

- Kho công khai: https://github.com/johndefine404/define404-research-public (đường dẫn 002-menu-translation/). Công khai mã thu thập nguồn, mã rút mẫu cố định seed, mẫu câu hỏi, các lô, mã chấm theo quy tắc, mã phân tích, tệp kết quả và kết quả chấm của chúng tôi (chỉ số thứ tự món và kết quả chấm). Không đưa vào bảng nguồn, chuỗi cách viết chuẩn và nguyên văn câu trả lời.
- Đăng ký trước: commit 9f84ace0f6d74576686023187776c5c752f7c5ad của kho nghiên cứu (2026-10-28 23:41 ICT). prereg.md SHA-256: 4cd0480d1af8b2b66bb10cfc4332a53ecd5806cf9dc3256d209c816a6c912596 (không thay đổi sau khi đăng ký)
- Quy tắc chấm judge/rules.md SHA-256: 76370cd882e392dafe6b093f3d11406acadbcdddb3c91ffde8559d87c5ae7908
- Bảng nguồn sampling/raw/hansik_menu_800_20261028.csv SHA-256: 620f0fc8be6918a7a5482e66f86086bf7991505bb679e046d28fa837bf4cc26f (tải lại bằng mã thu thập sampling/fetch_source.py rồi đối chiếu)
- Mẫu sampling/sample_v1.csv SHA-256: ec8992250598de301cf4acf5872476fcc67912c31a4be47084a303d70517868f, seed 20261028
- Dấu vân tay của nguyên văn câu trả lời (SHA-256 của các mã băm 36 tệp lô): b13052316b77ed6865a0cd299816b9eb8d2867187918623dea066321a25faae9
- Kết quả phân tích analysis/out/results.json SHA-256: b8b256647b25b729f4f51b42d7d0aff1e8a30167be15925040266355ff8fccab
- Trình tự tái lập: python sampling/fetch_source.py (thu thập nguồn, đối chiếu mã băm) → python sampling/draw_sample.py → python collect/build_batches.py → thu thập câu trả lời → python judge/auto_judge.py → python analysis/run_analysis.py → python analysis/explore_contains.py → python analysis/make_figures.py
- Dữ liệu tóm tắt công khai (CSV): chỉ gồm tỷ lệ, khoảng tin cậy và cỡ mẫu của từng chỉ số. Không có nguyên văn cách viết chuẩn.
- DOI: sẽ đăng ký trên Zenodo sau khi phát hành và ghi bổ sung.

<!-- src: 002-menu-translation/log.md; 002-menu-translation/prereg.md#3; shasum -a 256 -->

## Việc cửa hàng có thể làm ngay

1. Đừng đưa nguyên câu trả lời của AI lên thực đơn; hãy tự tra tên món tiếng nước ngoài trong bảng "Cách viết tên món ăn Hàn Quốc bằng tiếng nước ngoài" trên Cổng Hansik của Viện Xúc tiến Ẩm thực Hàn Quốc. Trong khảo sát này, câu trả lời của AI trùng hoàn toàn với chuẩn chỉ khoảng một phần năm, ở cả tiếng Anh lẫn tiếng Nhật.
2. Thực đơn tiếng Nhật cần kiểm tra kỹ hơn. Sáu phần mười câu trả lời tiếng Nhật là tên khác chuẩn, và có trường hợp chuẩn là bản dịch tiếng Nhật nhưng câu trả lời lại viết cách phát âm tiếng Hàn bằng katakana.
3. Nếu câu trả lời của AI có tên kèm trong ngoặc thì hãy xem cả phần đó. Có câu trả lời ghi tên chuẩn trong ngoặc. Tuy nhiên, kể cả xem trong ngoặc, sáu phần mười câu tiếng Anh và bảy phần mười câu tiếng Nhật vẫn không có tên chuẩn.
4. Cách hỏi AI "hãy cho biết theo cách viết chuẩn của Viện Xúc tiến Ẩm thực Hàn Quốc" chưa được thử trong khảo sát này. Hiệu quả của cách này chưa được đo.

## Tài liệu tham khảo

1. Yao B., Jiang M., Bobinac T., Yang D., Hu J. Benchmarking Machine Translation with Cultural Awareness. arXiv 2305.14328, v3 2024-10-19. https://arxiv.org/abs/2305.14328
2. Zhang Z., He C., Iyer V., Birch A. Cultural Adaptation of Menus: A Fine-Grained Approach. arXiv 2408.13534, 2024-08-24 (WMT 2024). https://arxiv.org/abs/2408.13534
3. Yuan và cộng sự. Culture-Aware Machine Translation in Large Language Models: Benchmarking and Investigation. arXiv 2604.24361, 2026-04-27 (ACL 2026). https://arxiv.org/abs/2604.24361
4. Zeng và cộng sự. CulturalMenuBench: Probing the Knowledge-Application Gap in Multimodal Culinary Reasoning. arXiv 2609.03526, 2026-09-03. https://arxiv.org/abs/2609.03526
5. Lee J.-H. A Comparative Study of ChatGPT and Papago Korean-to-English Translations of Dialogue from the Adaptation of Pachinko. International Journal of Contents 21(3), 2025, 138-151. https://www.accesson.kr/ijcon/v.21/3/138/57464
6. Viện Xúc tiến Ẩm thực Hàn Quốc. Cách viết tên món ăn Hàn Quốc bằng tiếng nước ngoài (Hướng dẫn cách viết tiếng nước ngoài cho 800 món ăn Hàn Quốc). Cổng Hansik, thu thập ngày 2026-10-28. https://www.hansik.or.kr/board/dn/list/017?menuSn=12

<!-- src: 002-menu-translation/gate.md#1, #3 -->

## Phụ lục A Mẫu câu hỏi

Ví dụ với món giả định "하늘비빔밥". Trong câu hỏi thực tế, tên tiếng Hàn của món trong mẫu được đặt nguyên dạng vào vị trí tên món.

| Ngôn ngữ | Câu hỏi |
|---|---|
| Tiếng Anh | I run a Korean restaurant in Korea and I'm making an English menu. How should I write the dish '하늘비빔밥' on the menu? Put one English menu name on the first line in the form 'NAME: ...', then add one or two short sentences of explanation. |
| Tiếng Nhật | 韓国で韓国料理店をやっていて、日本語のメニューを作っています。「하늘비빔밥」という料理はメニューにどう書けばいいですか。1行目に「NAME: ...」の形でメニュー名を1つだけ書いて、そのあとに1〜2文で短く説明してください。 |

<!-- src: 002-menu-translation/collect/question_templates.json v1.0 -->

## Phụ lục B Tóm tắt quy tắc chấm

- Đơn vị: một câu hỏi là 1 món x 1 ngôn ngữ. Đối tượng chấm là một ứng viên tên món lấy từ câu trả lời; câu giải thích không được chấm.
- Lấy ứng viên: nội dung dòng "NAME:" đầu tiên, nếu không có thì dòng đầu ngắn, nếu cả hai đều không có thì là trích xuất thất bại (0 trường hợp trong khảo sát này). Nếu có từ hai trở lên thì lấy cái đầu và bỏ phần trong ngoặc.
- Chuẩn hóa tiếng Anh: chữ thường, NFKC, bỏ phần trong ngoặc, bỏ dấu câu, gạch nối, gạch chéo, bỏ mạo từ và and, &, with, thống nhất biến thể phiên âm La-tinh.
- Chuẩn hóa tiếng Nhật: NFKC, bỏ khoảng trắng, dấu chấm giữa, dấu trường âm, phần trong ngoặc, bỏ qua việc có hay không có âm ngắt.
- Khớp chặt: ứng viên đã chuẩn hóa giống chuẩn đã chuẩn hóa. Khớp lỏng: tiếng Anh là Jaccard của tập từ từ 0.5 trở lên hoặc chứa phiên âm La-tinh của chuẩn; tiếng Nhật là Dice trên 2-gram ký tự từ 0.5 trở lên hoặc chứa chuẩn. Không khớp: không thuộc cả hai. Không đưa ra: không có câu trả lời.
- Có dẫn nguồn chuẩn: danh sách nguồn của câu trả lời có hansik.or.kr.

<!-- src: 002-menu-translation/judge/rules.md#1-5 -->
