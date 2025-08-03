#!/bin/bash

CONFIG_DIR="$HOME/.config/git-commit-ai"
CONFIG_FILE="$CONFIG_DIR/config"
MODEL_FILE="$CONFIG_DIR/model"
BASE_URL_FILE="$CONFIG_DIR/base_url"
PROVIDER_FILE="$CONFIG_DIR/provider"

# Debug mode flag
DEBUG=false
# Push flag
PUSH=false
# Stage changes flag
STAGE_CHANGES=true
# Dry run flag
DRY_RUN=false
# Default providers and URLs
PROVIDER_OPENROUTER="openrouter"
PROVIDER_OLLAMA="ollama"
PROVIDER_LMSTUDIO="lmstudio"
PROVIDER_CUSTOM="custom"

OPENROUTER_URL="https://openrouter.ai/api/v1"
OLLAMA_URL="http://localhost:11434/api"
LMSTUDIO_URL="http://localhost:1234/v1"

# Default models for providers
OLLAMA_MODEL="qwen3:1.7b"
OPENROUTER_MODEL="google/gemini-flash-1.5-8b"
LMSTUDIO_MODEL="default"

# Debug function
debug_log() {
    if [ "$DEBUG" = true ]; then
        echo "DEBUG: $1"
        if [ ! -z "$2" ]; then
            echo "DEBUG: Content >>>"
            echo "$2"
            echo "DEBUG: <<<"
        fi
    fi
}

# Generic function to save config values
save_config() {
    local file="$1"
    local value="$2"
    local description="$3"
    
    mkdir -p "$CONFIG_DIR"
    # Special handling for API key to remove quotes and extra arguments
    if [ "$file" = "$CONFIG_FILE" ]; then
        value=$(echo "$value" | cut -d' ' -f1)
    fi
    echo "$value" >"$file"
    chmod 600 "$file"
    debug_log "$description saved to config file"
}

# Generic function to get config values
get_config() {
    local file="$1"
    local default="$2"
    
    if [ -f "$file" ]; then
        cat "$file"
    else
        echo "$default"
    fi
}

# Function to save API key
save_api_key() {
    save_config "$CONFIG_FILE" "$1" "API key"
}

# Function to get API key
get_api_key() {
    get_config "$CONFIG_FILE" ""
}

# Function to save model
save_model() {
    save_config "$MODEL_FILE" "$1" "Model"
}

# Function to get model
get_model() {
    get_config "$MODEL_FILE" ""
}

# Function to save base URL
save_base_url() {
    save_config "$BASE_URL_FILE" "$1" "Base URL"
}

# Function to save provider
save_provider() {
    save_config "$PROVIDER_FILE" "$1" "Provider"
}

# Function to get provider
get_provider() {
    get_config "$PROVIDER_FILE" "$PROVIDER_OPENROUTER"
}

# Function to get base URL
get_base_url() {
    get_config "$BASE_URL_FILE" "$OPENROUTER_URL"
}

# Escape string for JSON
json_escape() {
    python3 -c 'import json, sys; print(json.dumps(sys.stdin.read()))'
}


# Function to setup provider configuration
setup_provider() {
    local provider="$1"
    local base_url="$2"
    local model="$3"
    
    PROVIDER="$provider"
    BASE_URL="$base_url"
    MODEL="$model"
    save_provider "$PROVIDER"
    save_base_url "$BASE_URL"
    save_model "$MODEL"
}

# Load saved provider and base URL or use defaults
PROVIDER=$(get_provider)
BASE_URL=$(get_base_url)

# Get saved model or use default based on provider
MODEL=$(get_model)
if [ -z "$MODEL" ]; then
    case "$PROVIDER" in
    "$PROVIDER_OLLAMA")
        MODEL="$OLLAMA_MODEL"
        ;;
    "$PROVIDER_OPENROUTER")
        MODEL="$OPENROUTER_MODEL"
        ;;
    esac
