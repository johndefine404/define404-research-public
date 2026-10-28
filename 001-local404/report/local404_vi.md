# Local404: AI có nói các cửa hàng khu phố đã đóng cửa là vẫn đang mở cửa không

Đây là bản dịch. Bản gốc làm chuẩn là bản tiếng Hàn, phiên bản 1: https://define404.com/report/002-local404-closed-shops/

Khảo sát câu trả lời của AI về 800 nhà hàng thông thường ở Hàn Quốc, 5 ngôn ngữ và 4 điều kiện trả lời

- Tác giả: Define404 Research
- Ngày: 2026-10-24
- Đăng ký trước: OSF https://osf.io/5qnxu (đăng ký ngày 2026-10-20)
- DOI: https://doi.org/10.5281/zenodo.23740040
- Xung đột lợi ích: Define404 (nơi tác giả làm việc) đang chuẩn bị dịch vụ giám sát câu trả lời của AI và chẩn đoán mức độ xuất hiện trên AI cho từng cửa hàng. Sản phẩm của chúng tôi không được đưa vào đối tượng khảo sát.

## Tóm tắt

Chúng tôi khảo sát cách AI trả lời khi được hỏi một cửa hàng khu phố hiện còn mở cửa hay không, địa chỉ và loại hình kinh doanh là gì. Đáp án chuẩn là dữ liệu cấp phép công khai. Chúng tôi phân tầng rút 400 cửa hàng đang kinh doanh và 400 cửa hàng đã đóng cửa, tự động gửi câu hỏi bằng 5 ngôn ngữ, phân loại câu trả lời bằng từ điển dựa trên quy tắc và phán định có LLM hỗ trợ, rồi kiểm định các giả thuyết đã đăng ký trước. Trong ba điều kiện của Claude Haiku 5.5 và Sonnet 5.5 (5,000 câu trả lời hợp lệ), chỉ có 1 câu trả lời khẳng định tình trạng mở cửa, và không có câu trả lời nào nói cửa hàng đã đóng cửa là đang mở. Vì vậy các giả thuyết H1, H3, H4 không thể kiểm định được. Llama 3.1 8B khẳng định ở 186 trong 1,641 câu đã phán định (11.3%) với độ chính xác 48.4%. Tỷ lệ trả lời cửa hàng đã đóng cửa là đang mở cao hơn tỷ lệ trả lời cửa hàng đang kinh doanh là đã đóng (ủng hộ H1).

### Kết quả chính

- Ba điều kiện của dòng Claude không khẳng định tình trạng mở cửa mà trả lời không thể xác nhận ở 99.98% số câu hỏi (4,999/5,000). Có 0 câu trả lời nói cửa hàng đã đóng cửa là đang mở (giới hạn trên Wilson 95% tính trên các câu trả lời về cửa hàng đã đóng cửa: điều kiện tìm kiếm web 1.51%, điều kiện trí nhớ 0.19%).
- Điều kiện dùng tìm kiếm web cũng vậy. Trong 1,000 câu của điều kiện tìm kiếm web chỉ có 1 câu khẳng định, và 1 câu đó là đúng.
- 112 câu trả lời của Claude có nêu địa chỉ hầu như đều là câu trả lời về cửa hàng đang kinh doanh, và 95.5% (107 câu) là đúng.
- Ở Llama 3.1 8B, số câu khẳng định đang mở (127 câu) nhiều hơn số câu khẳng định đã đóng (59 câu). Tỷ lệ trả lời cửa hàng đã đóng cửa là đang mở (7.3%) cao hơn tỷ lệ trả lời cửa hàng đang kinh doanh là đã đóng (4.4%) (chênh lệch 2.9 điểm phần trăm, Holm hiệu chỉnh p=0.039).

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv; 001-local404/analysis/out_final/h1.csv; 001-local404/analysis/out_final/holm.csv; 001-local404/analysis/out_final/judgments.csv (L-mem, status in open/closed: 186건, 정답 90건) -->

## 1 Giới thiệu

Mọi người hỏi AI xem cửa hàng khu phố hiện còn mở cửa không. Việc hỏi AI hội thoại "Quán này còn bán không?" trước khi mở ứng dụng bản đồ đã trở nên phổ biến. Nếu AI trả lời cửa hàng đã đóng cửa là đang mở, khách sẽ đi mất công; nếu trả lời cửa hàng đang kinh doanh là đã đóng, cửa hàng sẽ mất khách. Thế nhưng chủ cửa hàng hầu như không có cách nào để biết AI nói gì về cửa hàng của mình.

Khảo sát này chuyển vấn đề đó thành dạng có thể đo được. Đáp án chuẩn là tình trạng mở cửa theo dữ liệu cấp phép của chính quyền địa phương; cùng một câu hỏi về cùng một cửa hàng được gửi bằng năm ngôn ngữ, rồi câu trả lời được so sánh theo từng điều kiện trả lời của AI. Thiết kế mẫu, thu thập câu hỏi, phán định và phân tích thống kê đều được viết thành mã nên có thể chạy lại cùng quy trình. Giả thuyết và phương pháp phân tích đã được đăng ký trước trên OSF trước khi thu thập.

