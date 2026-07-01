#!/bin/bash
# Main orchestrator for local Docker testing
# Replicates GitHub Actions docker-tests.yml workflow for local development

set -euo pipefail

# Script directory and paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
UTILS_DIR="$SCRIPT_DIR/utils"
CONFIG_DIR="$SCRIPT_DIR/config"

# Source logging utilities
source "$UTILS_DIR/logging.sh"

# Default configuration
DEFAULT_CONFIG_FILE="$CONFIG_DIR/test-config.yml"
DEFAULT_PARALLEL_JOBS=4
DEFAULT_TIMEOUT=300
DEFAULT_CLEANUP=true
DEFAULT_VERBOSE=false
DEFAULT_QUIET=false

# Global variables
DISTRO=""
VERSION=""
PARALLEL_JOBS=$DEFAULT_PARALLEL_JOBS
REBUILD=false
CLEANUP_ONLY=false
NO_CLEANUP=false
VERBOSE=$DEFAULT_VERBOSE
QUIET=$DEFAULT_QUIET
GENERATE_REPORT=false
CONFIG_FILE=""
HELP=false

# Test statistics
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Show usage information
show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Local Docker Testing for Spices - Replicates GitHub Actions workflow

OPTIONS:
    --distro DISTRO         Test specific distribution (e.g., debian, ubuntu, centos)
    --version VERSION       Test specific version (e.g., 11, 20.04, 7)
    --parallel N            Number of parallel tests (default: $DEFAULT_PARALLEL_JOBS)
    --rebuild               Force rebuild Docker images
    --cleanup-only          Only perform cleanup operations
    --no-cleanup            Skip cleanup after tests
    --verbose               Enable verbose output
    --quiet                 Suppress non-essential output
    --report                Generate detailed HTML report
    --config FILE           Use custom configuration file
    --help                  Show this help message

EXAMPLES:
    $0                                      # Test all distributions
    $0 --distro debian                      # Test only Debian
    $0 --distro ubuntu --version 20.04      # Test Ubuntu 20.04 specifically
    $0 --parallel 8                         # Run 8 tests in parallel
    $0 --rebuild --verbose                  # Rebuild images with verbose output
    $0 --cleanup-only                       # Only cleanup old images/containers
    $0 --report --quiet                     # Generate report with minimal output

ENVIRONMENT VARIABLES:
    LOG_LEVEL               Set log level (DEBUG, INFO, WARN, ERROR)
    JSON_LOG                Enable JSON logging (true/false)
    ENABLE_COLORS           Enable colored output (true/false)

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
        --distro)
            DISTRO="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL_JOBS="$2"
            if ! [[ "$PARALLEL_JOBS" =~ ^[0-9]+$ ]] || [ "$PARALLEL_JOBS" -lt 1 ]; then
                log_error "Invalid parallel jobs count: $PARALLEL_JOBS"
                exit 1
            fi
            shift 2
            ;;
        --rebuild)
            REBUILD=true
            shift
            ;;
        --cleanup-only)
            CLEANUP_ONLY=true
            shift
            ;;
        --no-cleanup)
            NO_CLEANUP=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            set_log_level "DEBUG"
            shift
            ;;
        --quiet)
            QUIET=true
            set_log_level "ERROR"
            shift
            ;;
        --report)
            GENERATE_REPORT=true
            shift
            ;;
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --help)
            HELP=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        esac
    done
}

# Validate configuration
validate_configuration() {
    log_info "Validating configuration..." "CONFIG"

    # Check if Docker is available
    if ! command -v docker &>/dev/null; then
        log_error "Docker is not installed or not in PATH" "CONFIG"
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker info &>/dev/null; then
        log_error "Docker daemon is not running" "CONFIG"
        exit 1
    fi

    # Check if tests directory exists
    if [ ! -d "$ROOT_DIR/tests/docker" ]; then
        log_error "Tests directory not found: $ROOT_DIR/tests/docker" "CONFIG"
        exit 1
    fi

    # Validate config file if specified
    if [ -n "$CONFIG_FILE" ]; then
        if [ ! -f "$CONFIG_FILE" ]; then
            log_error "Config file not found: $CONFIG_FILE" "CONFIG"
            exit 1
        fi
    fi

    # Validate distro/version combination
    if [ -n "$VERSION" ] && [ -z "$DISTRO" ]; then
        log_error "Version specified without distro. Use --distro to specify distribution." "CONFIG"
        exit 1
    fi

    log_info "Configuration validation passed" "CONFIG"
}

