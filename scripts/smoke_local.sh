#!/usr/bin/env bash
# Local end-to-end smoke: session -> otp -> verify -> consents.
set -e
LAST_SID=$SID
BASE=http://localhost:8000
SID=$(curl -s $BASE/v1/sessions -X POST -H "Content-Type: application/json" \
  -d '{"language":"english"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['session_id'])")
echo "1 session created: $SID"
OTPRESP=$(curl -s $BASE/v1/sessions/$SID/otp -X POST -H "Content-Type: application/json" \
  -d '{"action":"send","aadhaar_number":"999999990019","consent":true}')
echo "2 otp send:     $OTPRESP"
CODE=$(echo "$OTPRESP" | python3 -c "import json,sys; print(json.load(sys.stdin)['dev_otp'])")
echo "3 otp verify:"
curl -s $BASE/v1/sessions/$SID/otp -X POST -H "Content-Type: application/json" \
  -d "{\"action\":\"verify\",\"otp\":\"$CODE\"}"
echo
echo "4 consents:"
curl -s $BASE/v1/sessions/$SID/consents -X POST -H "Content-Type: application/json" \
  -d '{"scope":["aa","uli"]}' | head -c 400
echo

SID=$(echo "$SID" 2>/dev/null || true)
