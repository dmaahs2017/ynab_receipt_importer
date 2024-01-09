#!/usr/bin/env bash

IMAGE_FILE=${1}
if [[ ! -f ${IMAGE_FILE} ]]; then
  echo "file not found"
  exit 1
fi
FILE_DATA=$(cat ${IMAGE_FILE} | base64 -w0)

# Function URL
function_url="https://3kd4bmtogiwxuoqkqn2adzj3ye0cqysa.lambda-url.us-east-1.on.aws/"

# Service details
service="lambda"
region="us-east-1"

# Request parameters
method="POST"
content_type="application/json"
request_payload="{
  \"RequestType\": \"put\",
  \"YnabKey\": \"empty\",
  \"BudgetId\": \"00d897bf-4703-4976-af2a-35d1bdc9b673\",
  \"DryRun\": \"true\",
  \"Receipt\": \"${FILE_DATA}\"
}"

if [[ -f payload.json ]]; then
  echo "please delete the payload.json file and re-run"
  exit 1
fi

echo "${request_payload}" > payload.json

# Use curl to make the request
curl -X $method -H "Content-Type: $content_type" \
    --data-binary "@payload.json" \
    --user "$AWS_ACCESS_KEY_ID":"$AWS_SECRET_ACCESS_KEY" \
    --aws-sigv4 "aws:amz:${region}:${service}" \
    ${function_url}

if [[ -f payload.json ]]; then
  rm payload.json
fi
