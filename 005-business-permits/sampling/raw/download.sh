#!/bin/bash
# usage: dl.sh publicDataPk outdir
pk=$1; out=$2; mkdir -p $out
page=$(curl -sL "https://www.data.go.kr/data/$pk/fileData.do")
uddi=$(echo "$page" | grep -o -E "fn_fileDataDown\('$pk', 'uddi:[^']+'" | head -1 | grep -o "uddi:[^']*")
title=$(echo "$page" | grep -o '<title>[^<]*' | sed 's/<title>//; s/ | 공공데이터포털//')
j=$(curl -s -X POST https://www.data.go.kr/tcs/dss/selectFileDataDownload.do -d "publicDataDetailPk=$uddi&publicDataPk=$pk&atchFileId=&fileDetailSn=1&publicDataTyCode=PR0051")
aid=$(echo "$j" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('atchFileId',''))")
ext=$(echo "$j" | python3 -c "import json,sys;d=json.load(sys.stdin);print((d['dataSetFileDetailInfo'].get('atchFileExtsn') or d['dataSetFileDetailInfo'].get('extsn') or 'bin').lower())" 2>/dev/null)
curl -s -X POST https://www.data.go.kr/cmm/cmm/check-limit.json -d "atchFileId=$aid&fileDetailSn=1" >/dev/null
curl -sL -o "$out/$pk.$ext" "https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=$aid&fileDetailSn=1&dataNm=x"
echo "$pk|$title|$aid|$out/$pk.$ext|$(wc -c < $out/$pk.$ext)"
