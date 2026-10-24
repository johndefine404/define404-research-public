#!/bin/bash
# W-mem 수집을 끝날 때까지 이어 돌린다. 하루 한도에 닿으면 UTC 0시 5분까지 기다렸다가 다시 시작한다.
# 세션과 분리해서 돈다(nohup). 로그: collect/wmem.log
cd "$(dirname "$0")/.."
while true; do
  out=$(python3 collect/run_wmem.py 2>&1 | tail -1); echo "$(date '+%F %T') $out"
  case "$out" in finished*) break ;; esac
  now=$(date -u +%s); next=$(date -u -j -f "%Y-%m-%d %H:%M" "$(date -u -v+1d +%Y-%m-%d) 00:05" +%s)
  case "$out" in "budget stop"*|limit*) sleep $((next-now)) ;; *) sleep 120 ;; esac
done
