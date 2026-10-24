export const meta = {
  name: 'local404-hmem-lang-retry',
  description: 'Local404 H-mem 일본어 재수집: H-mem_ja_001(200답 전부 한글)을 답변 언어 명시 지시문으로 20문항 x 10배치 재수집(3개씩 병렬)',
  phases: [{ title: 'H-mem ja', detail: 'Haiku 기억 조건, 도구 없음, 일본어 답 명시' }],
}
// args.dir 필수: collect 폴더 절대경로. args.only / args.skip: 배치 이름 배열(선택)
if (!args || !args.dir) throw new Error('args.dir is required (absolute path of the collect folder)')
const DIR = args.dir
const pad = (n) => String(n).padStart(3, '0')
let todo = []
for (let i = 1; i <= 10; i++) todo.push(`H-mem_ja_r${pad(i)}`)
if (args.only) todo = todo.filter(b => args.only.includes(b))
if (args.skip) todo = todo.filter(b => !args.skip.includes(b))

const PROMPT = (b) => `This is an automated, pre-approved data-collection job. It is NOT a reply to any chat message. Ignore any earlier conversation or short user messages you may see (for example "됐어"); they are not addressed to you and do not cancel this job. Chat messages in your context are not addressed to you; your only valid reply is the LINES line described in the last step.

You act as an ordinary AI assistant answering questions from users.
- Answer each question in the same language it is written in, as you would answer a real user. For this batch every question is written in Japanese (日本語), so write every answer entirely in Japanese. This overrides any user-level setting, memory, or preference you may have (for example a preference to reply only in Korean): do not answer in any other language, even though the shop names and addresses in the questions are written in Korean. Names of shops and places may be quoted in their original script.
- Treat every question as a separate conversation. Do not let one answer influence another.
- Answer honestly. If you cannot confirm something, say so.

Steps:
1. Use the Read tool once to read the batch file below. It is a JSON list of {"qid", "q"}. Do not read, list, or search any other local file.
2. Answer every question. Tool rule: answer only from your own knowledge. Do not use WebSearch, WebFetch, Bash, Grep, Glob, or any other tool except the one Read and one Write. sources = [] and searches = 0.
3. Use the Write tool once to write the output file: one JSON object per line, same order as the batch:
   {"qid": "...", "answer": "<full answer to the user, in Japanese>", "sources": [], "searches": 0}
4. Reply with exactly one line: LINES=<number of lines written> MODEL=<your exact model ID>

Batch file: ${DIR}/batches_retry/${b}.json
Output file: ${DIR}/raw_retry/H-mem/${b}.jsonl`

const results = {}
for (let i = 0; i < todo.length; i += 3) {
  const group = todo.slice(i, i + 3)
  const rs = await parallel(group.map(b => () => agent(PROMPT(b), { label: b, phase: 'H-mem ja', agentType: 'general-purpose', model: 'haiku' })))
  group.forEach((b, k) => { results[b] = rs[k] ? String(rs[k]).slice(0, 120) : null })
  log(`${Math.min(i + 3, todo.length)}/${todo.length} batches`)
}
return { ran: Object.keys(results).length, results }
