#!/bin/bash
# Validation utilities for Docker tests

set -euo pipefail

# Validate Dockerfile syntax and structure
validate_dockerfile() {
    local dockerfile="$1"
    local component="${2:-VALIDATE}"

    log_debug "Validating Dockerfile: $dockerfile" "$component"

    # Check if file exists and is readable
    if [ ! -f "$dockerfile" ]; then
        log_error "Dockerfile not found: $dockerfile" "$component"
        return 1
    fi

    if [ ! -r "$dockerfile" ]; then
        log_error "Dockerfile not readable: $dockerfile" "$component"
        return 1
    fi

    # Check if file is empty
    if [ ! -s "$dockerfile" ]; then
        log_error "Dockerfile is empty: $dockerfile" "$component"
        return 1
    fi

    # Check for required FROM instruction
    if ! grep -q "^FROM" "$dockerfile"; then
        log_error "Dockerfile missing FROM instruction: $dockerfile" "$component"
        return 1
    fi

    # Check for multiple FROM instructions (multi-stage build)
    local from_count=$(grep -c "^FROM" "$dockerfile")
    if [ "$from_count" -gt 1 ]; then
        log_debug "Multi-stage Dockerfile detected ($from_count stages)" "$component"
    fi

    # Validate instruction syntax
    local line_num=0
    local errors=0
    local warnings=0

    while IFS= read -r line; do
        ((line_num++))

        # Skip empty lines and comments
        if [[ "$line" =~ ^[[:space:]]*$ ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi

        # Check for valid instruction format
        if ! [[ "$line" =~ ^[A-Z]+[[:space:]] ]]; then
            log_warn "Line $line_num: Potentially invalid instruction format: $line" "$component"
            ((warnings++))
        fi

        # Check for common issues
        if [[ "$line" =~ ^RUN[[:space:]]+apt-get[[:space:]]+update ]] && ! [[ "$line" =~ &&.*apt-get.*install ]]; then
            log_warn "Line $line_num: Consider combining apt-get update with install" "$component"
            ((warnings++))
        fi

        # Check for COPY/ADD without specific ownership
        if [[ "$line" =~ ^(COPY|ADD)[[:space:]] ]] && ! [[ "$line" =~ --chown ]]; then
            log_debug "Line $line_num: Consider using --chown with COPY/ADD" "$component"
        fi

        # Check for EXPOSE instruction format
        if [[ "$line" =~ ^EXPOSE[[:space:]] ]]; then
            local port=$(echo "$line" | awk '{print $2}')
            if ! [[ "$port" =~ ^[0-9]+$ ]]; then
                log_warn "Line $line_num: Invalid port format in EXPOSE: $port" "$component"
                ((warnings++))
            fi
        fi

    done < "$dockerfile"

    # Check for security best practices
    if grep -q "^USER root" "$dockerfile"; then
        log_warn "Running as root user detected - consider using non-root user" "$component"
        ((warnings++))
    fi

    # Check for health check
    if ! grep -q "^HEALTHCHECK" "$dockerfile"; then
        log_debug "No HEALTHCHECK instruction found" "$component"
    fi

    # Summary
    if [ $errors -eq 0 ]; then
        log_info "Dockerfile validation passed ($warnings warnings)" "$component"
        return 0
    else
        log_error "Dockerfile validation failed ($errors errors, $warnings warnings)" "$component"
        return 1
    fi
}

# Validate configuration file (YAML)
validate_config() {
    local config_file="$1"
    local component="${2:-VALIDATE}"

    log_debug "Validating configuration file: $config_file" "$component"

    # Check if file exists and is readable
    if [ ! -f "$config_file" ]; then
        log_error "Configuration file not found: $config_file" "$component"
        return 1
    fi

    if [ ! -r "$config_file" ]; then
        log_error "Configuration file not readable: $config_file" "$component"
        return 1
    fi

    # Check if file is empty
    if [ ! -s "$config_file" ]; then
        log_error "Configuration file is empty: $config_file" "$component"
        return 1
    fi

    # Check YAML syntax using Python if available
    if command -v python3 &> /dev/null; then
        if ! python3 -c "import yaml; yaml.safe_load(open('$config_file'))" 2>/dev/null; then
            log_error "Invalid YAML syntax in configuration file: $config_file" "$component"
            return 1
        fi
    elif command -v python &> /dev/null; then
        if ! python -c "import yaml; yaml.safe_load(open('$config_file'))" 2>/dev/null; then
            log_error "Invalid YAML syntax in configuration file: $config_file" "$component"
            return 1
        fi
    else
        log_warn "Python not available - skipping YAML syntax validation" "$component"

        # Basic YAML structure check
        if ! head -1 "$config_file" | grep -q "^[a-zA-Z_]"; then
            log_error "Configuration file doesn't appear to be valid YAML" "$component"
            return 1
        fi
    fi

    # Check for required sections (spices-specific)
    if [[ "$config_file" =~ \.spices\.yml$ ]]; then
        if ! grep -q "^version:" "$config_file"; then
            log_error "Missing 'version' field in spices configuration" "$component"
            return 1
        fi

        if ! grep -q "^managers:" "$config_file"; then
            log_error "Missing 'managers' section in spices configuration" "$component"
            return 1
        fi
    fi

    log_info "Configuration validation passed: $config_file" "$component"
    return 0
}

# Validate test results JSON
validate_test_results() {
    local results_file="$1"
    local component="${2:-VALIDATE}"

    log_debug "Validating test results: $results_file" "$component"

    # Check if file exists and is readable
    if [ ! -f "$results_file" ]; then
        log_error "Test results file not found: $results_file" "$component"
        return 1
    fi

    if [ ! -r "$results_file" ]; then
        log_error "Test results file not readable: $results_file" "$component"
        return 1
    fi

    # Check if file is empty
    if [ ! -s "$results_file" ]; then
        log_error "Test results file is empty: $results_file" "$component"
        return 1
    fi

    # Validate JSON syntax
    if ! jq empty "$results_file" 2>/dev/null; then
        log_error "Invalid JSON in test results file: $results_file" "$component"
        return 1
    fi

    # Check for required fields
    local required_fields=("passed_count" "failed_count" "skipped_count" "total_count")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$results_file" >/dev/null 2>&1; then
            log_error "Missing required field '$field' in test results" "$component"
            return 1
        fi
    done

    # Validate count consistency
    local passed=$(jq -r '.passed_count' "$results_file")
    local failed=$(jq -r '.failed_count' "$results_file")
    local skipped=$(jq -r '.skipped_count' "$results_file")
    local total=$(jq -r '.total_count' "$results_file")

    local calculated_total=$((passed + failed + skipped))
    if [ "$calculated_total" -ne "$total" ]; then
        log_error "Test count mismatch: passed($passed) + failed($failed) + skipped($skipped) ≠ total($total)" "$component"
        return 1
    fi

    log_info "Test results validation passed: $results_file" "$component"
    return 0
}

# Check script dependencies
check_dependencies() {
    local component="${1:-VALIDATE}"

    log_info "Checking script dependencies..." "$component"

    local missing_deps=()
    local optional_deps=()

    # Required dependencies
    local required_tools=("docker" "jq" "find" "grep" "awk" "sed")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_deps+=("$tool")
        fi
    done

    # Optional dependencies
    local optional_tools=("python3" "python" "timeout" "mktemp")
    for tool in "${optional_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            optional_deps+=("$tool")
        fi
    done

    # Report missing required dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}" "$component"
        return 1
    fi

    # Report missing optional dependencies
    if [ ${#optional_deps[@]} -gt 0 ]; then
        log_warn "Missing optional dependencies: ${optional_deps[*]}" "$component"
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running" "$component"
        return 1
    fi

    # Check disk space
    local available_space=$(df /tmp | tail -1 | awk '{print $4}')
    local min_space_kb=1048576  # 1GB in KB

    if [ "$available_space" -lt "$min_space_kb" ]; then
        log_warn "Low disk space available: ${available_space}KB (minimum recommended: ${min_space_kb}KB)" "$component"
    fi

    log_info "Dependency check completed" "$component"
    return 0
}

# Verify required permissions
verify_permissions() {
    local component="${1:-VALIDATE}"

    log_info "Verifying permissions..." "$component"

    # Check Docker permissions
    if ! docker ps &> /dev/null; then
        log_error "Cannot execute Docker commands - check user permissions" "$component"
        return 1
    fi

    # Check write permissions for logs directory
    local logs_dir="${LOG_DIR:-$(pwd)/scripts/logs/docker-tests}"
    if [ ! -d "$logs_dir" ]; then
        if ! mkdir -p "$logs_dir" 2>/dev/null; then
            log_error "Cannot create logs directory: $logs_dir" "$component"
            return 1
        fi
    fi

    if [ ! -w "$logs_dir" ]; then
        log_error "No write permission for logs directory: $logs_dir" "$component"
        return 1
    fi

    # Check write permissions for temp directory
    local temp_dir="${TMPDIR:-/tmp}"
    if [ ! -w "$temp_dir" ]; then
        log_error "No write permission for temp directory: $temp_dir" "$component"
        return 1
    fi

    # Check script execution permissions
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local scripts_to_check=("../local-docker-test.sh" "../discover-images.sh")

    for script in "${scripts_to_check[@]}"; do
        local script_path="$script_dir/$script"
        if [ -f "$script_path" ] && [ ! -x "$script_path" ]; then
            log_warn "Script not executable: $script_path" "$component"
        fi
    done

    log_info "Permission verification completed" "$component"
    return 0
}

# Validate test matrix JSON structure
validate_test_matrix() {
    local matrix_file="$1"
    local component="${2:-VALIDATE}"

    log_debug "Validating test matrix: $matrix_file" "$component"

    # Check if file exists and is readable
    if [ ! -f "$matrix_file" ]; then
        log_error "Test matrix file not found: $matrix_file" "$component"
        return 1
    fi

    # Validate JSON syntax
    if ! jq empty "$matrix_file" 2>/dev/null; then
        log_error "Invalid JSON in test matrix file: $matrix_file" "$component"
        return 1
    fi

    # Check for required top-level fields
    local required_fields=("images" "total_count" "filtered_count")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$matrix_file" >/dev/null 2>&1; then
            log_error "Missing required field '$field' in test matrix" "$component"
            return 1
        fi
    done

    # Validate image objects
    local image_count=$(jq -r '.images | length' "$matrix_file")
    local total_count=$(jq -r '.total_count' "$matrix_file")

    if [ "$image_count" -ne "$total_count" ]; then
        log_error "Image count mismatch: images array has $image_count items, total_count is $total_count" "$component"
        return 1
    fi

    # Validate each image object
    local image_required_fields=("distro" "version" "dockerfile" "image_name")
    for ((i=0; i<image_count; i++)); do
        for field in "${image_required_fields[@]}"; do
            if ! jq -e ".images[$i].$field" "$matrix_file" >/dev/null 2>&1; then
                log_error "Missing required field '$field' in image object $i" "$component"
                return 1
            fi
        done

        # Check if dockerfile exists
        local dockerfile=$(jq -r ".images[$i].dockerfile" "$matrix_file")
        if [ ! -f "$dockerfile" ]; then
            log_error "Dockerfile not found for image $i: $dockerfile" "$component"
            return 1
        fi
    done

    log_info "Test matrix validation passed: $matrix_file" "$component"
    return 0
}

# Validate environment variables
validate_environment() {
    local component="${1:-VALIDATE}"

    log_debug "Validating environment..." "$component"

    # Check PATH
    if [ -z "${PATH:-}" ]; then
        log_error "PATH environment variable not set" "$component"
        return 1
    fi

    # Check HOME
    if [ -z "${HOME:-}" ]; then
        log_warn "HOME environment variable not set" "$component"
    fi

    # Check SHELL
    if [ -z "${SHELL:-}" ]; then
        log_warn "SHELL environment variable not set" "$component"
    fi

    # Check platform compatibility
    local platform=$(uname -s)
    case "$platform" in
        Linux|Darwin)
            log_debug "Platform: $platform (supported)" "$component"
            ;;
        *)
            log_warn "Platform: $platform (not explicitly supported)" "$component"
            ;;
    esac

    log_info "Environment validation completed" "$component"
    return 0
}

# Comprehensive validation check
validate_all() {
    local component="${1:-VALIDATE}"

    log_section "Running Comprehensive Validation"

    local validation_errors=0

    # Check dependencies
    if ! check_dependencies "$component"; then
        ((validation_errors++))
    fi

    # Verify permissions
    if ! verify_permissions "$component"; then
        ((validation_errors++))
    fi

    # Validate environment
    if ! validate_environment "$component"; then
        ((validation_errors++))
    fi

    # Summary
    if [ $validation_errors -eq 0 ]; then
        log_info "All validation checks passed" "$component"
        return 0
    else
        log_error "Validation failed with $validation_errors errors" "$component"
        return 1
    fi
}

# Export functions for use in other scripts
export -f validate_dockerfile validate_config validate_test_results
export -f check_dependencies verify_permissions validate_test_matrix
export -f validate_environment validate_all
