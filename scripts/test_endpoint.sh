#!/bin/bash

# Test script for the Agentic Honey-Pot API

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-your_secure_api_key_here}"

echo "Testing Agentic Honey-Pot API at $API_URL"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
    return $1
}

# Test 1: Health check
echo -e "\n1. Testing health check endpoint..."
response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
print_result $( [ "$http_code" = "200" ] && echo 0 || echo 1 ) "Health check (HTTP $http_code)"
echo "Response: $body"

# Test 2: Create new conversation
echo -e "\n2. Creating new conversation..."
response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $API_KEY" \
    "$API_URL/api/v1/conversation/new")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
print_result $( [ "$http_code" = "200" ] && echo 0 || echo 1 ) "Create conversation (HTTP $http_code)"
echo "Response: $body"

# Extract conversation ID
CONVERSATION_ID=$(echo "$body" | grep -o '"conversation_id":"[^"]*"' | cut -d'"' -f4)
echo "Conversation ID: $CONVERSATION_ID"

# Test 3: Process scam message
echo -e "\n3. Processing scam message..."
response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"conversation_id\": \"$CONVERSATION_ID\",
        \"message\": \"Congratulations! You've won Rs. 50,000 in our lottery. To claim, send Rs. 500 to this UPI ID: winner@paytm\",
        \"sender_id\": \"scammer123\",
        \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)\",
        \"conversation_history\": []
    }" \
    "$API_URL/api/v1/conversation/message")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
print_result $( [ "$http_code" = "200" ] && echo 0 || echo 1 ) "Process scam message (HTTP $http_code)"
echo "Response: $body"

# Test 4: Get conversation history
echo -e "\n4. Getting conversation history..."
response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $API_KEY" \
    "$API_URL/api/v1/conversation/$CONVERSATION_ID")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
print_result $( [ "$http_code" = "200" ] && echo 0 || echo 1 ) "Get conversation (HTTP $http_code)"
echo "Response: $body"

# Test 5: Invalid API key
echo -e "\n5. Testing invalid API key..."
response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer invalid_key" \
    "$API_URL/api/v1/conversation/new")
http_code=$(echo "$response" | tail -n1)
print_result $( [ "$http_code" = "403" ] && echo 0 || echo 1 ) "Invalid API key rejected (HTTP $http_code)"

echo -e "\n=========================================="
echo "Test suite completed!"