fi

# Get saved base URL or use default
BASE_URL=$(get_base_url)

debug_log "Script started"
debug_log "Config directory: $CONFIG_DIR"

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"
debug_log "Config directory created/checked"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    --debug)
        DEBUG=true
        shift
        ;;
    --use-ollama)
        setup_provider "$PROVIDER_OLLAMA" "$OLLAMA_URL" "$OLLAMA_MODEL"
        shift
        ;;
    --use-openrouter)
        setup_provider "$PROVIDER_OPENROUTER" "$OPENROUTER_URL" "$OPENROUTER_MODEL"
        shift
        ;;
    --use-lmstudio)
        setup_provider "$PROVIDER_LMSTUDIO" "$LMSTUDIO_URL" "$LMSTUDIO_MODEL"
        shift
        ;;
    --use-custom)
        if [ -z "$2" ]; then
            echo "Error: --use-custom requires a base URL"
            exit 1
        fi
        PROVIDER="$PROVIDER_CUSTOM"
        BASE_URL="$2"
        save_provider "$PROVIDER"
        save_base_url "$BASE_URL"
        shift 2
        ;;
    --push | -p)
        PUSH=true
        shift
        ;;
    --no-stage)
        STAGE_CHANGES=false
        shift
        ;;
    --dry-run)
        DRY_RUN=true
        shift
        ;;
    -h | --help)
        echo "Usage: cmai [options] [api_key]"
        echo ""
        echo "Options:"
        echo "  --debug               Enable debug mode"
        echo "  --push, -p            Push changes after commit"
        echo "  --no-stage            Do not stage changes automatically"
        echo "  --dry-run             Preview commit message without executing git commit"
        echo "  --model <model>       Use specific model (default: google/gemini-flash-1.5-8b)"
        echo "  --use-ollama          Use Ollama as provider (saves for future use)"
        echo "  --use-openrouter      Use OpenRouter as provider (saves for future use)"
        echo "  --use-lmstudio        Use LMStudio as provider (saves for future use)"
        echo "  --use-custom <url>    Use custom provider with base URL (saves for future use)"
        echo "  -h, --help            Show this help message"
        echo ""
        echo "Examples:"
        echo "  cmai --api-key your_api_key          # First time setup with API key"
        echo "  cmai --use-ollama                    # Switch to Ollama provider"
        echo "  cmai --use-openrouter                # Switch back to OpenRouter"
        echo "  cmai --use-lmstudio                  # Switch to LMStudio provider"
        echo "  cmai --use-custom http://my-api.com  # Use custom provider"
        exit 0
        ;;
    --model)
        # Check if next argument exists and doesn't start with -
        if [[ -n "$2" && "$2" != -* ]]; then
            # Remove any quotes from model name and save it
            MODEL=$(echo "$2" | tr -d '"')
            save_model "$MODEL"
            debug_log "New model saved: $MODEL"
            shift 2
        else
            echo "Error: --model requires a valid model name"
            exit 1
        fi
        ;;
    --base-url)
        # Check if next argument exists and doesn't start with -
        if [[ -n "$2" && "$2" != -* ]]; then
            BASE_URL="$2"
            save_base_url "$BASE_URL"
            debug_log "New base URL saved: $BASE_URL"
            shift 2
        else
            echo "Error: --base-url requires a valid URL"
            exit 1
        fi
        ;;
    --api-key)
        # Check if next argument exists and doesn't start with -
        if [[ -n "$2" && "$2" != -* ]]; then
            save_api_key "$2"
            debug_log "New API key saved"
            shift 2
        else
            echo "Error: --api-key requires a valid API key"
            exit 1
        fi
        ;;
    *)
        echo "Error: Unknown argument $1"
        exit 1
        ;;
    esac
done

# Get API key from config
API_KEY=$(get_api_key)
debug_log "API key retrieved from config"

