#!/bin/bash
# Docker helper functions for test infrastructure

set -euo pipefail

# Check if Docker is available and daemon is running
check_docker_available() {
    local component="${1:-DOCKER}"

    log_debug "Checking Docker availability..." "$component"

    # Check if Docker command exists
    if ! command -v docker &>/dev/null; then
        log_error "Docker is not installed or not in PATH" "$component"
        return 1
    fi

    # Check if Docker daemon is running
    if ! docker info &>/dev/null; then
        log_error "Docker daemon is not running" "$component"
        return 1
    fi

    # Check Docker version
    local docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    log_info "Docker version: $docker_version" "$component"

    # Check if we can run basic Docker commands
    if ! docker ps &>/dev/null; then
        log_error "Cannot execute Docker commands (permission denied?)" "$component"
        return 1
    fi

    log_info "Docker is available and functioning" "$component"
    return 0
}

# Get Docker system information
get_docker_info() {
    local component="${1:-DOCKER}"

    log_debug "Gathering Docker system information..." "$component"

    # Get Docker system info
    local info_output=$(docker system info 2>/dev/null)

    # Extract key information
    local containers_running=$(echo "$info_output" | grep "Containers:" | head -1 | awk '{print $2}')
    local images_count=$(echo "$info_output" | grep "Images:" | awk '{print $2}')
    local storage_driver=$(echo "$info_output" | grep "Storage Driver:" | awk '{print $3}')

    log_info "Docker system info: $containers_running containers, $images_count images, storage: $storage_driver" "$component"

    # Return JSON format
    cat <<EOF
{
    "containers_running": "${containers_running:-0}",
    "images_count": "${images_count:-0}",
    "storage_driver": "${storage_driver:-unknown}"
}
EOF
}

# Build Docker image
build_docker_image() {
    local dockerfile="$1"
    local image_name="$2"
    local build_args="${3:-}"
    local component="${4:-BUILD}"

    log_info "Building Docker image: $image_name" "$component"
    log_debug "Dockerfile: $dockerfile" "$component"

    # Validate inputs
    if [ ! -f "$dockerfile" ]; then
        log_error "Dockerfile not found: $dockerfile" "$component"
        return 1
    fi

    # Get dockerfile directory
    local dockerfile_dir=$(dirname "$dockerfile")

    # Build Docker command
    local docker_cmd="docker build"
    docker_cmd="$docker_cmd -t $image_name"
    docker_cmd="$docker_cmd -f $dockerfile"

    # Add build arguments if provided
    if [ -n "$build_args" ]; then
        local arg_pairs
        IFS=',' read -ra arg_pairs <<<"$build_args"
        for arg_pair in "${arg_pairs[@]}"; do
            docker_cmd="$docker_cmd --build-arg $arg_pair"
        done
    fi

    docker_cmd="$docker_cmd $dockerfile_dir"

    log_debug "Docker build command: $docker_cmd" "$component"

    # Execute build with timeout
    local build_start_time=$(date +%s)

    if timeout 1800 $docker_cmd; then
        local build_end_time=$(date +%s)
        local build_duration=$((build_end_time - build_start_time))
        log_info "Image build completed in ${build_duration}s: $image_name" "$component"
        return 0
    else
        local exit_code=$?
        log_error "Image build failed with exit code $exit_code: $image_name" "$component"
        return $exit_code
    fi
}

# Check if Docker image exists
image_exists() {
    local image_name="$1"
    local component="${2:-DOCKER}"

    log_debug "Checking if image exists: $image_name" "$component"

    if docker image inspect "$image_name" &>/dev/null; then
        log_debug "Image exists: $image_name" "$component"
        return 0
    else
        log_debug "Image does not exist: $image_name" "$component"
        return 1
    fi
}

# Get image information
get_image_info() {
    local image_name="$1"
    local component="${2:-DOCKER}"

    log_debug "Getting image information: $image_name" "$component"

    if ! image_exists "$image_name" "$component"; then
        log_error "Image not found: $image_name" "$component"
        return 1
    fi

    # Get image details
    local image_info=$(docker image inspect "$image_name" 2>/dev/null)

    # Extract key information
    local image_id=$(echo "$image_info" | jq -r '.[0].Id' 2>/dev/null || echo "unknown")
    local created=$(echo "$image_info" | jq -r '.[0].Created' 2>/dev/null || echo "unknown")
    local size=$(echo "$image_info" | jq -r '.[0].Size' 2>/dev/null || echo "0")

    # Convert size to human readable format
    local size_mb=$((size / 1024 / 1024))

    log_debug "Image info: $image_name (ID: ${image_id:0:12}, Size: ${size_mb}MB)" "$component"

    # Return JSON format
    cat <<EOF
{
    "image_name": "$image_name",
    "image_id": "$image_id",
    "created": "$created",
    "size_bytes": $size,
    "size_mb": $size_mb
}
EOF
}

# Run container with test configuration
run_container() {
    local image_name="$1"
    local container_name="$2"
    local command="${3:-/bin/sh}"
    local timeout="${4:-300}"
    local component="${5:-CONTAINER}"

    log_info "Running container: $container_name from $image_name" "$component"

    # Check if image exists
    if ! image_exists "$image_name" "$component"; then
        log_error "Image not found: $image_name" "$component"
        return 1
    fi

    # Clean up existing container if it exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        log_debug "Removing existing container: $container_name" "$component"
        docker rm -f "$container_name" &>/dev/null || true
    fi

    # Run container
    local container_id
    container_id=$(docker run -d --name "$container_name" "$image_name" "$command")

    if [ $? -eq 0 ]; then
        log_info "Container started: $container_name (ID: ${container_id:0:12})" "$component"
        echo "$container_id"
        return 0
    else
        log_error "Failed to start container: $container_name" "$component"
        return 1
    fi
}

