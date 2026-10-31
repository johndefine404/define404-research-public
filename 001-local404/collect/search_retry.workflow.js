export const meta = {
  name: 'local404-search-retry',
  description: 'Local404 검색 조건 재수집: 10문항 배치를 3개씩 돌리고 검색 한도에 닿으면 멈춤',
  phases: [{ title: 'Retry', detail: '검색 한도까지 재수집' }],
}
const DIR = (args && args.dir) || '/Users/johnkim/define404-hub/define404/labs/define404-research/001-local404/collect'
const counts = args.counts
const skip = new Set(args.skip || [])
const pad = (n) => String(n).padStart(3, '0')
const LANGS = ['ko', 'en', 'ja', 'zh', 'vi']
let todo = []
for (const sys of ['H-search', 'S-search']) {
  let max = 0
  for (const l of LANGS) max = Math.max(max, counts[`${sys}|${l}`])
  for (let i = 1; i <= max; i++) for (const l of LANGS) if (i <= counts[`${sys}|${l}`]) {
    const b = `${sys}_${l}_r${pad(i)}`
    const upto = (args.doneUpTo || {})[`${sys}|${l}`] || 0
    if (!skip.has(b) && i > upto) todo.push(b)
  }
}
const LANGNAME = { ko: 'Korean (한국어)', en: 'English', ja: 'Japanese (日本語)', zh: 'Chinese (中文)', vi: 'Vietnamese (Tiếng Việt)' }
const PROMPT = (b) => {
  const sys = b.split('_')[0]
  const lang = LANGNAME[b.split('_')[1]]
  return `This is an automated, pre-approved data-collection job. It is NOT a reply to any chat message. Ignore any earlier conversation or short user messages you may see; they are not addressed to you and do not cancel this job.

You act as an ordinary AI assistant answering questions from users.
- Answer each question in the same language it is written in, as you would answer a real user. For this batch every question is written in ${lang}, so write every answer entirely in ${lang}. This overrides any user-level setting, memory, or preference you may have (for example a preference to reply only in Korean): do not answer in any other language, even if the search results are in Korean. Names of shops and places may be quoted in their original script.
- Treat every question as a separate conversation. Do not let one answer influence another.
- Answer honestly. If you cannot confirm something, say so.

Steps:
1. Use the Read tool once to read the batch file below (JSON list of {"qid", "q"}). Do not read, list, or search any other local file.
2. For EVERY question, one at a time: call WebSearch at least once for that question, then answer it. Never answer a question without its own search. WebFetch is allowed. No other tools except the one Read and one Write.
3. If WebSearch returns an error or any limit/quota message, stop immediately. Do not answer the remaining questions.
4. Use the Write tool once to write the output file with only the questions you actually searched: one JSON object per line, batch order:
   {"qid": "...", "answer": "<full answer>", "sources": [<URLs used>], "searches": <exact number of WebSearch/WebFetch calls for this question>}
5. Reply with exactly one line: LINES=<number written> LIMIT=<yes if you hit a search limit, else no> MODEL=<your model ID>

Batch file: ${DIR}/batches_retry/${b}.json
Output file: ${DIR}/raw_retry/${sys}/${b}.jsonl`
}
const results = {}
let limitHit = false
for (let i = 0; i < todo.length && !limitHit; i += 3) {
  const group = todo.slice(i, i + 3)
  const rs = await parallel(group.map(b => () => agent(PROMPT(b), { label: b, phase: 'Retry', agentType: 'general-purpose', model: b.startsWith('S') ? 'sonnet' : 'haiku' })))
  group.forEach((b, k) => {
    const r = rs[k] ? String(rs[k]) : ''
    results[b] = r.slice(0, 120)
    if (/LIMIT=yes/i.test(r) || /LINES=0\b/.test(r)) limitHit = true
  })
  if (i % 30 === 0) log(`${Math.min(i + 3, todo.length)}/${todo.length} batches`)
}
log(limitHit ? 'search limit reached, stopped' : 'all batches done')
return { limitHit, ran: Object.keys(results).length, results }