if [ -z "$API_KEY" ] && [ "$PROVIDER" = "$PROVIDER_OPENROUTER" ]; then
    echo "No API key found. Please provide the OpenRouter API key using --api-key flag"
    echo "Usage: cmai [--debug] [--push|-p] [--use-ollama] [--model <model_name>] [--base-url <url>] [--api-key <key>]"
    exit 1
fi

# Set default model based on provider
if [ "$PROVIDER" = "$PROVIDER_OLLAMA" ]; then
    [ -z "$MODEL" ] && MODEL="$OLLAMA_MODEL"
    # Check if Ollama is running
    if ! pgrep ollama >/dev/null; then
        echo "Error: Ollama server not running. Please start Ollama first:"
        echo "ollama serve"
        exit 1
    fi
    # Check if model exists using ollama ls
    if ! ollama ls | awk '{print $1}' | grep -q "^${MODEL}$"; then
        echo "Error: Model '$MODEL' not found in Ollama. Please pull it first:"
        echo "ollama pull $MODEL"
        exit 1
    fi
fi

# Stage all changes
debug_log "Staging all changes"
if [ "$STAGE_CHANGES" = true ]; then
    git add .
fi

# Get git changes and clean up any tabs
# Get changes and format them appropriately for the provider
if [ "$PROVIDER" = "$PROVIDER_OLLAMA" ]; then
    CHANGES=$(git diff --cached --name-status | tr '\t' ' ' | tr '\n' ' ' | sed 's/  */ /g')
else
    CHANGES=$(git diff --cached --name-status | tr '\t' ' ' | sed 's/  */ /g')
fi
# Get git diff for context
DIFF_CONTENT=$(git diff --cached)

# Smart diff handling based on size to prevent token limit issues
# Token estimation: ~3.5 characters per token for code
# 32k token limit, but messages alone used 33k tokens in error case
# Need to be much more conservative: limit total message to ~20k tokens
# Diff content should be max ~10k tokens = ~35k characters
DIFF_CHAR_COUNT=${#DIFF_CONTENT}
SMALL_DIFF_LIMIT=15000    # Use full diff (~4.3k tokens)
MEDIUM_DIFF_LIMIT=50000   # Truncate diff 
USE_DIFF_CONTENT=true

debug_log "Diff content size: $DIFF_CHAR_COUNT characters"

if [ $DIFF_CHAR_COUNT -le $SMALL_DIFF_LIMIT ]; then
    debug_log "Using full diff content (small diff)"
elif [ $DIFF_CHAR_COUNT -le $MEDIUM_DIFF_LIMIT ]; then
    debug_log "Truncating diff content (medium diff)"
    TRUNCATE_TO=12000  # ~3.4k tokens for diff content
    DIFF_CONTENT=$(echo "$DIFF_CONTENT" | head -c $TRUNCATE_TO)
    DIFF_CONTENT="$DIFF_CONTENT

[... diff truncated due to size - showing first $TRUNCATE_TO characters only]"
else
    debug_log "Diff too large ($DIFF_CHAR_COUNT chars), using file list only"
    USE_DIFF_CONTENT=false
    # Get more detailed file statistics for very large diffs
    DETAILED_CHANGES=$(git diff --cached --stat)
fi

debug_log "Git changes detected" "$CHANGES"

if [ -z "$CHANGES" ]; then
    echo "No staged changes found. Please stage your changes using 'git add' first."
    exit 1
fi

# Keep CHANGES as raw content for proper JSON escaping

# Set model based on provider if not explicitly specified
if [ -z "$MODEL" ]; then
    case "$PROVIDER" in
    "$PROVIDER_OLLAMA")
        MODEL="$OLLAMA_MODEL"
        ;;
    "$PROVIDER_OPENROUTER")
        MODEL="$OPENROUTER_MODEL"
        ;;
    "$PROVIDER_LMSTUDIO")
        MODEL="$LMSTUDIO_MODEL"
        ;;
    esac