# Initialize environment
initialize_environment() {
    log_section "Initializing Docker Test Environment"

    # Set up logging
    setup_logging "docker-tests"

    # Configure quiet/verbose modes
    if [ "$QUIET" = true ]; then
        set_log_level "ERROR"
    elif [ "$VERBOSE" = true ]; then
        set_log_level "DEBUG"
    fi

    # Log configuration
    log_info "Root directory: $ROOT_DIR" "INIT"
    log_info "Script directory: $SCRIPT_DIR" "INIT"
    log_info "Parallel jobs: $PARALLEL_JOBS" "INIT"
    log_info "Distro filter: ${DISTRO:-all}" "INIT"
    log_info "Version filter: ${VERSION:-all}" "INIT"
    log_info "Rebuild images: $REBUILD" "INIT"
    log_info "Generate report: $GENERATE_REPORT" "INIT"

    # Create temporary directory for test artifacts
    TEST_TEMP_DIR=$(mktemp -d)
    export TEST_TEMP_DIR
    log_debug "Created temporary directory: $TEST_TEMP_DIR" "INIT"

    # Set up signal handlers
    trap cleanup_on_exit EXIT
    trap 'log_error "Interrupted by user"; exit 130' INT
    trap 'log_error "Terminated"; exit 143' TERM
}

# Cleanup function
cleanup_on_exit() {
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log_info "Test execution completed successfully" "CLEANUP"
    else
        log_error "Test execution failed with exit code $exit_code" "CLEANUP"
    fi

    # Clean up temporary directory
    if [ -n "${TEST_TEMP_DIR:-}" ] && [ -d "$TEST_TEMP_DIR" ]; then
        log_debug "Cleaning up temporary directory: $TEST_TEMP_DIR" "CLEANUP"
        rm -rf "$TEST_TEMP_DIR"
    fi

    # Perform cleanup if enabled
    if [ "$NO_CLEANUP" = false ]; then
        log_info "Performing cleanup..." "CLEANUP"
        "$SCRIPT_DIR/cleanup.sh" --quiet
    fi

    # Show final statistics
    show_final_statistics
}

# Show final statistics
show_final_statistics() {
    log_section "Test Results Summary"

    log_info "Total tests: $TOTAL_TESTS" "STATS"
    log_info "Passed: $PASSED_TESTS" "STATS"
    log_info "Failed: $FAILED_TESTS" "STATS"
    log_info "Skipped: $SKIPPED_TESTS" "STATS"

    if [ $TOTAL_TESTS -gt 0 ]; then
        local success_rate=$(((PASSED_TESTS * 100) / TOTAL_TESTS))
        log_info "Success rate: ${success_rate}%" "STATS"
    fi

    # Show log statistics
    get_log_stats
}

# Discover test images
discover_images() {
    log_section "Discovering Docker Test Images"

    local discover_cmd="$SCRIPT_DIR/discover-images.sh"

    # Add filters
    if [ -n "$DISTRO" ]; then
        discover_cmd="$discover_cmd --distro $DISTRO"
    fi

    if [ -n "$VERSION" ]; then
        discover_cmd="$discover_cmd --version $VERSION"
    fi

    log_info "Running image discovery: $discover_cmd" "DISCOVER"

    if ! $discover_cmd >"$TEST_TEMP_DIR/test-matrix.json"; then
        log_error "Image discovery failed" "DISCOVER"
        return 1
    fi

    # Parse results
    TOTAL_TESTS=$(jq -r '.total_count' "$TEST_TEMP_DIR/test-matrix.json")
    log_info "Discovered $TOTAL_TESTS test configurations" "DISCOVER"

    if [ "$TOTAL_TESTS" -eq 0 ]; then
        log_warn "No test configurations found matching criteria" "DISCOVER"
        return 1
    fi

    return 0
}

