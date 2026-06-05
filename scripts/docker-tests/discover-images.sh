#!/bin/bash
# Discover and catalog Docker test images
# Scans tests/docker/ directory and generates test matrix for parallel execution

set -euo pipefail

# Script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
UTILS_DIR="$SCRIPT_DIR/utils"

# Source logging utilities
source "$UTILS_DIR/logging.sh"

# Default configuration
TESTS_DIR="$ROOT_DIR/tests/docker"
OUTPUT_FORMAT="json"
DISTRO_FILTER=""
VERSION_FILTER=""
VALIDATE_DOCKERFILES=true
VERBOSE=false

# Global variables
declare -a DISCOVERED_IMAGES=()

# Get distro priority (function-based approach for bash 3.2 compatibility)
get_distro_priority() {
    local distro="$1"

    case "$distro" in
    "debian" | "ubuntu" | "centos")
        echo "high"
        ;;
    "fedora" | "alpine" | "amazonlinux" | "oracle" | "redhat")
        echo "medium"
        ;;
    "archlinux" | "busybox" | "cirros" | "coreos" | "gentoo" | "opensuse" | "raspbian")
        echo "low"
        ;;
    *)
        echo "low"
        ;;
    esac
}

# Show usage information
show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Discover Docker test images and generate test matrix

OPTIONS:
    --distro DISTRO         Filter by distribution (e.g., debian, ubuntu, centos)
    --version VERSION       Filter by version (e.g., 11, 20.04, 7)
    --format FORMAT         Output format: json, table (default: json)
    --no-validate          Skip Dockerfile validation
    --verbose              Enable verbose output
    --help                 Show this help message

EXAMPLES:
    $0                                  # Discover all images
    $0 --distro debian                  # Only Debian images
    $0 --distro ubuntu --version 20.04  # Ubuntu 20.04 specifically
    $0 --format table                   # Output as table
    $0 --no-validate                    # Skip validation

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
        --distro)
            DISTRO_FILTER="$2"
            shift 2
            ;;
        --version)
            VERSION_FILTER="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            if [[ "$OUTPUT_FORMAT" != "json" && "$OUTPUT_FORMAT" != "table" ]]; then
                echo "ERROR: Invalid output format: $OUTPUT_FORMAT" >&2
                exit 1
            fi
            shift 2
            ;;
        --no-validate)
            VALIDATE_DOCKERFILES=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option: $1" >&2
            show_usage
            exit 1
            ;;
        esac
    done
}

# Discover all Dockerfiles in tests directory
discover_dockerfiles() {
    log_info "Discovering Dockerfiles in $TESTS_DIR" "DISCOVER"

    if [ ! -d "$TESTS_DIR" ]; then
        log_error "Tests directory not found: $TESTS_DIR" "DISCOVER"
        return 1
    fi

    local dockerfile_count=0
    while IFS= read -r -d '' dockerfile; do
        log_debug "Found Dockerfile: $dockerfile" "DISCOVER"

        if [ "$VALIDATE_DOCKERFILES" = true ]; then
            if ! validate_dockerfile "$dockerfile"; then
                log_warn "Skipping invalid Dockerfile: $dockerfile" "DISCOVER"
                continue
            fi
        fi

        local image_info
        if image_info=$(parse_image_info "$dockerfile"); then
            DISCOVERED_IMAGES+=("$image_info")
            ((dockerfile_count++))
        else
            log_warn "Failed to parse image info for: $dockerfile" "DISCOVER"
        fi
    done < <(find "$TESTS_DIR" -name "Dockerfile" -type f -print0)

    log_info "Discovered $dockerfile_count valid Dockerfiles" "DISCOVER"
    return 0
}

# Parse image information from Dockerfile path
parse_image_info() {
    local dockerfile="$1"
    local relative_path="${dockerfile#$TESTS_DIR/}"

    # Extract distro and version from path
    # Expected format: distro/version/Dockerfile
    local path_parts
    IFS='/' read -ra path_parts <<<"$relative_path"

    if [ ${#path_parts[@]} -lt 2 ]; then
        log_error "Invalid Dockerfile path structure: $relative_path" "PARSE"
        return 1
    fi

    local distro="${path_parts[0]}"
    local version="${path_parts[1]}"

    # Skip if filters don't match
    if [ -n "$DISTRO_FILTER" ] && [ "$distro" != "$DISTRO_FILTER" ]; then
        log_debug "Skipping $distro (doesn't match filter: $DISTRO_FILTER)" "PARSE"
        return 1
    fi

    if [ -n "$VERSION_FILTER" ] && [ "$version" != "$VERSION_FILTER" ]; then
        log_debug "Skipping $distro:$version (doesn't match filter: $VERSION_FILTER)" "PARSE"
        return 1
    fi

    # Generate image name
    local image_name="spices-test-${distro}-${version}"

    # Get test priority
    local priority=$(get_distro_priority "$distro")

    # Calculate timeout based on priority
    local timeout
    case "$priority" in
    "high") timeout=300 ;;
    "medium") timeout=450 ;;
    "low") timeout=600 ;;
    *) timeout=300 ;;
    esac

    # Extract additional metadata from Dockerfile
    local base_image=""
    local build_args=""
    if [ -f "$dockerfile" ]; then
        base_image=$(grep -m1 "^FROM" "$dockerfile" | cut -d' ' -f2 || echo "")
        # Extract ARG instructions for build arguments
        while IFS= read -r arg_line; do
            if [ -n "$build_args" ]; then
                build_args="${build_args},"
            fi
            local arg_name=$(echo "$arg_line" | cut -d' ' -f2 | cut -d'=' -f1)
            local arg_value=$(echo "$arg_line" | cut -d'=' -f2 || echo "")
            build_args="${build_args}\"${arg_name}\":\"${arg_value}\""
        done < <(grep "^ARG" "$dockerfile" || true)
    fi

    # Create JSON object
    local json_object=$(
        cat <<EOF
{
    "distro": "$distro",
    "version": "$version",
    "dockerfile": "$dockerfile",
    "image_name": "$image_name",
    "test_priority": "$priority",
    "build_args": {$build_args},
    "test_timeout": $timeout,
    "base_image": "$base_image",
    "relative_path": "$relative_path"
}
EOF
    )

    echo "$json_object"
    return 0
}