# Execute command in container
exec_in_container() {
    local container_name="$1"
    local command="$2"
    local timeout="${3:-60}"
    local component="${4:-EXEC}"

    log_debug "Executing command in container $container_name: $command" "$component"

    # Check if container exists and is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        log_error "Container not found or not running: $container_name" "$component"
        return 1
    fi

    # Execute command with timeout
    if timeout "$timeout" docker exec "$container_name" sh -c "$command"; then
        log_debug "Command executed successfully in container: $container_name" "$component"
        return 0
    else
        local exit_code=$?
        log_error "Command failed in container $container_name (exit code: $exit_code)" "$component"
        return $exit_code
    fi
}

# Monitor container execution
monitor_container() {
    local container_name="$1"
    local timeout="${2:-300}"
    local component="${3:-MONITOR}"

    log_info "Monitoring container: $container_name" "$component"

    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))

    while [ $(date +%s) -lt $end_time ]; do
        # Check container status
        local status=$(docker ps -a --format '{{.Status}}' --filter "name=$container_name" 2>/dev/null)

        if [ -z "$status" ]; then
            log_error "Container not found: $container_name" "$component"
            return 1
        fi

        if [[ "$status" == "Exited"* ]]; then
            local exit_code=$(docker ps -a --format '{{.Status}}' --filter "name=$container_name" | grep -o 'Exited (\([0-9]*\))' | grep -o '[0-9]*')
            log_info "Container exited with code: $exit_code" "$component"
            return $exit_code
        fi

        log_debug "Container status: $status" "$component"
        sleep 5
    done

    log_warn "Container monitoring timed out: $container_name" "$component"
    return 124
}

# Extract logs from container
extract_logs() {
    local container_name="$1"
    local log_file="${2:-}"
    local component="${3:-LOGS}"

    log_debug "Extracting logs from container: $container_name" "$component"

    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        log_error "Container not found: $container_name" "$component"
        return 1
    fi

    # Extract logs
    local logs_output
    logs_output=$(docker logs "$container_name" 2>&1)

    # Save to file if specified
    if [ -n "$log_file" ]; then
        echo "$logs_output" >"$log_file"
        log_debug "Logs saved to file: $log_file" "$component"
    fi

    # Return logs
    echo "$logs_output"
    return 0
}

# Cleanup containers
cleanup_containers() {
    local pattern="${1:-spices-test-*}"
    local component="${2:-CLEANUP}"

    log_info "Cleaning up containers matching pattern: $pattern" "$component"

    # Get containers matching pattern
    local containers=$(docker ps -a --format '{{.Names}}' | grep "$pattern" || true)

    if [ -z "$containers" ]; then
        log_info "No containers found matching pattern: $pattern" "$component"
        return 0
    fi

    # Remove containers
    local count=0
    while IFS= read -r container_name; do
        if [ -n "$container_name" ]; then
            log_debug "Removing container: $container_name" "$component"
            if docker rm -f "$container_name" &>/dev/null; then
                ((count++))
            else
                log_warn "Failed to remove container: $container_name" "$component"
            fi
        fi
    done <<<"$containers"

    log_info "Removed $count containers" "$component"
    return 0
}

# Cleanup images
cleanup_images() {
    local pattern="${1:-spices-test-*}"
    local component="${2:-CLEANUP}"

    log_info "Cleaning up images matching pattern: $pattern" "$component"

    # Get images matching pattern
    local images=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep "$pattern" || true)

    if [ -z "$images" ]; then
        log_info "No images found matching pattern: $pattern" "$component"
        return 0
    fi

    # Remove images
    local count=0
    while IFS= read -r image_name; do
        if [ -n "$image_name" ]; then
            log_debug "Removing image: $image_name" "$component"
            if docker rmi -f "$image_name" &>/dev/null; then
                ((count++))
            else
                log_warn "Failed to remove image: $image_name" "$component"
            fi
        fi
    done <<<"$images"

    log_info "Removed $count images" "$component"
    return 0
}

# Cleanup all test artifacts
cleanup_all() {
    local component="${1:-CLEANUP}"

    log_info "Performing complete cleanup of Docker test artifacts" "$component"

    # Clean up containers
    cleanup_containers "spices-test-*" "$component"

    # Clean up images
    cleanup_images "spices-test-*" "$component"

    # Clean up volumes if any
    local volumes=$(docker volume ls -q | grep "spices-test" || true)
    if [ -n "$volumes" ]; then
        log_info "Cleaning up volumes..." "$component"
        echo "$volumes" | xargs docker volume rm -f &>/dev/null || true
    fi

    # Clean up networks if any
    local networks=$(docker network ls --format '{{.Name}}' | grep "spices-test" || true)
    if [ -n "$networks" ]; then
        log_info "Cleaning up networks..." "$component"
        echo "$networks" | xargs docker network rm &>/dev/null || true
    fi

    # System cleanup
    log_info "Running Docker system cleanup..." "$component"
    docker system prune -f &>/dev/null || true

    log_info "Complete cleanup finished" "$component"
}

# Export functions for use in other scripts
export -f check_docker_available get_docker_info build_docker_image image_exists
export -f get_image_info run_container exec_in_container monitor_container
export -f extract_logs cleanup_containers cleanup_images cleanup_all
