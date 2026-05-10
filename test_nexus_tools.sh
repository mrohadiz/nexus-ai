#!/bin/bash

echo "=========================================="
echo "Testing Nexus-AI Tool Integration"
echo "=========================================="
echo ""

# Test 1: Health check
echo "🏥 Test 1: Health check..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo "---"
echo ""

# Test 2: Regular chat (no tools)
echo "💬 Test 2: Regular chat..."
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "session_id": "test-1"
  }' | python3 -m json.tool
echo ""
echo "---"
echo ""

# Test 3: Chat with tools (streaming)
echo "🔧 Test 3: Chat with tools (streaming endpoint)..."
echo "Note: This will stream responses with potential tool calls"
curl -s -X POST http://localhost:8000/chat/tools \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the latest news about AI?",
    "session_id": "test-tools-1",
    "model": "gpt-4o-mini"
  }'
echo ""
echo "---"
echo ""

# Test 4: Autonomous research
echo "🔍 Test 4: Autonomous research..."
echo "This may take a minute as it performs multiple searches..."
curl -s -X POST http://localhost:8000/research/autonomous \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Research the benefits of renewable energy",
    "session_id": "research-test-1"
  }' | python3 -m json.tool
echo ""
echo "---"
echo ""

# Test 5: Task planning
echo "📋 Test 5: Task planning..."
curl -s -X POST http://localhost:8000/planning/task \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a plan to build a web scraping application",
    "session_id": "planning-test-1"
  }' | python3 -m json.tool
echo ""
echo "---"
echo ""

echo "✅ All Nexus-AI tests completed!"
echo ""
echo "Check the server logs for detailed execution information."
