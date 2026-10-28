# What Does a Shop's AI Assistant Say When You Ask About Something Not on the Menu

- Author: Define404 Research
- Date: 2026-10-19
- Type: lab note. A record of 36 questions, 12 questions in 3 languages, put to a sample bakery's AI assistant.
- Web version: https://define404.com/report/001-off-menu-questions/
- DOI: https://doi.org/10.5281/zenodo.23740036

This is a translation. The reference version is the Korean original, version 1: [https://define404.com/report/001-off-menu-questions/](https://define404.com/report/001-off-menu-questions/)

We put the same 12 questions to a shop's AI assistant once each in Korean, English and Vietnamese, 36 questions in all. Of the 9 questions about items not on the menu, 5 answers said "I don't have that information, let me check for you" and 4 flatly said "we don't have it." Not once did it invent a price for an item that was not there.

The real cause for concern lay elsewhere. When asked in Vietnamese about the closing day, which is clearly written in the shop information, it got it wrong both times. Below we set out the test method, the full questions and answers, and a checklist a shop owner can run through right away.

- 0 / 3: Answers that invented a price when asked about macarons, which are not on the menu
- 4 / 9: Answers that flatly said "we don't have it" without checking, when asked about something not on the menu
- 3 / 27: Wrong answers to questions with a fixed correct answer. 2 of them were Vietnamese questions about the closing day
## How we tested

- Test date: 19 October 2026, from 11:26 p.m. to 11:36 p.m. (Vietnam time). In Korean time that is from 1:26 a.m. on 20 October.
- Test subject: the preview of Booking Meo, an AI assistant chatbot built by Define404 ([booking.define404.com](https://booking.define404.com)). It answers from the information of a sample shop, "Morak Bakery."
- The AI that writes the answers: according to the preview's configuration file, Cloudflare Workers AI's Llama 3.3 70B model. The value that controls how much the answers vary (temperature) is 0.3.
- Questions: 2 per type across 6 types (items on the menu, items not on the menu, prices, opening hours, reservations, off-topic questions), 12 in all, each written with the same meaning in three versions: Korean, English and Vietnamese.
- How we sent them: through the same address the website chat window uses, opening a new conversation for each question and sending it only once, so that an earlier question could not bleed into a later answer. We left 12 seconds between questions to avoid loading the preview.
- Judgment: we compared each answer line by line against the shop information file and sorted it into four categories: correct, says it doesn't know and hands off, flatly says no, and wrong. For questions unrelated to the shop, a polite refusal counted as correct.

### What the sample shop's information says

- Opening hours: Tuesday to Sunday, 8 a.m. to 8 p.m. Closed every Monday. Open on public holidays, closed only on the day of major traditional holidays.
- Signature items: milk bread 5,500 won, salt bread 3,000 won, baguette 4,500 won, fig campagne 7,000 won, cake slices from 6,500 won.
- Custom cakes: order at least 3 days in advance, size 1 at 38,000 won, size 2 at 46,000 won, 50% deposit.
- Croissants, gluten-free bread and macarons are not listed. These were the "not on the menu" questions in this test.

The shop information lists only "signature items." So this information alone cannot tell whether croissants are really unavailable. The right answer is "let me check for you."

## Results by type

2 questions per type, in 3 languages, 6 questions per type in all.

| Type | Correct | Says it doesn't know, hands off | Flatly says no | Wrong |
|---|---:|---:|---:|---:|
| On the menu | 6 | 0 | 0 | 0 |
| Not on the menu | 0 | 2 | 4 | 0 |
| Prices | 3 | 3 | 0 | 0 |
| Opening hours | 4 | 0 | 0 | 2 |
| Reservations | 5 | 0 | 0 | 1 |
| Off-topic | 6 | 0 | 0 | 0 |
| Total | 24 | 5 | 4 | 3 |

12 questions per language. All 36 answers came back in the language of the question.

| Language | Correct | Says it doesn't know, hands off | Flatly says no | Wrong |
|---|---:|---:|---:|---:|
| Korean | 8 | 1 | 2 | 1 |
| English | 9 | 2 | 1 | 0 |
| Vietnamese | 7 | 2 | 1 | 2 |

## Four answers worth a closer look

### Same croissant question, a different answer in each language

Asked in Korean, it flatly said "크루아상은 메뉴에 없습니다" (croissants are not on the menu). Asked in English, it said it had no information about croissants and asked the customer to leave an inquiry. Looking at the same shop information, the way it spoke diverged. From the customer's side, "we don't have it" ends the conversation, while "let me check for you" keeps it going.

### It did not invent a macaron price in any of the three languages

To "마카롱 하나에 얼마예요?" (how much is one macaron?) and its counterparts, all three answers said there was no price information. The Korean and English answers said they would check and get back; the Vietnamese answer only said there was no information and did not mention getting back.

### Asked in Vietnamese about Monday, it said the shop is open

To "Thứ Hai tiệm có mở cửa không?" (is the shop open on Monday?), it answered that the shop opens on Monday from 8 to 20. Monday is the regular closing day. To the question about the day of Chuseok, it said "open as usual on public holidays," missing the closure on the holiday itself. In Korean and English it got both questions right.

### The Korean reservation answer contradicted itself

To "케이크 내일 받을 수 있게 예약돼요?" (can I reserve a cake to pick up tomorrow?), it opened with "네, 가능합니다" (yes, that's possible) and then went on with "최소 3일 전 예약이 원칙이라 어려울 수 있습니다" (as a rule orders need at least 3 days' notice, so it may be difficult). A customer who reads only the first sentence takes it as a yes. The English and Vietnamese answers stated the 3-day rule first. Also, the two Vietnamese reservation questions came back without a reservation button attached. The Korean and English ones had it.

## A checklist shop owners can run right away

1. Pick 3 items your shop does not sell and ask the chat window about them yourself. If it flatly says "we don't have it," write into your shop information how it should answer instead, for example "for anything beyond the listed menu, we'll check and let you know."
2. Ask about your closing day once in each language your customers use. Of the 3 wrong answers in this test, 2 were closing-day questions asked in Vietnamese.
3. Spell out blanket terms like "holidays" and "public holidays" as actual dates. There was a case where it said the shop was open on the day of Chuseok, when it is closed.
4. For anything with a condition attached, like "order 3 days ahead," add one example such as "a cake for tomorrow is not possible."
5. Check that a reservation button or reservation link is attached even when the reservation question comes in a foreign language.

For items 1, 3 and 4, this test did not measure whether rewriting the shop information actually helps. After you change it, ask the same questions again and check for yourself whether the answers changed.

## What this test cannot tell you

- Booking Meo is a product made by Define404. Define404 also did the judging. That is why we left every question, answer and judgment reason in the raw data.
- One shop, one AI model, each question asked only once. Asking the same question again may give a different answer.
- These results cannot be carried over as they are to another company's AI assistant or to another model.

The test also turned up things to fix on the Booking Meo side: it did not recognize the Vietnamese reservation questions as reservations, and it read information that lists only signature items as if it were the full menu. So that the same question set can be run again after the fixes, we publish the questions and the test method as they are.

## Full questions and answers

Not a single character of the answers was changed. Next to the English and Vietnamese answers, only the judgment reason is given, in Korean.

Full questions and answers: https://define404.com/report/data/001-booking-meo-test.csv

## Raw data

- [Raw test results (CSV, 36 rows)](https://define404.com/report/data/001-booking-meo-test.csv): question, time sent, response time, full answer, judgment, judgment reason
- [Script used for the test (Python)](https://define404.com/report/data/001-run-test.py): contains the question set and the sending method

Revised 2026-10-20: Booking Meo was updated to recognize Vietnamese reservation terms such as "đặt bánh" (cake order) and "tiền cọc" (deposit). On re-asking, the 2 Vietnamese reservation questions came back with a reservation button, and the 2 questions unrelated to reservations did not. We also added a weekday mapping table, after which it answered all 4 Vietnamese Monday questions correctly as the regular closing day. The question about the day of Chuseok was answered clearly as closed in only 2 of 4 tries, so that is not fixed yet. The results and raw data above are from the 19 October test, unchanged.
