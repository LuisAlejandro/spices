#!/bin/bash
# Logging utilities for Docker tests

# Color codes for terminal output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly MAGENTA='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Log levels
readonly LOG_LEVEL_DEBUG=0
readonly LOG_LEVEL_INFO=1
readonly LOG_LEVEL_WARN=2
readonly LOG_LEVEL_ERROR=3

# Default log level
LOG_LEVEL=${LOG_LEVEL:-$LOG_LEVEL_INFO}

# Log file configuration
LOG_DIR="${LOG_DIR:-$(pwd)/scripts/logs/docker-tests}"
LOG_FILE="${LOG_FILE:-}"
JSON_LOG="${JSON_LOG:-false}"
ENABLE_COLORS="${ENABLE_COLORS:-true}"

# Initialize logging system
setup_logging() {
    local log_name="${1:-docker-tests}"
    local date_str=$(date +%Y-%m-%d)
    local timestamp=$(date +%Y%m%d_%H%M%S)

    # Create log directory structure
    mkdir -p "${LOG_DIR}/${date_str}"
    mkdir -p "${LOG_DIR}/latest"

    # Set log file path
    LOG_FILE="${LOG_DIR}/${date_str}/${log_name}_${timestamp}.log"

    # Create symlink to latest log
    ln -sf "${LOG_FILE}" "${LOG_DIR}/latest/${log_name}.log"

    # Initialize log file
    echo "# Docker Tests Log - Started at $(date)" >"${LOG_FILE}"
    echo "# Log Level: ${LOG_LEVEL}" >>"${LOG_FILE}"
    echo "# JSON Format: ${JSON_LOG}" >>"${LOG_FILE}"
    echo "" >>"${LOG_FILE}"

    log_info "Logging initialized: ${LOG_FILE}"
}

# Get current timestamp
get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# Get log level name
get_log_level_name() {
    case "$1" in
    $LOG_LEVEL_DEBUG) echo "DEBUG" ;;
    $LOG_LEVEL_INFO) echo "INFO" ;;
    $LOG_LEVEL_WARN) echo "WARN" ;;
    $LOG_LEVEL_ERROR) echo "ERROR" ;;
    *) echo "UNKNOWN" ;;
    esac
}

# Get log level color
get_log_level_color() {
    case "$1" in
    $LOG_LEVEL_DEBUG) echo "$CYAN" ;;
    $LOG_LEVEL_INFO) echo "$GREEN" ;;
    $LOG_LEVEL_WARN) echo "$YELLOW" ;;
    $LOG_LEVEL_ERROR) echo "$RED" ;;
    *) echo "$WHITE" ;;
    esac
}

# Core logging function
_log() {
    local level="$1"
    local message="$2"
    local component="${3:-MAIN}"
    local extra_data="${4:-}"

    # Check if message should be logged based on log level
    if [[ $level -lt $LOG_LEVEL ]]; then
        return 0
    fi

    local timestamp=$(get_timestamp)
    local level_name=$(get_log_level_name "$level")
    local color=$(get_log_level_color "$level")

    # Format message for terminal output
    local terminal_message=""
    if [[ "$ENABLE_COLORS" == "true" && -t 1 ]]; then
        terminal_message="${color}[${timestamp}] [${level_name}] [${component}]${NC} ${message}"
    else
        terminal_message="[${timestamp}] [${level_name}] [${component}] ${message}"
    fi

    # Output to terminal
    echo -e "$terminal_message" >&2

    # Log to file if configured
    if [[ -n "$LOG_FILE" ]]; then
        if [[ "$JSON_LOG" == "true" ]]; then
            # JSON format
            local json_entry=$(
                cat <<EOF
{
  "timestamp": "$timestamp",
  "level": "$level_name",
  "component": "$component",
  "message": "$message"$([ -n "$extra_data" ] && echo ",\"extra\": $extra_data")
}
EOF
            )
            echo "$json_entry" >>"$LOG_FILE"
        else
            # Plain text format
            echo "[${timestamp}] [${level_name}] [${component}] ${message}" >>"$LOG_FILE"
        fi
    fi
}

# Log debug messages
log_debug() {
    local message="$1"
    local component="${2:-MAIN}"
    local extra_data="${3:-}"
    _log $LOG_LEVEL_DEBUG "$message" "$component" "$extra_data"
}

# Log info messages
log_info() {
    local message="$1"
    local component="${2:-MAIN}"
    local extra_data="${3:-}"
    _log $LOG_LEVEL_INFO "$message" "$component" "$extra_data"
}

