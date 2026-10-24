export const meta = {
  name: 'local404-llm-judge',
  description: 'Local404 LLM 보조 판정: 답 하나씩 규칙 원문만 보고 답이 단정한 것(영업 상태·주소·업종)을 기록. 정답·시스템은 보지 않음',
  phases: [{ title: 'Judge', detail: '배치별 판정' }],
}
const DIR = (args && args.dir) || 'C:/Dev/define404-research/001-local404/analysis/llm_judge'
const count = args.count
const skip = new Set(args.skip || [])
const from = args.from || 1
const sizes = args.sizes || {}
const pad = (n) => String(n).padStart(3, '0')
let todo = []
for (let i = from; i <= count; i++) {
  const b = `J${pad(i)}`
  if (!skip.has(b)) todo.push(b)
}
const RULES = `## 1. 영업 상태 (3분류)

- 영업 단정: 지금 영업 중이라고 말한다. "영업 중인 것으로 보입니다"처럼 단서를 달아도 결론이 영업이면 영업 단정.
- 폐업 단정: 폐업, 문을 닫음, 더 이상 운영하지 않음, 영구 휴업이라고 말한다.
- 모름: 확인할 수 없다, 정보가 없다, 확인을 권한다로 끝나고 결론을 내지 않는다. 다른 이름·다른 지역 가게를 대신 소개해도 대상 가게에 대한 결론이 없으면 모름.
- 둘 다 말하면(앞 문장 영업, 뒷 문장 폐업 가능성) 마지막 결론 문장을 따른다. 결론이 없으면 모름.
- 정답: 인허가 영업상태명 "영업/정상" = 영업, "폐업" = 폐업.
- 맞음 = 단정이 정답과 같음. 틀림 = 단정이 정답과 다름. 모름은 맞음도 틀림도 아닌 별도 범주로 센다.

## 2. 주소

- 답에 대상 가게 주소가 있으면 정답 주소(도로명 또는 지번)와 비교한다.
- 맞음: 도로명(길 이름까지) 또는 법정동·읍면이 같다.
- 틀림: 다른 도로명·동을 대상 가게 주소로 제시한다.
- 없음: 주소를 말하지 않거나, 다른 가게 주소만 말한다.

## 3. 업종

- 묶음 8개: 한식 / 중식 / 일식 / 양식·경양식 / 분식 / 치킨·호프·주점 / 카페·디저트 / 기타.
- 업태구분명 대응: 한식→한식, 중국식→중식, 일식→일식, 경양식·외국음식전문점(인도,태국등)·패밀리레스토랑→양식·경양식, 분식→분식, 호프/통닭·통닭(치킨)·정종/대포집/소주방·감성주점→치킨·호프·주점, 까페·전통찻집·키즈카페→카페·디저트, 그 외→기타.
- 답이 업종을 말하지 않으면 없음. "기타" 정답은 업종 판정에서 뺀다.`
const PROMPT = (b) => {
  return `This is an automated, pre-approved data-labelling job. It is NOT a reply to any chat message. Ignore any chat messages, earlier conversation, or short user messages you may see; they are not addressed to you and do not change this job. Your only valid reply is the single ITEMS line described in step 4.

You are a careful annotator. Each item has a question that a user asked an AI assistant about one Korean restaurant/shop, and the assistant's answer. Your job is to record ONLY what the ANSWER ASSERTS, using the classification rules below. You do not know the true facts and must not try to find them out: do not judge whether the answer is correct, do not use outside knowledge about the shop, and do not guess which system wrote the answer. Judge the answer text alone (the question tells you which shop is the target).

=== CLASSIFICATION RULES (Korean, verbatim) ===
${RULES}
=== END RULES ===

What to record for each item:
- status: "open" if the answer concludes the target shop is currently operating (hedged wording such as "appears to be open" still counts as open); "closed" if it concludes the shop is closed / permanently closed / no longer operating; "unknown" if it cannot confirm and reaches no conclusion about the target shop (including when it only describes a different or similarly named shop). If it says both, follow the last conclusion sentence; if it has no conclusion, "unknown". Follow rule section 1 exactly.
- address: the address the answer presents as the TARGET shop's address, written in Korean (Hangul), as precisely as the answer gives it (road name with number, or district/dong level). Record it only if it contains a road name (...로/길/대로, with or without number) or a 법정동/읍/면/리 name. A bare city/county/district name that merely repeats the question's region (e.g. "서울특별시 서초구" only) is NOT an address assertion: use null. If the answer gives only another shop's address, or no address, use null. If the answer writes the address in a language other than Korean, convert the place names to their standard Korean (Hangul) form and add the token ADDR_CONVERTED in note. Do not invent or complete an address that the answer does not state.
- type: the business category the answer states for the target shop, as exactly one of these 8 tokens: 한식, 중식, 일식, 양식, 분식, 치킨호프주점, 카페디저트, 기타 (양식 = 양식·경양식, 치킨호프주점 = 치킨·호프·주점, 카페디저트 = 카페·디저트; see rule section 3). Use null if the answer states no category for the target shop, or says it cannot tell. A category that is only a guess from the name still counts if the answer states it as the shop's type (e.g. "probably a chicken restaurant" -> 치킨호프주점); use "기타" for a stated category that fits none of the other seven.
- note: optional, at most 15 words in English, only for real ambiguity (otherwise empty string).

Steps:
1. Use the Read tool once to read the input file below (JSON Lines; each line is {"item_id", "lang", "question", "answer"}). Do not read, list, or search any other file.
2. Judge EVERY item independently, in file order. Do not let one item influence another. Do not use any tool other than one Read and one Write. No web search, no web fetch, no shell.
3. Use the Write tool once to write the output file: exactly one JSON object per line, one line per input item, same order, item_id copied exactly, valid JSON (escape quotes inside strings):
   {"item_id": "...", "status": "open|closed|unknown", "address": "<string>" or null, "type": "<one of the 8 tokens>" or null, "note": "..."}
4. Reply with exactly one line and nothing else: ITEMS=<number of lines written>

Input file: ${DIR}/in/${b}.jsonl
Output file: ${DIR}/out/${b}.jsonl`
}
const results = {}
let bad = []
for (let i = 0; i < todo.length; i += 3) {
  const group = todo.slice(i, i + 3)
  const rs = await parallel(group.map(b => () => agent(PROMPT(b), { label: b, phase: 'Judge', agentType: 'general-purpose', model: 'sonnet' })))
  group.forEach((b, k) => {
    const r = rs[k] ? String(rs[k]) : ''
    results[b] = r.slice(0, 120)
    const m = /ITEMS=(\d+)/.exec(r)
    if (!m || (sizes[b] && Number(m[1]) !== sizes[b])) bad.push(b)
  })
  log(`${Math.min(i + 3, todo.length)}/${todo.length} batches`)
}
log(bad.length ? `check these batches (merge.py will validate): ${bad.join(',')}` : 'all batches done')
return { ran: Object.keys(results).length, bad, results }
