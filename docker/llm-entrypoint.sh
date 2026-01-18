#!/bin/bash
set -e

echo "=================================================="
echo "Starting Ollama with auto-model-pull"
echo "=================================================="

# Start Ollama service in background
echo "[1/4] Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "[2/4] Waiting for Ollama API to be ready..."
for i in {1..30}; do
    if ollama list >/dev/null 2>&1; then
        echo "✓ Ollama API is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "✗ Ollama API failed to start after 30 seconds"
        exit 1
    fi
    echo "  Waiting for API... ($i/30)"
    sleep 1
done

# Check if llama3 model exists
echo "[3/4] Checking for llama3 model..."
if ollama list | grep -q "llama3"; then
    echo "✓ llama3 model already exists"
else
    echo "✗ llama3 model not found"
    echo "[3/4] Pulling llama3 model (this may take 5-10 minutes on first run)..."
    echo "=================================================="
    ollama pull llama3
    echo "=================================================="
    echo "✓ llama3 model downloaded successfully"
fi

echo "[4/4] Ollama is ready with llama3 model"
echo "=================================================="
echo "System ready for LLM analysis"
echo "=================================================="

# Keep Ollama running in foreground
wait $OLLAMA_PID
