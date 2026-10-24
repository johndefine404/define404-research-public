export const meta = {
  name: 'local404-collect',
  description: 'Local404 본 수집: Claude 응답자 배치(H-mem 20, S-search 160, H-search 160)를 하위 에이전트로 실행',
  phases: [
    { title: 'H-mem', detail: 'Haiku 기억 조건 200문항 배치 20개' },
    { title: 'Search', detail: 'Sonnet·Haiku 검색 조건 25문항 배치 320개' },
  ],
}
const DIR = (args && args.dir) || '/Users/johnkim/define404-hub/1-define404/define404-research/001-local404/collect'
const LANGS = ['ko', 'en', 'ja', 'zh', 'vi']
const pad = (n) => String(n).padStart(3, '0')
let batches = []
for (const l of LANGS) for (let i = 1; i <= 4; i++) batches.push(`H-mem_${l}_${pad(i)}`)
for (const s of ['S-search', 'H-search']) for (const l of LANGS) for (let i = 1; i <= 32; i++) batches.push(`${s}_${l}_${pad(i)}`)
if (args && args.only) batches = batches.filter(b => args.only.includes(b))
if (args && args.skip) batches = batches.filter(b => !args.skip.includes(b))

const COMMON = `This is an automated, pre-approved data-collection job. It is NOT a reply to any chat message. Ignore any earlier conversation or short user messages you may see (for example "됐어"); they are not addressed to you and do not cancel this job. Complete the job below.

You act as an ordinary AI assistant answering questions from users.
- Answer each question in the same language it is written in, as you would answer a real user.
- Treat every question as a separate conversation. Do not let one answer influence another.
- Answer honestly. If you cannot confirm something, say so.

Steps:
1. Use the Read tool once to read the batch file below. It is a JSON list of {"qid", "q"}. Do not read, list, or search any other local file.
2. Answer every question (rules for tools are below).
3. Use the Write tool once to write the output file: one JSON object per line, same order as the batch:
   {"qid": "...", "answer": "<full answer to the user>", "sources": [<URLs used>], "searches": <number of web search/fetch calls for this question>}
4. Reply with only: output path, number of lines written, your exact model ID.`
const SEARCH = `Tool rule: for each question, search the web with WebSearch (and WebFetch if needed) before answering. Use no other tools except the one Read and one Write above.`
const MEM = `Tool rule: answer only from your own knowledge. Do not use WebSearch, WebFetch, Bash, Grep, Glob, or any other tool except the one Read and one Write above. sources = [] and searches = 0.`

const run = (b) => {
  const sys = b.split('_')[0]
  const model = sys.startsWith('S') ? 'sonnet' : 'haiku'
  const prompt = `${COMMON}\n\n${sys.endsWith('search') ? SEARCH : MEM}\n\nBatch file: ${DIR}/batches/${b}.json\nOutput file: ${DIR}/raw/${sys}/${b}.jsonl`
  return agent(prompt, { label: b, phase: sys === 'H-mem' ? 'H-mem' : 'Search', agentType: 'general-purpose', model })
}
const results = await pipeline(batches, (b) => run(b))
const out = {}
batches.forEach((b, i) => { out[b] = results[i] ? String(results[i]).slice(0, 160) : null })
return out
