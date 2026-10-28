# Hỏi trợ lý AI của cửa hàng về món không có trong thực đơn, nó trả lời thế nào

- Tác giả: Define404 Research
- Ngày: 2026-10-19
- Loại: ghi chú thử nghiệm. Bản ghi 36 lần hỏi, gồm 12 câu hỏi bằng 3 ngôn ngữ, với trợ lý AI của một tiệm bánh mẫu.
- Bản trên web: https://define404.com/report/001-off-menu-questions/
- DOI: https://doi.org/10.5281/zenodo.23740036

Đây là bản dịch. Bản gốc làm chuẩn là bản tiếng Hàn, phiên bản 1: [https://define404.com/report/001-off-menu-questions/](https://define404.com/report/001-off-menu-questions/)

Chúng tôi hỏi trợ lý AI của một cửa hàng cùng 12 câu hỏi, mỗi câu một lần bằng tiếng Hàn, tiếng Anh và tiếng Việt, tổng cộng 36 lần. Trong 9 lần hỏi về món không có trong thực đơn, 5 lần AI trả lời "không có thông tin, để tôi kiểm tra giúp" và 4 lần nói thẳng "không có". Không lần nào AI bịa ra một mức giá không tồn tại.

Điều đáng lo lại nằm ở chỗ khác. Ngày nghỉ được ghi rõ trong thông tin cửa hàng, nhưng khi hỏi bằng tiếng Việt thì cả hai lần đều sai. Dưới đây là cách thử nghiệm, nguyên văn câu hỏi và câu trả lời, cùng danh sách kiểm tra mà chủ cửa hàng có thể tự làm ngay.

- 0 / 3: Số câu trả lời bịa ra giá khi được hỏi giá bánh macaron, một món không có trong thực đơn
- 4 / 9: Số câu trả lời nói thẳng "không có" mà không kiểm tra, khi được hỏi về món không có trong thực đơn
- 3 / 27: Số câu trả lời sai ở những câu hỏi có đáp án cố định. Trong đó 2 câu là câu hỏi về ngày nghỉ bằng tiếng Việt
## Chúng tôi đã thử nghiệm như thế nào

- Thời điểm thử nghiệm: ngày 19 tháng 10 năm 2026, từ 11 giờ 26 phút đến 36 phút đêm (giờ Việt Nam). Theo giờ Hàn Quốc là từ 1 giờ 26 phút sáng ngày 20 tháng 10.
- Đối tượng thử nghiệm: bản xem trước của Booking Meo, chatbot trợ lý AI do Define404 xây dựng ([booking.define404.com](https://booking.define404.com)). Nó trả lời dựa trên thông tin của cửa hàng mẫu "Tiệm bánh Morak".
- AI tạo câu trả lời: theo tệp cấu hình của bản xem trước, là mô hình Llama 3.3 70B của Cloudflare Workers AI. Giá trị quyết định mức dao động của câu trả lời (temperature) là 0.3.
- Câu hỏi: 6 loại (món có trong thực đơn, món không có trong thực đơn, giá, giờ mở cửa, đặt trước, câu hỏi không liên quan), mỗi loại 2 câu, tổng cộng 12 câu, và soạn ba bộ cùng nghĩa bằng tiếng Hàn, tiếng Anh, tiếng Việt.
- Cách gửi: gửi qua đúng địa chỉ mà cửa sổ trò chuyện trên trang web sử dụng, mỗi câu hỏi mở một cuộc trò chuyện mới và chỉ gửi một lần, để câu hỏi trước không lẫn vào câu trả lời sau. Để không gây tải cho bản xem trước, giữa các câu hỏi cách nhau 12 giây.
- Đánh giá: đối chiếu từng dòng với tệp thông tin cửa hàng và chia thành bốn loại: đúng, nói không biết và chuyển tiếp, khẳng định không có, và sai. Với câu hỏi không liên quan đến cửa hàng, từ chối lịch sự được tính là đúng.

### Thông tin ghi trong cửa hàng mẫu

- Giờ mở cửa: thứ Ba đến Chủ nhật, từ 8 giờ sáng đến 8 giờ tối. Nghỉ cố định thứ Hai. Ngày lễ vẫn mở cửa, chỉ nghỉ đúng ngày Tết truyền thống.
- Món chủ lực: bánh mì sữa 5,500 won, bánh mì muối 3,000 won, baguette 4,500 won, bánh campagne sung 7,000 won, bánh kem miếng từ 6,500 won.
- Bánh kem đặt trước: đặt trước ít nhất 3 ngày, cỡ 1 giá 38,000 won, cỡ 2 giá 46,000 won, đặt cọc 50%.
- Bánh croissant, bánh mì không gluten và bánh macaron không được ghi. Đây là các câu hỏi được dùng làm "món không có trong thực đơn" trong thử nghiệm này.

Thông tin cửa hàng chỉ ghi "món chủ lực". Chỉ với thông tin này thì không thể biết tiệm có thật sự không bán croissant hay không. Câu trả lời đúng là "để tôi kiểm tra giúp".

## Kết quả theo loại câu hỏi

Mỗi loại câu hỏi 2 câu, hỏi bằng 3 ngôn ngữ, tổng cộng 6 lần mỗi loại.

| Loại | Đúng | Nói không biết và chuyển tiếp | Khẳng định không có | Sai |
|---|---:|---:|---:|---:|
| Món có trong thực đơn | 6 | 0 | 0 | 0 |
| Món không có trong thực đơn | 0 | 2 | 4 | 0 |
| Giá | 3 | 3 | 0 | 0 |
| Giờ mở cửa | 4 | 0 | 0 | 2 |
| Đặt trước | 5 | 0 | 0 | 1 |
| Câu hỏi không liên quan | 6 | 0 | 0 | 0 |
| Tổng | 24 | 5 | 4 | 3 |

Mỗi ngôn ngữ hỏi 12 lần. Cả 36 lần AI đều trả lời bằng đúng ngôn ngữ được hỏi.

| Ngôn ngữ | Đúng | Nói không biết và chuyển tiếp | Khẳng định không có | Sai |
|---|---:|---:|---:|---:|
| Tiếng Hàn | 8 | 1 | 2 | 1 |
| Tiếng Anh | 9 | 2 | 1 | 0 |
| Tiếng Việt | 7 | 2 | 1 | 2 |

## Bốn câu trả lời đáng chú ý

### Cùng câu hỏi về croissant, mỗi ngôn ngữ một câu trả lời khác

Hỏi bằng tiếng Hàn, AI nói thẳng "크루아상은 메뉴에 없습니다" (croissant không có trong thực đơn). Hỏi bằng tiếng Anh, AI trả lời rằng không có thông tin về croissant và đề nghị để lại yêu cầu. Cùng nhìn vào một thông tin cửa hàng mà cách nói lại khác nhau. Về phía khách, "không có" là cuộc trò chuyện đã kết thúc, còn "để tôi kiểm tra giúp" là cuộc trò chuyện còn tiếp tục.

### Giá macaron: cả ba ngôn ngữ đều không bịa

Với "마카롱 하나에 얼마예요?" (một chiếc macaron giá bao nhiêu) và các bản tương ứng, cả ba lần AI đều trả lời không có thông tin về giá. Câu trả lời tiếng Hàn và tiếng Anh nói sẽ kiểm tra rồi liên hệ lại; câu trả lời tiếng Việt chỉ nói không có thông tin, không nhắc đến việc liên hệ.

### Hỏi về thứ Hai bằng tiếng Việt, AI nói tiệm mở cửa

Với "Thứ Hai tiệm có mở cửa không?", AI trả lời rằng thứ Hai có mở, từ 8 giờ đến 20 giờ. Thứ Hai là ngày nghỉ cố định. Với câu hỏi về đúng ngày Tết Trung thu (Chuseok), AI trả lời "ngày lễ mở cửa bình thường" và bỏ sót việc nghỉ đúng ngày Tết. Bằng tiếng Hàn và tiếng Anh, AI trả lời đúng cả hai câu.

### Câu trả lời đặt bánh bằng tiếng Hàn tự mâu thuẫn

Với "케이크 내일 받을 수 있게 예약돼요?" (có thể đặt bánh kem để mai lấy không), AI mở đầu bằng "네, 가능합니다" (vâng, được ạ) rồi nói tiếp "최소 3일 전 예약이 원칙이라 어려울 수 있습니다" (nguyên tắc là đặt trước ít nhất 3 ngày nên có thể khó). Khách chỉ đọc câu đầu sẽ hiểu là được. Câu trả lời tiếng Anh và tiếng Việt nêu nguyên tắc 3 ngày trước. Ngoài ra, hai lần hỏi đặt bánh bằng tiếng Việt đều không có nút đặt trước kèm theo. Tiếng Hàn và tiếng Anh thì có.

## Danh sách kiểm tra chủ cửa hàng có thể tự làm ngay

1. Chọn 3 món cửa hàng mình không bán và tự hỏi trong cửa sổ trò chuyện. Nếu AI nói thẳng "không có", hãy ghi vào thông tin cửa hàng cách trả lời thay thế, chẳng hạn "ngoài các món đã ghi, chúng tôi sẽ kiểm tra rồi báo lại".
2. Nhất định hỏi về ngày nghỉ, mỗi ngôn ngữ khách dùng một lần. Trong 3 câu trả lời sai của thử nghiệm này, 2 câu là câu hỏi về ngày nghỉ bằng tiếng Việt.
3. Những từ gộp chung như "Tết", "ngày lễ" hãy viết rõ thành ngày tháng. Đã có trường hợp AI trả lời tiệm mở cửa vào đúng ngày Tết Trung thu, trong khi hôm đó nghỉ.
4. Với nội dung có điều kiện như "đặt trước 3 ngày", hãy thêm một ví dụ như "bánh kem lấy ngày mai thì không được".
5. Khi khách hỏi đặt trước bằng tiếng nước ngoài, hãy xem nút đặt trước hoặc đường dẫn đặt trước có hiện kèm theo không.

Cách sửa lại thông tin cửa hàng như ở mục 1, 3, 4 chưa được đo hiệu quả trong thử nghiệm này. Sau khi sửa, hãy hỏi lại cùng câu hỏi và tự kiểm tra xem câu trả lời có thay đổi không.

## Những điều thử nghiệm này không thể nói

- Booking Meo là sản phẩm do Define404 làm ra. Việc đánh giá cũng do Define404 thực hiện. Vì vậy chúng tôi giữ lại toàn bộ câu hỏi, câu trả lời và lý do đánh giá trong dữ liệu gốc.
- Chỉ một cửa hàng, một mô hình AI, mỗi câu hỏi chỉ hỏi một lần. Hỏi lại cùng câu hỏi thì câu trả lời có thể khác.
- Không thể đem nguyên kết quả này áp cho trợ lý AI của công ty khác hay mô hình khác.

Phía Booking Meo cũng lộ ra những chỗ cần sửa: không nhận ra câu hỏi đặt bánh bằng tiếng Việt là yêu cầu đặt trước, và đọc thông tin chỉ ghi món chủ lực như thể đó là toàn bộ thực đơn. Để sau khi sửa có thể hỏi lại bằng đúng bộ câu hỏi này, chúng tôi công khai nguyên văn câu hỏi và cách thử nghiệm.

## Nguyên văn câu hỏi và câu trả lời

Câu trả lời không sửa một chữ nào. Bên cạnh câu trả lời tiếng Anh và tiếng Việt, chỉ ghi thêm lý do đánh giá bằng tiếng Hàn.

Nguyên văn câu hỏi và câu trả lời: https://define404.com/report/data/001-booking-meo-test.csv

## Dữ liệu gốc

- [Dữ liệu gốc kết quả thử nghiệm (CSV, 36 dòng)](https://define404.com/report/data/001-booking-meo-test.csv): câu hỏi, thời điểm gửi, thời gian phản hồi, nguyên văn câu trả lời, đánh giá, lý do đánh giá
- [Tập lệnh dùng để thử nghiệm (Python)](https://define404.com/report/data/001-run-test.py): chứa bộ câu hỏi và cách gửi

Sửa đổi 2026-10-20: Booking Meo đã được sửa để nhận ra các cách nói đặt trước bằng tiếng Việt như "đặt bánh", "tiền cọc". Khi hỏi lại, 2 câu hỏi đặt bánh bằng tiếng Việt đã có nút đặt trước kèm theo, còn 2 câu hỏi không liên quan đến đặt trước thì không có. Chúng tôi cũng thêm bảng đối chiếu thứ trong tuần, sau đó AI trả lời đúng cả 4 lần rằng thứ Hai là ngày nghỉ cố định. Câu hỏi về đúng ngày Tết Trung thu chỉ 2 trong 4 lần trả lời rõ là nghỉ, nên chưa sửa xong. Kết quả và dữ liệu gốc ở trên vẫn giữ nguyên như thử nghiệm ngày 19 tháng 10.