fi

# All providers now use raw content with proper JSON escaping
# No pre-formatting needed since json_escape handles everything

# Common prompt instructions
COMMON_INSTRUCTIONS="Follow the conventional commits format: <type>(<scope>): <subject>\n\n<body>\n\nWhere type is one of: feat, fix, docs, style, refactor, perf, test, chore.\n- Scope: max 3 words.\n- Keep the subject under 70 chars.\n- Body: list changes to explain what and why\n- Use 'fix' for minor changes\n- Do not wrap your response in triple backticks\n- Response should be the commit message only, no explanations."

# System message constant
SYSTEM_MESSAGE="You are a git commit message generator. Create conventional commit messages."

# Function to build chat request for OpenRouter/Custom providers
build_openrouter_request() {
    local model="$1"
    local changes="$2"
    local diff="$3"
    local use_diff="$4"
    local detailed_changes="$5"
    
    if [ "$use_diff" = "true" ]; then
        local user_content="Generate a commit message for these changes:

## File changes:
<file_changes>
$changes
</file_changes>

## Diff:
<diff>
$diff
</diff>

## Format:
<type>(<scope>): <subject>

<body>

Important:
- Type must be one of: feat, fix, docs, style, refactor, perf, test, chore
- Subject: max 70 characters, imperative mood, no period
- Body: list changes to explain what and why, not how
- Scope: max 3 words
- For minor changes: use 'fix' instead of 'feat'
- Do not wrap your response in triple backticks
- Response should be the commit message only, no explanations."
    else
        local user_content="Generate a commit message for these changes:

## File changes:
<file_changes>
$changes
</file_changes>

## File statistics:
<file_stats>
$detailed_changes
</file_stats>

Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only.

## Format:
<type>(<scope>): <subject>

<body>

Important:
- Type must be one of: feat, fix, docs, style, refactor, perf, test, chore
- Subject: max 70 characters, imperative mood, no period
- Body: list changes to explain what and why, not how
- Scope: max 3 words
- For minor changes: use 'fix' instead of 'feat'
- Do not wrap your response in triple backticks
- Response should be the commit message only, no explanations."
    fi
    
    # Properly escape the user content for JSON
    local user_content_escaped=$(echo "$user_content" | json_escape)
    local system_message_escaped=$(echo "$SYSTEM_MESSAGE" | json_escape)
    
    cat <<EOF
{
  "model": "$model",
  "stream": false,
  "messages": [
    {
      "role": "system",
      "content": $system_message_escaped
    },
    {
      "role": "user",
      "content": $user_content_escaped
    }
  ]
}
EOF
}

# Function to build user content for LMStudio (needs JSON escaping)
build_user_content_lmstudio() {
    local changes="$1"
    local diff="$2"
    local use_diff="$3"
    local detailed_changes="$4"
    
    if [ "$use_diff" = "true" ]; then
        cat <<EOF
Generate a commit message for these changed files:  
<file_changes>
$changes.
</file_changes>

## Diff:
<diff>
$diff
</diff>

$COMMON_INSTRUCTIONS
EOF
    else
        cat <<EOF
Generate a commit message for these changed files:  
<file_changes>
$changes.
</file_changes>

## File statistics:
<file_stats>
$detailed_changes
</file_stats>

Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only.

$COMMON_INSTRUCTIONS
EOF
    fi
}

# Make the API request
case "$PROVIDER" in
"$PROVIDER_OLLAMA")
    debug_log "Making API request to Ollama"
    ENDPOINT="api/generate"
    HEADERS=(-H "Content-Type: application/json")
    BASE_URL="http://localhost:11434"
    
    if [ "$USE_DIFF_CONTENT" = "true" ]; then
        OLLAMA_PROMPT="Generate a conventional commit message for these changes: 
<file_changes>
$CHANGES
</file_changes>