Câu hỏi nghiên cứu được gom thành năm giả thuyết. H1 là liệu tỷ lệ trả lời cửa hàng đã đóng cửa là đang mở có cao hơn tỷ lệ trả lời cửa hàng đang kinh doanh là đã đóng hay không. H2 là liệu tỷ lệ đúng của câu hỏi không phải tiếng Hàn có thấp hơn tiếng Hàn hay không, H3 là liệu tìm kiếm web có làm giảm tỷ lệ lỗi hay không, H4 là liệu thời gian sau khi đóng cửa càng dài thì câu trả lời sai rằng đang mở có càng ít đi hay không, và H5 là liệu câu trả lời về cùng một cửa hàng có khác nhau theo ngôn ngữ hay không.

## 2 Phương pháp khảo sát

Hình 1. Khảo sát được tiến hành như thế này

![Trình tự chọn 800 nhà hàng, hỏi bằng 5 ngôn ngữ, chia câu trả lời của bốn AI thành đang mở, đã đóng, không rõ rồi đối chiếu với tình trạng mở cửa thực tế](figures/fig1-flow.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

### 2.1 Mẫu

Nguồn đáp án chuẩn là tệp toàn quốc "식품_일반음식점" (thực phẩm, nhà hàng thông thường) trong dữ liệu cấp phép của chính quyền địa phương (file.localdata.go.kr, nhận ngày 2026-10-21 với 2,305,461 dòng). Chúng tôi loại các dòng không có địa chỉ, tên cửa hàng dưới 2 ký tự, cùng tên cửa hàng xuất hiện từ 2 dòng trở lên trong cùng một quận huyện, hoặc đã đóng cửa nhưng không có ngày đóng cửa.

Có 8 tầng, là tích của tình trạng mở cửa (đang kinh doanh, đã đóng cửa), có đăng ký địa điểm trên Kakao hay không (có, không) và khu vực (thành phố trực thuộc trung ương, tỉnh); mỗi tầng rút 100 cửa hàng, tổng cộng 800 cửa hàng (đang kinh doanh 400, đã đóng cửa 400). Các ứng viên trong mỗi tầng được sắp xếp theo mã quản lý, xáo trộn với seed 20261021 và lấy từ đầu. Trong khảo sát sơ bộ, với các cửa hàng chọn ngẫu nhiên, mọi hệ thống đều trả lời không biết nên không thấy được khác biệt. Đó là lý do đưa việc có đăng ký trên Kakao hay không vào tầng như một biến thay thế cho mức độ được biết đến trên mạng. Cỡ mẫu được đặt theo mức khoảng 392 cửa hàng mỗi nhóm, cần để phát hiện chênh lệch 10 điểm phần trăm ở H1 với mức ý nghĩa 5% và lực kiểm định 80%.

Điều kiện tìm kiếm web được thu thập trên mẫu con phân tầng gồm 100 trong 800 cửa hàng (đang kinh doanh 50, đã đóng cửa 50, phân bổ tỷ lệ theo 8 tầng, seed 20261024).

Bảng 1. Cấu trúc mẫu

| Phân loại | Số cửa hàng | Cấu trúc | Seed |
|---|---|---|---|
| Toàn bộ mẫu (điều kiện trí nhớ) | 800 | 8 tầng x 100 (đang kinh doanh 400, đã đóng cửa 400) | 20261021 |
| Mẫu con tìm kiếm (điều kiện tìm kiếm web) | 100 | Phân bổ tỷ lệ theo 8 tầng (đang kinh doanh 50, đã đóng cửa 50) | 20261024 |

<!-- src: 001-local404/prereg.md#3; 001-local404/DEVIATIONS.md; 001-local404/analysis/out_final/results.json#inputs.sample_v2_sha256 -->

### 2.2 Câu hỏi

Với mỗi cửa hàng, một câu hỏi hỏi cùng lúc tình trạng mở cửa, địa chỉ và loại hình kinh doanh được soạn bằng tiếng Hàn, tiếng Anh, tiếng Nhật, tiếng Trung giản thể và tiếng Việt. Tên cửa hàng và quận huyện giữ nguyên cách viết tiếng Hàn trong mọi ngôn ngữ. Loại hình kinh doanh là đối tượng phán định nên không đưa vào câu hỏi. Mẫu câu hỏi nằm ở Phụ lục A (collect/question_templates.json v1.1).

### 2.3 Hệ thống trả lời

Bảng 2. Hệ thống trả lời và câu trả lời hợp lệ

| Mã | Mô hình | Điều kiện | Số cửa hàng | Câu trả lời hợp lệ |
|---|---|---|---|---|
| H-mem | Claude Haiku 5.5 | Không dùng công cụ | 800 | 4,000 |
| H-search | Claude Haiku 5.5 | Tìm kiếm web | 100 | 500 |
| S-search | Claude Sonnet 5.5 | Tìm kiếm web | 100 | 500 |
| L-mem | Llama 3.1 8B Instruct (Ollama q8_0, tối đa 300 token, seed 20261021) | Không dùng công cụ | 800 | 2,312 (tiếng Anh 800, tiếng Nhật 800, tiếng Hàn 712) |

<!-- src: 001-local404/analysis/out_final/data_inventory.csv; 001-local404/collect/PROTOCOL.md; 001-local404/collect/run_lmem.py -->

Câu trả lời của Claude được thu thập bằng quy trình hỏi tự động. Mỗi câu hỏi đều kèm một chỉ dẫn (system prompt) chung, trong đó có câu "Answer honestly. If you cannot confirm something, say so.". Điều kiện trí nhớ thêm chỉ dẫn không dùng công cụ, điều kiện tìm kiếm web thêm chỉ dẫn dùng tìm kiếm web cho mỗi câu hỏi. Mỗi câu hỏi được trả lời riêng và bên trả lời không biết mục đích khảo sát cũng như đáp án chuẩn. Với Llama, chỉ câu hỏi được gửi làm tin nhắn người dùng trong môi trường cục bộ để nhận câu trả lời. Không kèm chỉ dẫn chung.

### 2.4 Phán định

Quy tắc phán định (judge/rules.md v1.0) được cố định trước khi thu thập. Tình trạng mở cửa có ba loại: khẳng định đang mở, khẳng định đã đóng, không rõ (không thể xác nhận hoặc không có kết luận). Dù có kèm điều kiện, nếu kết luận là đang mở thì vẫn là khẳng định đang mở. Địa chỉ được xem là đúng nếu tên đường hoặc phường xã pháp định trùng với đáp án chuẩn, sai nếu khác, và không có nếu không nêu. Loại hình kinh doanh được so sánh với đáp án chuẩn theo 8 nhóm (món Hàn, món Trung, món Nhật, món Âu và món Âu bình dân, đồ ăn nhanh kiểu Hàn, gà rán và quán bia rượu, cà phê và tráng miệng, khác). Đúng theo tiêu chí lỏng là trường hợp tình trạng mở cửa đúng; đúng theo tiêu chí chặt là trường hợp tình trạng mở cửa đúng và địa chỉ, loại hình kinh doanh đã nêu đều đúng.

Phán định lần 1 do mã quy tắc dùng từ điển biểu đạt đa ngôn ngữ (analysis/auto_judge.py) thực hiện. Các mục mà từ điển không đưa ra được kết luận được chuyển sang phán định có LLM hỗ trợ. Phán định hỗ trợ chỉ xem nguyên văn quy tắc, câu hỏi và câu trả lời rồi phân loại từng câu trả lời, không được xem đáp án chuẩn và hệ thống trả lời. Việc đối chiếu với đáp án chuẩn do mã thực hiện. Trong ba điều kiện của dòng Claude, phán định có LLM hỗ trợ đã chốt 492 câu (H-mem 214, H-search 171, S-search 107). L-mem chỉ áp dụng phán định bằng từ điển; 671 câu (29.0%) không được từ điển chốt được để là chưa phán định và loại khỏi mọi kiểm định và tính toán độ chính xác.

### 2.5 Phân tích

Các phân tích đã đăng ký trước như sau. H1 là chênh lệch giữa tỷ lệ khẳng định đang mở trong các cửa hàng đã đóng cửa và tỷ lệ khẳng định đã đóng trong các cửa hàng đang kinh doanh, dùng sai số chuẩn theo cụm ở cấp cửa hàng. H2 là chênh lệch theo cặp của tỷ lệ đúng giữa tiếng Hàn và các ngôn ngữ khác trên cùng một cửa hàng. H3 là chênh lệch theo cặp giữa Haiku tìm kiếm web và Haiku trí nhớ. H4 là mô hình hỗn hợp logistic (hệ số chặn ngẫu nhiên theo cửa hàng) hồi quy việc có khẳng định đang mở hay không ở các cửa hàng đã đóng cửa theo logarit của số ngày sau khi đóng cửa. H5 là tỷ lệ cửa hàng mà câu trả lời ở 5 ngôn ngữ không hoàn toàn giống nhau. Khoảng tin cậy dùng khoảng Wilson. H1 đến H4 được hiệu chỉnh đa kiểm định bằng phương pháp Holm; các ô có mẫu dưới 40 và các ô không xác định được giá trị p bị loại khỏi họ hiệu chỉnh. H5 có giả thuyết không là tỷ lệ không nhất quán bằng 0 nên giá trị p không xác định; vì vậy nó bị loại khỏi hiệu chỉnh Holm và được đánh giá bằng việc giới hạn dưới của khoảng tin cậy có vượt 0 hay không (Phụ lục C). Các phân tích không có trong đăng ký trước được đánh dấu là phân tích khám phá.

## 3 Kết quả

### 3.1 Phân bố câu trả lời: dòng Claude bảo lưu phán đoán

Bảng 3. Phán định tình trạng mở cửa theo hệ thống (trong ngoặc là khoảng tin cậy Wilson 95%)

| Hệ thống | n | Khẳng định đang mở | Khẳng định đã đóng | Không rõ | Chưa phán định |
|---|---|---|---|---|---|
| H-mem | 4,000 | 0 (0%) | 0 (0%) | 4,000 (100%; 99.90~100) | 0 |
| H-search | 500 | 0 (0%) | 0 (0%) | 500 (100%; 99.24~100) | 0 |
| S-search | 500 | 1 (0.2%; 0.04~1.12) | 0 (0%) | 499 (99.8%; 98.88~99.96) | 0 |
| L-mem | 2,312 | 127 (5.5%; 4.6~6.5) | 59 (2.6%; 2.0~3.3) | 1,455 (62.9%; 60.9~64.9) | 671 (29.0%) |

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv (scope=all) -->

Hình 2. Nếu hỏi AI 100 lần (số câu trả lời được rút gọn và làm tròn thành 100 ô. 1 câu khẳng định của dòng Claude là 1 trong 5,000 câu nên nhỏ hơn một ô)

![Dòng Claude trả lời không thể xác nhận ở cả 100 ô, còn Llama trong 100 ô có 5 ô đang mở, 3 ô đã đóng, 63 ô không rõ, 29 ô không phân loại được](figures/fig2-100-answers.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

Trong 5,000 câu trả lời hợp lệ của ba điều kiện dòng Claude, chỉ có 1 câu khẳng định tình trạng mở cửa, là câu hỏi tiếng Trung của S-search. Câu đó cũng là câu trả lời đúng, nói cửa hàng đang kinh doanh là đang mở. Trong 2,500 câu trả lời về cửa hàng đã đóng cửa có 0 câu khẳng định đang mở, và trong 2,500 câu trả lời về cửa hàng đang kinh doanh cũng có 0 câu khẳng định đã đóng. Giới hạn trên Wilson 95% của ô cửa hàng đã đóng cửa là 1.51% với mỗi 250 câu của điều kiện tìm kiếm web và 0.19% với 2,000 câu của H-mem. Kết quả giống nhau ở cả năm ngôn ngữ. Ngay cả trong điều kiện dùng tìm kiếm web, số câu khẳng định cũng chỉ là 1 trong 1,000 câu.

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv (scope=truth, scope=lang); 001-local404/analysis/out_final/status_distribution.csv -->

### 3.2 Các giả thuyết đăng ký trước H1 đến H5

Trong ba điều kiện của dòng Claude, hầu như không có câu trả lời khẳng định nên kiểm định H1, H3, H4 không thành lập. Khi mọi tỷ lệ cần so sánh đều bằng 0 thì sai số chuẩn bằng 0 và giá trị p của kiểm định dựa trên khoảng tin cậy không xác định. Điều này không có nghĩa là giả thuyết sai. Đó là kết quả cho thấy câu trả lời trong điều kiện này không có đủ biến thiên để kiểm định giả thuyết.

Bảng 4. Kết quả kiểm định các giả thuyết đăng ký trước

| Giả thuyết | Hệ thống | Kết quả |
|---|---|---|
| H1 | S-search, H-search, H-mem | Khẳng định đang mở ở cửa hàng đã đóng cửa 0%, khẳng định đã đóng ở cửa hàng đang kinh doanh 0%. Không thể kiểm định (0 so với 0) |
| H1 | L-mem | 7.3% (59/803; 95% CI 5.5~9.2) so với 4.4% (37/838; 3.0~5.8). Chênh lệch 2.9 điểm phần trăm (0.6~5.2), p hai phía=0.013, Holm hiệu chỉnh p=0.039. Ủng hộ |
| H2 | S-search, H-search, H-mem | Tỷ lệ đúng 0%, không khác tiếng Hàn. Không thể kiểm định. Ngoại lệ: tiếng Trung ở S-search +1 điểm phần trăm (1 câu, p=0.317) |
| H2 | L-mem | Tiếng Anh -15.1 điểm phần trăm (-19.0~-11.2; Holm p=2.0e-13), tiếng Nhật -10.2 điểm phần trăm (-15.7~-4.7; Holm p=0.0010). Không có câu trả lời tiếng Trung và tiếng Việt. Ủng hộ ở tiếng Anh và tiếng Nhật |
| H3 | H-search so với H-mem | 500 cặp (100 cửa hàng), cả hai điều kiện đều có 0 lỗi. Không thể kiểm định |
| H4 | S-search, H-search, H-mem | 0 câu trả lời sai rằng đang mở (trong 250, 250, 2,000 câu). Không thể kiểm định |
| H4 | L-mem | 59 câu khẳng định đang mở trong 803 câu về cửa hàng đã đóng cửa. Tỷ số odds theo mỗi đơn vị logarit số ngày đóng cửa 1.04 (0.84~1.30), p=0.70. Không được ủng hộ |
| H5 | S-search | Cửa hàng có phán định khác nhau giữa 5 ngôn ngữ: 1/100 (1.0%; Wilson 0.18~5.45%). Thỏa mãn về mặt hình thức nhưng phụ thuộc vào một trường hợp |
| H5 | H-search, H-mem | 0/100 (giới hạn trên 3.70%), 0/800 (giới hạn trên 0.48%). Mọi cửa hàng đều có cùng phán định ở 5 ngôn ngữ |
| H5 | L-mem | Không có cửa hàng nào có đủ cả 5 ngôn ngữ nên không thể kiểm định |

<!-- src: 001-local404/analysis/out_final/h1.csv; 001-local404/analysis/out_final/h2.csv; 001-local404/analysis/out_final/h3.csv; 001-local404/analysis/out_final/h4.csv; 001-local404/analysis/out_final/h5.csv; 001-local404/analysis/out_final/holm.csv (holm_p_two_all) -->

1 trường hợp của S-search ở H5 là chỉ câu trả lời tiếng Trung nói đang mở, còn bốn ngôn ngữ còn lại là không rõ. Không có hệ thống nào có cửa hàng mà đang mở và đã đóng mâu thuẫn nhau. Trường hợp duy nhất này chính là mục trùng với câu trả lời duy nhất khẳng định đang mở.

Kết quả H2 của Llama là tỷ lệ đúng tính không rõ là không đúng, nên khác biệt giữa các ngôn ngữ phần lớn phản ánh khác biệt về tỷ lệ khẳng định. Tính trên các câu đã phán định, Llama khẳng định tình trạng mở cửa ở 120 trong 380 câu tiếng Hàn (31.6%), 61 trong 524 câu tiếng Nhật (11.6%) và 5 trong 737 câu tiếng Anh (0.7%).

### 3.3 Địa chỉ và loại hình kinh doanh

Địa chỉ và loại hình kinh doanh xuất hiện cả trong những câu trả lời không khẳng định tình trạng mở cửa. Mục này là phân tích khám phá.

Bảng 5. Tỷ lệ nêu và độ chính xác của địa chỉ và loại hình kinh doanh (trong ngoặc là khoảng tin cậy Wilson 95%)

| Hệ thống | Nêu địa chỉ | Độ chính xác địa chỉ | Nêu loại hình kinh doanh | Độ chính xác loại hình kinh doanh |
|---|---|---|---|---|
| S-search | 26/500 (5.2%) | 25 (96.2%; 81.1~99.3) | 149/500 (29.8%) | 124 (83.2%; 76.4~88.4) |
| H-search | 34/500 (6.8%) | 30 (88.2%; 73.4~95.3) | 141/500 (28.2%) | 120 (85.1%; 78.3~90.1) |
| H-mem | 52/4,000 (1.3%) | 52 (100%; 93.1~100) | 738/4,000 (18.5%) | 561 (76.0%; 72.8~79.0) |
| L-mem | 70/2,312 (3.0%) | Không tính do có mục chưa phán định | 285/2,312 (12.3%) | Không tính do có mục chưa phán định |

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv (scope=all, address_*, type_*) -->

Hình 3. Câu trả lời của Claude có nêu địa chỉ (tổng ba điều kiện)

![Trong ba điều kiện của dòng Claude, câu trả lời có nêu địa chỉ gồm 105 lần với cửa hàng đang kinh doanh (đúng 101) và 7 lần với cửa hàng đã đóng cửa (đúng 6)](figures/fig3-claude-address.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

Trong ba điều kiện của dòng Claude, 107 trong 112 câu trả lời có nêu địa chỉ (95.5%) trùng với địa chỉ chuẩn. Câu trả lời có nêu địa chỉ phần lớn là về cửa hàng đang kinh doanh. S-search nêu địa chỉ ở 26 trong 250 câu về cửa hàng đang kinh doanh, và 0 câu trong 250 câu về cửa hàng đã đóng cửa. H-search là 31 câu đang kinh doanh so với 3 câu đã đóng cửa, H-mem là 48 câu đang kinh doanh so với 4 câu đã đóng cửa. Có vẻ cửa hàng đã đóng cửa còn ít thông tin trên mạng nên khó xác nhận địa chỉ, và tỷ lệ trả lời không biết tăng lên tương ứng. Đây chỉ là mô hình quan sát được, không phải kết quả kiểm định trực tiếp nguyên nhân.

Loại hình kinh doanh được nêu thường xuyên hơn địa chỉ. Điều kiện tìm kiếm web (28~30%) nêu thường xuyên hơn điều kiện trí nhớ (18.5%), với độ chính xác 76~85%.

### 3.4 Kết quả Llama

Khác với dòng Claude, Llama 3.1 8B có những câu trả lời khẳng định tình trạng mở cửa. Nó khẳng định ở 186 trong 1,641 câu đã phán định (11.3%; 9.9~13.0), gồm 127 câu khẳng định đang mở và 59 câu khẳng định đã đóng. Trong 186 câu khẳng định có 90 câu đúng, nên độ chính xác là 48.4% (41.3~55.5). Không khác nhiều so với tung đồng xu.

Bảng 6. Phán định tình trạng mở cửa của Llama theo ngôn ngữ

| Ngôn ngữ | n | Khẳng định đang mở | Khẳng định đã đóng | Không rõ | Chưa phán định |
|---|---|---|---|---|---|
| Tiếng Anh | 800 | 5 (0.6%) | 0 (0%) | 732 (91.5%) | 63 (7.9%) |
| Tiếng Nhật | 800 | 37 (4.6%) | 24 (3.0%) | 463 (57.9%) | 276 (34.5%) |
| Tiếng Hàn | 712 | 85 (11.9%) | 35 (4.9%) | 260 (36.5%) | 332 (46.6%) |

<!-- src: 001-local404/analysis/out_final/exploratory_summary.csv (system=L-mem, scope=lang); 001-local404/analysis/out_final/judgments.csv (L-mem, 확정 단정 186건 중 정답 90건: 한국어 57/120, 일본어 31/61, 영어 2/5) -->

Trong 81 câu khẳng định về cửa hàng đã đóng cửa, 59 câu (72.8%) là câu trả lời sai rằng đang mở; trong 105 câu khẳng định về cửa hàng đang kinh doanh, 37 câu (35.2%) là câu trả lời sai rằng đã đóng. Llama nghiêng về phía trả lời đang mở, và với cửa hàng đã đóng cửa, sự nghiêng này trở thành lỗi. So sánh có điều kiện trên các câu khẳng định này (chênh lệch 37.6 điểm phần trăm) là phân tích khám phá. Độ chính xác của các câu khẳng định đã phán định là 47.5% ở tiếng Hàn (57/120) và 50.8% ở tiếng Nhật (31/61), khác biệt giữa các ngôn ngữ nhỏ.

Hình 4. Câu trả lời khẳng định dứt khoát của Llama (tính trên các câu đã phán định)

![Trong 81 lần khẳng định về cửa hàng đã đóng cửa, 59 lần là câu trả lời sai rằng đang mở; trong 105 lần khẳng định về cửa hàng đang kinh doanh, 37 lần là câu trả lời sai rằng đã đóng. Đúng 90 lần, sai 96 lần](figures/fig4-llama-right-wrong.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

### 3.5 Mức độ nhất quán của phán định

Độ tin cậy của phán định được đánh giá bằng việc phán định bằng từ điển và phán định có LLM hỗ trợ có đưa ra cùng kết luận cho cùng một câu trả lời hay không. Chúng tôi so sánh các câu trả lời mà cả hai phương pháp đều phân loại trong ba điều kiện của dòng Claude.

Bảng 7. Sự nhất quán giữa phán định bằng từ điển và phán định có LLM hỗ trợ

| Hạng mục | n | Tỷ lệ nhất quán | Kappa của Cohen (95% CI) |
|---|---|---|---|
| Tình trạng mở cửa | 1,364 | 100% | Không tính được (hầu hết câu trả lời thuộc một loại) |
| Địa chỉ | 1,239 | 95.7% | 0.35 (0.22~0.48) |
| Loại hình kinh doanh | 722 | 73.0% | 0.46 (0.39~0.52) |

<!-- src: 001-local404/analysis/out_final/llm_dictionary_agreement.csv (group=all) -->

Tình trạng mở cửa nhất quán ở toàn bộ 1,364 câu. Tuy nhiên, hầu hết câu trả lời là không rõ nên các loại dồn về một phía và kappa không xác định. Tỷ lệ nhất quán 100% chỉ cho thấy phán định không rõ là ổn định, chứ không cho thấy phán định khẳng định là hợp lệ. Kappa của địa chỉ được tính ra thấp vì câu trả lời có nêu địa chỉ hiếm. Loại hình kinh doanh có mức nhất quán thấp nhất, 73%. Độ chính xác loại hình kinh doanh (Bảng 5) cần được đọc có tính đến sự không chắc chắn của phán định này.

## 4 Thảo luận

Kết quả nổi bật nhất trong khảo sát này không phải câu trả lời sai mà là việc bảo lưu phán đoán. Dòng Claude hầu như luôn trả lời không thể xác nhận trước câu hỏi về tình trạng mở cửa, và không có trường hợp nào trong 5,000 câu nói cửa hàng đã đóng cửa là đang mở. Với cửa hàng, điều này vừa có mặt may mắn vừa có mặt đáng tiếc. Nguy cơ khách đi mất công vì hướng dẫn sai về tình trạng mở cửa là thấp. Nhưng ngay cả cửa hàng đang kinh doanh cũng vẫn là "cửa hàng không thể xác nhận" đối với AI. Trong 2,500 câu về cửa hàng đang kinh doanh, chỉ có 1 câu trả lời là đang mở.

Địa chỉ và loại hình kinh doanh cũng chỉ về cùng một hướng. Địa chỉ phần lớn chỉ xuất hiện ở cửa hàng đang kinh doanh và có độ chính xác cao. AI nói chính xác về cửa hàng nó biết, và nói không biết về cửa hàng nó không biết. Sẽ tự nhiên hơn khi cho rằng để cửa hàng xuất hiện trong câu trả lời của AI, thông tin cửa hàng phải được công khai ở dạng AI có thể xác nhận. Đây là diễn giải rút ra từ mô hình quan sát được, không phải kết quả kiểm định giả thuyết.

Tìm kiếm web cũng không thay đổi được việc bảo lưu phán đoán. Trong điều kiện tìm kiếm web, số câu khẳng định cũng chỉ là 1 trong 1,000 câu. Có thể tìm kiếm không chạm tới nguồn xác nhận trực tiếp được tình trạng mở cửa, cũng có thể chỉ dẫn (system prompt) yêu cầu không khẳng định khi thiếu căn cứ đã phát huy tác dụng. Thiết kế này không tách được hai khả năng đó.

Llama 3.1 8B thì ngược lại. Mô hình nhỏ chạy cục bộ đưa ra khẳng định, với độ chính xác 48.4%. Đặc biệt, 72.8% câu khẳng định về cửa hàng đã đóng cửa là câu trả lời sai rằng đang mở. Điều này cho thấy nguy cơ của việc nói một cách tự tin dù sai. Trì hoãn phán đoán và khẳng định sai là hai kiểu thất bại khác nhau. Trong dữ liệu lần này, dòng Claude gần với kiểu thứ nhất, Llama gần với kiểu thứ hai. Tuy nhiên hai dòng khác nhau cả về mô hình lẫn chỉ dẫn (system prompt) (mục 5 điểm 1), nên không phân định được đâu là tính chất của mô hình và đâu là tác dụng của chỉ dẫn.

Hình 5. AI trì hoãn phán đoán và AI khẳng định sai (hai dòng khác nhau cả về chỉ dẫn (system prompt) nên không thể xem là khác biệt chỉ do mô hình, mục 5 điểm 1)

![Dòng Claude không nói cửa hàng đã đóng cửa là đang mở nhưng cũng hầu như không cho biết cửa hàng nào đang kinh doanh, còn Llama thì phần lớn câu khẳng định về cửa hàng đã đóng cửa là câu trả lời sai rằng đang mở](figures/fig5-two-failures.svg)

<!-- src: 001-local404/analysis/make_figures.py; 001-local404/analysis/out_final/exploratory_summary.csv -->

Trong Llama, câu hỏi tiếng Hàn có tỷ lệ khẳng định cao nhất (so với tổng số câu trả lời: tiếng Hàn 120/712, tiếng Nhật 61/800, tiếng Anh 5/800). Có thể vì tài liệu tiếng Hàn về cửa hàng Hàn Quốc tương đối nhiều hơn. Tuy nhiên độ chính xác của các câu khẳng định tương tự nhau giữa các ngôn ngữ, nên nói nhiều hơn không có nghĩa là chính xác hơn.

## 5 Hạn chế

1. Điều kiện chỉ dẫn (system prompt) khác nhau giữa các hệ thống trả lời. Dòng Claude nhận chỉ dẫn hãy nói rõ nếu không thể xác nhận, còn Llama chỉ nhận câu hỏi. Khác biệt giữa các dòng bao gồm cả khác biệt về mô hình lẫn khác biệt về chỉ dẫn.
2. Điều kiện tìm kiếm web được thu thập trên mẫu con phân tầng 100 cửa hàng, và câu trả lời của Llama giới hạn ở 800 câu tiếng Anh, 800 câu tiếng Nhật và 712 câu tiếng Hàn.
3. Khảo sát được thực hiện tại một thời điểm từ ngày 2026-10-21 đến ngày 24 và phán định được thực hiện bằng phân loại dựa trên quy tắc và phán định bằng LLM.

## 6 Kết luận

Claude Haiku 5.5 và Sonnet 5.5 trong điều kiện chỉ dẫn (system prompt) của khảo sát này trên thực tế không khẳng định tình trạng mở cửa của các nhà hàng khu phố ở Hàn Quốc. Số trường hợp trả lời cửa hàng đã đóng cửa là đang mở là 0 trong 5,000 câu. Trong điều kiện này, vấn đề thực sự không phải nguy cơ trả lời sai mà là cửa hàng không xuất hiện trong câu trả lời của AI vì không có thông tin. Thêm tìm kiếm web cũng vậy. Ngược lại, mô hình công khai cỡ nhỏ Llama 3.1 8B đưa ra khẳng định, và gần một nửa số câu khẳng định là sai. Xu hướng trả lời cửa hàng đã đóng cửa là đang mở ủng hộ giả thuyết H1 đã đăng ký trước. Để AI nói chính xác tình trạng mở cửa, địa chỉ và loại hình kinh doanh, trước hết phải có thông tin công khai mà AI có thể xác nhận. Đó là hướng mà dữ liệu này chỉ ra.

## Công bố dữ liệu

- Kho lưu trữ công khai: https://github.com/johndefine404/define404-research-public/tree/main/001-local404 (đường dẫn 001-local404/). Mã phân tích và kết quả được công bố. Mẫu gốc chứa tên cửa hàng và địa chỉ cùng nguyên văn câu trả lời không được đưa vào; thay vào đó là mẫu đã bỏ tên cửa hàng và địa chỉ.
- Commit chốt báo cáo trong kho nghiên cứu (riêng tư): b52ee75cd1fb6f35f8aed6381e866a3e3a54887c (các commit dọn dẹp sau đó đổi tên thư mục kết quả từ analysis/out_dryrun thành analysis/out_final, xóa câu thông báo kết quả thử nghiệm và đổi đuôi câu sang thể 해요체 (văn phong lịch sự thân mật). Số liệu không thay đổi)
- Seed: mẫu 20261021, mẫu con tìm kiếm 20261024, Llama 20261021
- Tệp mẫu sampling/sample_v2.csv SHA-256: 4aaf1ecd22963e703e3283c9223206e3cde2aa1e9daf6fde24f53fc8abc24871
- Đăng ký trước prereg.md SHA-256: 87be279e17ebc0922ca079845ea3959ee04ca1379033f7b2c5e5fd8a21abc02b
- Quy tắc phán định judge/rules.md SHA-256: a4ddb1efe5bd50c8d74e64a9678773646c9d05da0af73e749bf3f55f79386209
- Dấu vân tay của câu trả lời gốc (SHA-256 của các mã băm 510 tệp): 71bee2b3dc6dd3af61c09f5334b840f12798f40043cea9eec57c99bda10a4ed0
- Kết quả phân tích analysis/out_final/results.json SHA-256: f9a4dbdcf88ac7aff3e32d13cea971ddbaa224332fbcaa176f995c6a79ea6123
- Tái lập: python analysis/run_analysis.py --dryrun --out analysis/out_final (tên tùy chọn chạy là dryrun, và giá trị cột mode trong tệp kết quả cũng là dryrun. Lý do là việc thu thập Llama ít hơn kế hoạch nên không qua được kiểm tra tính đầy đủ của --final. Chạy lại sẽ làm thay đổi thời điểm tạo và dấu vân tay)

Tên cửa hàng và địa chỉ của hộ kinh doanh cá thể được bỏ khỏi dữ liệu công khai, và ví dụ ở Phụ lục A dùng tên giả định.

<!-- src: 001-local404/analysis/out_final/results.json#inputs -->

## Phụ lục A Ví dụ câu hỏi

가상의 가게 "하늘식당"(서울 마포구)을 묻는 질문 틀이에요.

| Ngôn ngữ | Câu hỏi |
|---|---|
| Tiếng Hàn | 마포구에 있는 음식점 '하늘식당', 지금도 영업하나요? 주소와 어떤 종류의 음식점인지도 알려 주세요. |
| Tiếng Anh | Is the restaurant '하늘식당' in 마포구 still open? Please also tell me its address and what kind of restaurant it is. |
| Tiếng Nhật | 마포구にある「하늘식당」という飲食店は今も営業していますか？住所と、どんな種類のお店かも教えてください。 |
| Tiếng Trung | 位于마포구的餐厅“하늘식당”现在还在营业吗？请同时告诉我它的地址和它是什么类型的餐厅。 |
| Tiếng Việt | Nhà hàng '하늘식당' ở 마포구 hiện còn mở cửa không? Cho tôi biết luôn địa chỉ và đây là loại nhà hàng gì. |

## Phụ lục B Tóm tắt quy tắc phán định

- Tình trạng mở cửa: có ba loại là khẳng định đang mở, khẳng định đã đóng, không rõ. Dù có kèm điều kiện, nếu có kết luận thì xem là khẳng định. Nếu cả đang mở và đã đóng cùng xuất hiện thì theo câu kết luận cuối cùng, không có kết luận thì là không rõ. Câu trả lời chỉ giới thiệu cửa hàng khác tên hoặc ở khu vực khác cũng là không rõ.
- Đáp án chuẩn: nếu tên trạng thái kinh doanh trong dữ liệu cấp phép là đang kinh doanh hoặc bình thường thì là đang mở, nếu là đóng cửa thì là đã đóng.
- Địa chỉ: đúng nếu tên đường (đến tên phố) hoặc phường xã pháp định, thị trấn xã trùng nhau; sai nếu nêu nơi khác làm địa chỉ của cửa hàng mục tiêu; không có nếu không nêu hoặc chỉ nêu địa chỉ của cửa hàng khác.
- Loại hình kinh doanh: so sánh theo 8 nhóm (món Hàn, món Trung, món Nhật, món Âu và món Âu bình dân, đồ ăn nhanh kiểu Hàn, gà rán và quán bia rượu, cà phê và tráng miệng, khác). Nếu đáp án chuẩn là khác thì loại khỏi phán định loại hình kinh doanh.
- Điểm: đúng theo tiêu chí lỏng là trường hợp tình trạng mở cửa đúng; đúng theo tiêu chí chặt là thêm vào đó, địa chỉ và loại hình kinh doanh đã nêu đều đúng.
- Trình tự phán định: từ điển biểu đạt đa ngôn ngữ, phán định có LLM hỗ trợ (không tiết lộ đáp án chuẩn), đối chiếu với đáp án chuẩn bằng mã.

<!-- src: 001-local404/judge/rules.md#1-5 -->

## Phụ lục C Thay đổi so với đăng ký trước

| Hạng mục | Đăng ký trước | Thực hiện |
|---|---|---|
| Mô hình cục bộ | Llama 3.1 8B trên Cloudflare Workers AI (W-mem) | Llama 3.1 8B Instruct trên Ollama cục bộ (L-mem) |
| Mẫu của điều kiện tìm kiếm web | Toàn bộ 800 cửa hàng | Mẫu con phân tầng 100 cửa hàng |
| Phán định | Phán định bằng từ điển dựa trên quy tắc | Thêm phán định có LLM hỗ trợ vào phán định bằng từ điển |
| Đánh giá độ tin cậy của phán định | Mức độ nhất quán và kappa của Cohen khi 2 người phán định 200 câu trả lời ngẫu nhiên | Thay bằng mức độ nhất quán giữa phán định bằng từ điển và phán định có LLM hỗ trợ (Bảng 7) |
| H5 và hiệu chỉnh Holm | Hiệu chỉnh Holm cho H1 đến H5 | H5 có giá trị p không xác định nên loại khỏi họ Holm, đánh giá bằng giới hạn dưới của khoảng tin cậy |
| Ngôn ngữ trả lời của Llama | 5 ngôn ngữ | Tiếng Anh, tiếng Nhật, tiếng Hàn |
| Chỉ dẫn (system prompt) trả lời | Không quy định chỉ dẫn giống nhau giữa các hệ thống | Ba điều kiện Claude dùng chỉ dẫn chung, Llama chỉ có câu hỏi |
| Thu thập lại câu trả lời | Chỉ thử lại câu trả lời thất bại và câu trả lời trống | Thu thập lại một phần câu trả lời (thay thế câu trả lời sai ngôn ngữ và câu trả lời không hợp lệ) |

<!-- src: 001-local404/DEVIATIONS.md; 001-local404/prereg.md#5-6 -->

## Phụ lục D Kết quả chỉ dùng phán định bằng từ điển

Vì quy tắc phán định được bổ sung sau khi thu thập (thêm phán định có LLM hỗ trợ), theo mục 8 của bản đăng ký trước, chúng tôi cũng đưa vào kết quả chỉ áp dụng phán định bằng từ điển, tức quy tắc ban đầu. Nếu chỉ dùng phán định bằng từ điển, số câu khẳng định tình trạng mở cửa trong ba điều kiện Claude đều là 0 ở S-search 500 câu, H-search 500 câu và H-mem 4,000 câu. Số câu từ điển không đưa ra được kết luận là S-search 15 câu, H-search 25 câu, H-mem 0 câu. 1 câu khẳng định đang mở duy nhất trong phần chính (S-search tiếng Trung) là câu được chốt bằng phán định hỗ trợ. Nếu chỉ dùng phán định bằng từ điển thì không hệ thống nào có cửa hàng mà phán định khác nhau giữa 5 ngôn ngữ, nên H5 không được ủng hộ (tính trên các cửa hàng có phán định đã chốt ở cả 5 ngôn ngữ: 0 trong S-search 91 cửa hàng, H-search 81 cửa hàng, H-mem 800 cửa hàng). Llama không dùng phán định hỗ trợ nên kết quả trong phần chính chính là kết quả phán định bằng từ điển.

<!-- src: 001-local404/analysis/out_dictonly/exploratory_summary.csv (Claude 세 조건, scope=all); 001-local404/analysis/out_dictonly/h5.csv -->