# Validate Dockerfile syntax
validate_dockerfile() {
    local dockerfile="$1"

    log_debug "Validating Dockerfile: $dockerfile" "VALIDATE"

    # Check if file exists and is readable
    if [ ! -f "$dockerfile" ] || [ ! -r "$dockerfile" ]; then
        log_error "Dockerfile not found or not readable: $dockerfile" "VALIDATE"
        return 1
    fi

    # Check if file is empty
    if [ ! -s "$dockerfile" ]; then
        log_error "Dockerfile is empty: $dockerfile" "VALIDATE"
        return 1
    fi

    # Check for required FROM instruction
    if ! grep -q "^FROM" "$dockerfile"; then
        log_error "Dockerfile missing FROM instruction: $dockerfile" "VALIDATE"
        return 1
    fi

    # Check for basic syntax issues
    local line_num=0
    while IFS= read -r line; do
        ((line_num++))

        # Skip empty lines and comments
        if [[ "$line" =~ ^[[:space:]]*$ ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi

        # Check for valid instruction format
        if ! [[ "$line" =~ ^[A-Z]+[[:space:]] ]]; then
            log_warn "Potentially invalid instruction at line $line_num: $line" "VALIDATE"
        fi
    done <"$dockerfile"

    log_debug "Dockerfile validation passed: $dockerfile" "VALIDATE"
    return 0
}

# Filter images based on criteria
filter_images() {
    local filter_criteria="$1"

    log_debug "Applying filter: $filter_criteria" "FILTER"

    # This function can be extended to support more complex filtering
    # For now, basic filtering is handled in parse_image_info

    return 0
}

# Generate test matrix JSON
generate_test_matrix() {
    local total_count=${#DISCOVERED_IMAGES[@]}
    local filtered_count=$total_count

    log_info "Generating test matrix with $total_count images" "MATRIX"

    # Create JSON array of images
    local images_json=""
    for ((i = 0; i < ${#DISCOVERED_IMAGES[@]}; i++)); do
        if [ $i -gt 0 ]; then
            images_json="${images_json},"
        fi
        images_json="${images_json}${DISCOVERED_IMAGES[$i]}"
    done

    # Generate complete test matrix
    local test_matrix=$(
        cat <<EOF
{
    "images": [$images_json],
    "total_count": $total_count,
    "filtered_count": $filtered_count,
    "generation_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "filters": {
        "distro": "${DISTRO_FILTER:-all}",
        "version": "${VERSION_FILTER:-all}"
    },
    "metadata": {
        "tests_directory": "$TESTS_DIR",
        "script_version": "1.0.0",
        "validation_enabled": $VALIDATE_DOCKERFILES
    }
}
EOF
    )

    echo "$test_matrix"
    return 0
}

# Generate table output
generate_table_output() {
    local total_count=${#DISCOVERED_IMAGES[@]}

    echo "Docker Test Images Discovery Results"
    echo "===================================="
    echo
    printf "%-15s %-10s %-12s %-30s %-8s\n" "DISTRO" "VERSION" "PRIORITY" "IMAGE_NAME" "TIMEOUT"
    printf "%-15s %-10s %-12s %-30s %-8s\n" "------" "-------" "--------" "----------" "-------"

    for image_json in "${DISCOVERED_IMAGES[@]}"; do
        local distro=$(echo "$image_json" | jq -r '.distro')
        local version=$(echo "$image_json" | jq -r '.version')
        local priority=$(echo "$image_json" | jq -r '.test_priority')
        local image_name=$(echo "$image_json" | jq -r '.image_name')
        local timeout=$(echo "$image_json" | jq -r '.test_timeout')

        printf "%-15s %-10s %-12s %-30s %-8s\n" "$distro" "$version" "$priority" "$image_name" "${timeout}s"
    done

    echo
    echo "Summary:"
    echo "  Total images: $total_count"
    echo "  Filters applied: distro=${DISTRO_FILTER:-all}, version=${VERSION_FILTER:-all}"
    echo "  Validation: $VALIDATE_DOCKERFILES"
}

# Main execution function
main() {
    # Parse arguments
    parse_arguments "$@"

    # Initialize logging
    if [ "$VERBOSE" = true ]; then
        set_log_level "DEBUG"
    else
        set_log_level "INFO"
    fi

    # Discover Dockerfiles
    if ! discover_dockerfiles; then
        log_error "Failed to discover Dockerfiles" "MAIN"
        exit 1
    fi

    # Check if any images were found
    if [ ${#DISCOVERED_IMAGES[@]} -eq 0 ]; then
        log_warn "No Docker images found matching criteria" "MAIN"

        # Output empty result based on format
        if [ "$OUTPUT_FORMAT" = "json" ]; then
            echo '{"images": [], "total_count": 0, "filtered_count": 0}'
        else
            echo "No images found."
        fi
        exit 0
    fi

    # Generate output based on format
    if [ "$OUTPUT_FORMAT" = "json" ]; then
        generate_test_matrix
    else
        generate_table_output
    fi

    log_info "Image discovery completed successfully" "MAIN"
    exit 0
}

# Run main function with all arguments
main "$@"