# Log warning messages
log_warn() {
    local message="$1"
    local component="${2:-MAIN}"
    local extra_data="${3:-}"
    _log $LOG_LEVEL_WARN "$message" "$component" "$extra_data"
}

# Log error messages
log_error() {
    local message="$1"
    local component="${2:-MAIN}"
    local extra_data="${3:-}"
    _log $LOG_LEVEL_ERROR "$message" "$component" "$extra_data"
}

# Log test results
log_test_result() {
    local test_name="$1"
    local result="$2" # "PASS" or "FAIL"
    local duration="${3:-0}"
    local details="${4:-}"

    local component="TEST"
    local message="Test '$test_name' $result"

    if [[ -n "$duration" ]]; then
        message="$message (${duration}s)"
    fi

    if [[ -n "$details" ]]; then
        message="$message - $details"
    fi

    local extra_data=""
    if [[ "$JSON_LOG" == "true" ]]; then
        extra_data=$(
            cat <<EOF
{
  "test_name": "$test_name",
  "result": "$result",
  "duration": $duration,
  "details": "$details"
}
EOF
        )
    fi

    if [[ "$result" == "PASS" ]]; then
        _log $LOG_LEVEL_INFO "$message" "$component" "$extra_data"
    else
        _log $LOG_LEVEL_ERROR "$message" "$component" "$extra_data"
    fi
}

# Log progress updates
log_progress() {
    local current="$1"
    local total="$2"
    local description="${3:-Processing}"

    local percentage=$(((current * 100) / total))
    local message="$description: $current/$total ($percentage%)"

    log_info "$message" "PROGRESS"
}

# Log section headers
log_section() {
    local section_name="$1"
    local border=$(printf '%*s' 60 | tr ' ' '=')

    log_info "$border"
    log_info "$section_name"
    log_info "$border"
}

# Rotate old log files
rotate_logs() {
    local max_age_days="${1:-7}"
    local max_files="${2:-50}"

    log_info "Starting log rotation (max age: ${max_age_days} days, max files: ${max_files})"

    # Remove old log directories
    find "$LOG_DIR" -mindepth 1 -maxdepth 1 -type d -name "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]" -mtime +$max_age_days -exec rm -rf {} \;

    # Remove excess log files in each directory
    find "$LOG_DIR" -name "*.log" -type f -printf '%T@ %p\n' | sort -n | head -n -$max_files | cut -d' ' -f2- | xargs -r rm -f

    log_info "Log rotation completed"
}

# Set log level from string
set_log_level() {
    local level_upper=$(echo "$1" | tr '[:lower:]' '[:upper:]')
    case "$level_upper" in
    "DEBUG") LOG_LEVEL=$LOG_LEVEL_DEBUG ;;
    "INFO") LOG_LEVEL=$LOG_LEVEL_INFO ;;
    "WARN" | "WARNING") LOG_LEVEL=$LOG_LEVEL_WARN ;;
    "ERROR") LOG_LEVEL=$LOG_LEVEL_ERROR ;;
    *) log_warn "Unknown log level: $1. Using INFO." ;;
    esac
}

# Enable/disable colored output
set_colors() {
    ENABLE_COLORS="$1"
}

# Enable/disable JSON logging
set_json_logging() {
    JSON_LOG="$1"
}

# Get log statistics
get_log_stats() {
    if [[ -z "$LOG_FILE" || ! -f "$LOG_FILE" ]]; then
        echo "No log file available"
        return 1
    fi

    local total_lines=$(wc -l <"$LOG_FILE")
    local debug_count=$(grep -c "\[DEBUG\]" "$LOG_FILE" 2>/dev/null || echo 0)
    local info_count=$(grep -c "\[INFO\]" "$LOG_FILE" 2>/dev/null || echo 0)
    local warn_count=$(grep -c "\[WARN\]" "$LOG_FILE" 2>/dev/null || echo 0)
    local error_count=$(grep -c "\[ERROR\]" "$LOG_FILE" 2>/dev/null || echo 0)

    echo "Log Statistics:"
    echo "  Total lines: $total_lines"
    echo "  DEBUG: $debug_count"
    echo "  INFO: $info_count"
    echo "  WARN: $warn_count"
    echo "  ERROR: $error_count"
    echo "  File: $LOG_FILE"
}

# Export functions for use in other scripts
export -f setup_logging get_timestamp log_debug log_info log_warn log_error
export -f log_test_result log_progress log_section rotate_logs set_log_level
export -f set_colors set_json_logging get_log_stats