## Diff:
<diff>
$DIFF_CONTENT
</diff>

## Instructions:
$COMMON_INSTRUCTIONS"
    else
        OLLAMA_PROMPT="Generate a conventional commit message for these changes: 
<file_changes>
$CHANGES
</file_changes>

## File statistics:
<file_stats>
$DETAILED_CHANGES
</file_stats>

Note: Diff content was too large to include. Please generate commit message based on file changes and statistics only.

## Instructions:
$COMMON_INSTRUCTIONS"
    fi
    
    # Use json_escape to properly escape the prompt for JSON
    OLLAMA_PROMPT_ESCAPED=$(echo "$OLLAMA_PROMPT" | json_escape)
    
    REQUEST_BODY=$(
        cat <<EOF
{
  "model": "$MODEL",
  "prompt": $OLLAMA_PROMPT_ESCAPED,
  "think": false,
  "stream": false
}
EOF
    )
    ;;
"$PROVIDER_LMSTUDIO")
    debug_log "Making API request to LMStudio"
    ENDPOINT="chat/completions"
    HEADERS=(-H "Content-Type: application/json")

    if [ "$USE_DIFF_CONTENT" = "true" ]; then
        USER_CONTENT=$(build_user_content_lmstudio "$CHANGES" "$DIFF_CONTENT" "$USE_DIFF_CONTENT" "")
    else
        USER_CONTENT=$(build_user_content_lmstudio "$CHANGES" "" "$USE_DIFF_CONTENT" "$DETAILED_CHANGES")
    fi
    USER_CONTENT_ESCAPED=$(echo "$USER_CONTENT" | json_escape)
    
    REQUEST_BODY=$(cat <<EOF
{
  "model": "$MODEL",
  "stream": false,
  "messages": [
    {
      "role": "system",
      "content": "$SYSTEM_MESSAGE"
    },
    {
      "role": "user",
      "content": $USER_CONTENT_ESCAPED
    }
  ]
}
EOF
)
    ;;
"$PROVIDER_OPENROUTER")
    debug_log "Making API request to OpenRouter"
    ENDPOINT="chat/completions"
    HEADERS=(
        "HTTP-Referer: https://github.com/mrgoonie/cmai"
        "Authorization: Bearer $API_KEY"
        "Content-Type: application/json"
        "X-Title: cmai - AI Commit Message Generator"
    )
    REQUEST_BODY=$(build_openrouter_request "$MODEL" "$CHANGES" "$DIFF_CONTENT" "$USE_DIFF_CONTENT" "$DETAILED_CHANGES")
    ;;
"$PROVIDER_CUSTOM")
    debug_log "Making API request to custom provider"
    ENDPOINT="chat/completions"
    [ ! -z "$API_KEY" ] && HEADERS=(-H "Authorization: Bearer ${API_KEY}")
    REQUEST_BODY=$(build_openrouter_request "$MODEL" "$CHANGES" "$DIFF_CONTENT" "$USE_DIFF_CONTENT" "$DETAILED_CHANGES")
    ;;
esac

# Debug
debug_log "Using provider: $PROVIDER"
debug_log "Provider endpoint: $ENDPOINT"
debug_log "Request headers: ${HEADERS}"
debug_log "Request model: ${MODEL}"
debug_log "Request body: $REQUEST_BODY"

# Convert headers array to proper curl format
CURL_HEADERS=()
for header in "${HEADERS[@]}"; do
    CURL_HEADERS+=(-H "$header")
done

RESPONSE=$(curl -s -X POST "$BASE_URL/$ENDPOINT" \
    "${CURL_HEADERS[@]}" \
    -d "$REQUEST_BODY")
debug_log "API response received" "$RESPONSE"