# Build test images
build_images() {
    log_section "Building Docker Test Images"

    local build_cmd="$SCRIPT_DIR/build-image.sh"

    # Add options
    if [ "$REBUILD" = true ]; then
        build_cmd="$build_cmd --rebuild"
    fi

    if [ "$VERBOSE" = true ]; then
        build_cmd="$build_cmd --verbose"
    fi

    build_cmd="$build_cmd --parallel $PARALLEL_JOBS"
    build_cmd="$build_cmd --matrix $TEST_TEMP_DIR/test-matrix.json"

    log_info "Running image build: $build_cmd" "BUILD"

    if ! $build_cmd; then
        log_error "Image building failed" "BUILD"
        return 1
    fi

    log_info "Image building completed successfully" "BUILD"
    return 0
}

# Run tests
run_tests() {
    log_section "Running Docker Tests"

    local test_cmd="$SCRIPT_DIR/test-image.sh"

    # Add options
    if [ "$VERBOSE" = true ]; then
        test_cmd="$test_cmd --verbose"
    fi

    test_cmd="$test_cmd --parallel $PARALLEL_JOBS"
    test_cmd="$test_cmd --matrix $TEST_TEMP_DIR/test-matrix.json"
    test_cmd="$test_cmd --results $TEST_TEMP_DIR/test-results.json"

    log_info "Running tests: $test_cmd" "TEST"

    if ! $test_cmd; then
        log_error "Test execution failed" "TEST"
        return 1
    fi

    # Parse test results
    if [ -f "$TEST_TEMP_DIR/test-results.json" ]; then
        PASSED_TESTS=$(jq -r '.passed_count' "$TEST_TEMP_DIR/test-results.json")
        FAILED_TESTS=$(jq -r '.failed_count' "$TEST_TEMP_DIR/test-results.json")
        SKIPPED_TESTS=$(jq -r '.skipped_count' "$TEST_TEMP_DIR/test-results.json")
    fi

    log_info "Test execution completed" "TEST"
    return 0
}

# Generate report
generate_report() {
    if [ "$GENERATE_REPORT" = false ]; then
        return 0
    fi

    log_section "Generating Test Report"

    local report_cmd="$SCRIPT_DIR/reports/generate-report.sh"
    report_cmd="$report_cmd --results $TEST_TEMP_DIR/test-results.json"
    report_cmd="$report_cmd --matrix $TEST_TEMP_DIR/test-matrix.json"

    log_info "Generating report: $report_cmd" "REPORT"

    if ! $report_cmd; then
        log_error "Report generation failed" "REPORT"
        return 1
    fi

    log_info "Report generation completed" "REPORT"
    return 0
}

# Main execution function
main() {
    # Parse arguments
    parse_arguments "$@"

    # Show help if requested
    if [ "$HELP" = true ]; then
        show_usage
        exit 0
    fi

    # Initialize environment
    initialize_environment

    # Validate configuration
    validate_configuration

    # Handle cleanup-only mode
    if [ "$CLEANUP_ONLY" = true ]; then
        log_info "Running cleanup only..." "MAIN"
        "$SCRIPT_DIR/cleanup.sh"
        exit 0
    fi

    # Execute main workflow
    log_section "Starting Docker Test Workflow"

    local workflow_success=true

    # Step 1: Discover test images
    if ! discover_images; then
        workflow_success=false
    fi

    # Step 2: Build test images
    if [ "$workflow_success" = true ]; then
        if ! build_images; then
            workflow_success=false
        fi
    fi

    # Step 3: Run tests
    if [ "$workflow_success" = true ]; then
        if ! run_tests; then
            workflow_success=false
        fi
    fi

    # Step 4: Generate report
    if [ "$workflow_success" = true ]; then
        if ! generate_report; then
            workflow_success=false
        fi
    fi

    # Exit with appropriate code
    if [ "$workflow_success" = true ]; then
        log_info "Docker test workflow completed successfully" "MAIN"
        exit 0
    else
        log_error "Docker test workflow failed" "MAIN"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
