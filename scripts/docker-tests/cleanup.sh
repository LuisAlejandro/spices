#!/bin/bash
# Cleanup utilities for Docker test artifacts

set -euo pipefail

# Script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILS_DIR="$SCRIPT_DIR/utils"

# Source utilities
source "$UTILS_DIR/logging.sh"
source "$UTILS_DIR/docker-utils.sh"

# Default configuration
QUIET=false
FORCE=false
CONTAINERS_ONLY=false
IMAGES_ONLY=false

# Show usage information
show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Cleanup Docker test artifacts

OPTIONS:
    --quiet             Suppress non-essential output
    --force             Force cleanup without confirmation
    --containers-only   Only cleanup containers
    --images-only       Only cleanup images
    --help              Show this help message

EXAMPLES:
    $0                  # Interactive cleanup
    $0 --quiet --force  # Silent cleanup
    $0 --containers-only # Only remove containers

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
        --quiet)
            QUIET=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --containers-only)
            CONTAINERS_ONLY=true
            shift
            ;;
        --images-only)
            IMAGES_ONLY=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        esac
    done
}

# Main cleanup function
main() {
    # Parse arguments
    parse_arguments "$@"

    # Configure logging
    if [ "$QUIET" = true ]; then
        set_log_level "ERROR"
    else
        set_log_level "INFO"
    fi

    # Initialize logging
    setup_logging "cleanup"

    log_info "Starting Docker test cleanup..." "CLEANUP"

    # Check if Docker is available
    if ! check_docker_available "CLEANUP"; then
        log_error "Docker not available for cleanup"
        exit 1
    fi

    # Perform cleanup based on options
    if [ "$CONTAINERS_ONLY" = true ]; then
        cleanup_containers "spices-test-*" "CLEANUP"
    elif [ "$IMAGES_ONLY" = true ]; then
        cleanup_images "spices-test-*" "CLEANUP"
    else
        cleanup_all "CLEANUP"
    fi

    log_info "Cleanup completed successfully" "CLEANUP"
}

# Run main function with all arguments
main "$@"