# Function to handle common error checking
check_api_errors() {
    local response="$1"
    local provider="$2"
    
    case "$provider" in
    "$PROVIDER_OLLAMA")
        if echo "$response" | grep -q "404 page not found"; then
            echo "Error: Ollama API endpoint not found. Make sure Ollama is running and try again."
            echo "Run: ollama serve"
            exit 1
        fi
        if echo "$response" | grep -q "error"; then
            ERROR=$(echo "$response" | jq -r '.error')
            echo "Error from Ollama: $ERROR"
            exit 1
        fi
        ;;
    "$PROVIDER_LMSTUDIO")
        if echo "$response" | grep -q "<!DOCTYPE html>"; then
            echo "Error: LMStudio API returned HTML error. Make sure LMStudio is running and the API is accessible."
            echo "Response: $response"
            exit 1
        fi
        if echo "$response" | jq -e '.error' >/dev/null 2>&1; then
            ERROR=$(echo "$response" | jq -r '.error.message // .error' 2>/dev/null)
            echo "Error from LMStudio: $ERROR"
            exit 1
        fi
        ;;
    esac
}

# Function to extract commit message from response
extract_commit_message() {
    local response="$1"
    local provider="$2"
    
    case "$provider" in
    "$PROVIDER_OLLAMA")
        COMMIT_FULL=$(echo "$response" | jq -r '.response // empty')
        if [ -z "$COMMIT_FULL" ]; then
            echo "Error: Failed to get response from Ollama. Response: $response"
            exit 1
        fi
        ;;
    "$PROVIDER_LMSTUDIO")
        COMMIT_FULL=$(echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null)
        if [ $? -ne 0 ] || [ -z "$COMMIT_FULL" ] || [ "$COMMIT_FULL" = "null" ]; then
            echo "Error: Failed to parse LMStudio response. Response format may be unexpected."
            echo "Response: $response"
            exit 1
        fi
        ;;
    "$PROVIDER_OPENROUTER" | "$PROVIDER_CUSTOM")
        COMMIT_FULL=$(echo "$response" | jq -r '.choices[0].message.content')
        # If jq fails or returns null, fallback to grep method
        if [ -z "$COMMIT_FULL" ] || [ "$COMMIT_FULL" = "null" ]; then
            COMMIT_FULL=$(echo "$response" | grep -o '"content":"[^"]*"' | cut -d'"' -f4)
        fi
        ;;
    esac
}

# Extract and clean the commit message
check_api_errors "$RESPONSE" "$PROVIDER"
extract_commit_message "$RESPONSE" "$PROVIDER"

# Clean the message:
# 1. Preserve the structure of the commit message
# 2. Clean up escape sequences
COMMIT_FULL=$(echo "$COMMIT_FULL" |
    sed 's/\\n/\n/g' |
    sed 's/\\r//g' |
    sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' |
    sed 's/\\[[:alpha:]]//g')

debug_log "Extracted commit message" "$COMMIT_FULL"

if [ -z "$COMMIT_FULL" ]; then
    echo "Failed to generate commit message. API response:"
    echo "$RESPONSE"
    exit 1
fi

# Execute git commit or preview in dry-run mode
if [ "$DRY_RUN" = true ]; then
    echo "Dry run mode - Generated commit message:"
    echo "======================================="
    echo "$COMMIT_FULL"
    echo "======================================="
    echo "Use 'cmai' without --dry-run to execute the commit."
else
    debug_log "Executing git commit"
    git commit -m "$COMMIT_FULL"

    if [ $? -ne 0 ]; then
        echo "Failed to commit changes"
        exit 1
    fi

    # Push to origin if flag is set
    if [ "$PUSH" = true ]; then
        debug_log "Pushing to origin"
        git push origin

        if [ $? -ne 0 ]; then
            echo "Failed to push changes"
            exit 1
        fi
        echo "Successfully pushed changes to origin"
    fi

    echo "Successfully committed changes with message:"
    echo "$COMMIT_FULL"
fi
debug_log "Script completed successfully"
