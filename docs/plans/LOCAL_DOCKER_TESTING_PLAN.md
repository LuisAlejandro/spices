# Local Docker Testing Plan

## Overview

This document outlines a comprehensive plan to create bash scripts that replicate the functionality of `.github/workflows/docker-tests.yml` for local development and testing. The plan includes scripts for automated discovery, building, and testing across multiple Linux distributions.

## Current Docker Testing Analysis

### Existing GitHub Actions Workflow

- **27 different Docker configurations** across 15 Linux distributions
- **Automated discovery** of Dockerfiles in `tests/docker/` directory
- **Matrix-based testing** strategy for parallel execution
- **Standardized test configuration** using `.spices.yml`
- **Installation and execution testing** in each container

### Tested Distributions

```
Alpine: 3.19
Amazon Linux: 2023
Arch Linux: latest
BusyBox: latest
CentOS: 6, 7, stream8, stream9
CirrOS: latest
CoreOS: latest
Debian: 9, 10, 11, 12
Fedora: 33, 34, 35, 39
Gentoo: latest
openSUSE: leap-15.5
Oracle Linux: 9
Raspbian: latest
Red Hat: 9
Ubuntu: 18.04, 20.04, 22.04, 24.04
```

## 1. Script Architecture

### 1.1 Directory Structure

```
scripts/
├── docker-tests/
│   ├── local-docker-test.sh         # Main test orchestrator
│   ├── discover-images.sh           # Image discovery script
│   ├── build-image.sh               # Image building script
│   ├── test-image.sh                # Individual image testing
│   ├── cleanup.sh                   # Cleanup utilities
│   ├── parallel-runner.sh           # Parallel execution manager
│   ├── config/
│   │   ├── test-config.yml          # Test configuration template
│   │   ├── distribution-mapping.sh  # Distribution-specific settings
│   │   └── test-scenarios.sh        # Test scenario definitions
│   ├── utils/
│   │   ├── logging.sh               # Logging utilities
│   │   ├── docker-utils.sh          # Docker helper functions
│   │   └── validation.sh            # Validation utilities
│   └── reports/
│       ├── generate-report.sh       # Test report generation
│       └── templates/               # Report templates
└── logs/                            # Test execution logs
    └── docker-tests/
        ├── YYYY-MM-DD/              # Date-based log organization
        └── latest/                  # Symlink to latest run
```

### 1.2 Core Scripts Overview

#### Main Orchestrator (`local-docker-test.sh`)

- Entry point for all local Docker testing
- Handles command-line arguments and configuration
- Orchestrates the entire testing workflow
- Provides progress reporting and error handling

#### Image Discovery (`discover-images.sh`)

- Replicates GitHub Actions image discovery logic
- Scans `tests/docker/` for Dockerfiles
- Generates test matrix data
- Supports filtering by distribution or version

#### Image Builder (`build-image.sh`)

- Builds Docker images for testing
- Handles build caching and optimization
- Provides build status reporting
- Supports parallel building

#### Image Tester (`test-image.sh`)

- Executes spices installation tests in containers
- Replicates the GitHub Actions test logic
- Captures test output and results
- Handles test failures gracefully

## 2. Detailed Script Specifications

### 2.1 Main Orchestrator Script

#### `scripts/docker-tests/local-docker-test.sh`

```bash
#!/bin/bash
# Main orchestrator for local Docker testing

# Usage examples:
# ./local-docker-test.sh                          # Test all distributions
# ./local-docker-test.sh --distro debian          # Test only Debian
# ./local-docker-test.sh --version 20.04          # Test only version 20.04
# ./local-docker-test.sh --parallel 4             # Run 4 tests in parallel
# ./local-docker-test.sh --rebuild                # Force rebuild images
# ./local-docker-test.sh --cleanup-only           # Only cleanup old images
# ./local-docker-test.sh --report                 # Generate detailed report
```

**Key Features**:

- Command-line argument parsing
- Configuration validation
- Workflow orchestration
- Progress tracking
- Error handling and recovery
- Report generation

**Command-line Options**:

- `--distro DISTRO`: Test specific distribution
- `--version VERSION`: Test specific version
- `--parallel N`: Number of parallel tests
- `--rebuild`: Force rebuild Docker images
- `--cleanup-only`: Only perform cleanup
- `--no-cleanup`: Skip cleanup after tests
- `--verbose`: Enable verbose output
- `--quiet`: Suppress non-essential output
- `--report`: Generate detailed HTML report
- `--config FILE`: Use custom configuration file
- `--help`: Show usage information

### 2.2 Image Discovery Script

#### `scripts/docker-tests/discover-images.sh`

```bash
#!/bin/bash
# Discover and catalog Docker test images

# Functions:
# - discover_dockerfiles()     # Find all Dockerfiles
# - parse_image_info()         # Extract distro/version info
# - generate_test_matrix()     # Create test matrix JSON
# - filter_images()            # Apply filters
# - validate_dockerfiles()     # Validate Dockerfile syntax
```

**Key Features**:

- Automatic Dockerfile discovery
- Metadata extraction (distro, version, architecture)
- Test matrix generation
- Filtering capabilities
- Validation checks

**Output Format**:

```json
{
  "images": [
    {
      "distro": "debian",
      "version": "11",
      "dockerfile": "tests/docker/debian/11/Dockerfile",
      "image_name": "spices-test-debian-11",
      "test_priority": "high",
      "build_args": {},
      "test_timeout": 300
    }
  ],
  "total_count": 27,
  "filtered_count": 5
}
```

### 2.3 Image Builder Script

#### `scripts/docker-tests/build-image.sh`

```bash
#!/bin/bash
# Build Docker images for testing

# Functions:
# - build_single_image()       # Build individual image
# - build_parallel()           # Build multiple images in parallel
# - check_build_cache()        # Check if rebuild needed
# - optimize_build_order()     # Optimize build sequence
# - handle_build_failure()     # Handle build failures
```

**Key Features**:

- Parallel building support
- Build caching and optimization
- Build status tracking
- Error handling and retry logic
- Build time optimization

**Build Optimization**:

- Layer caching
- Build order optimization (base images first)
- Parallel builds with dependency management
- Build artifact reuse

### 2.4 Image Tester Script

#### `scripts/docker-tests/test-image.sh`

```bash
#!/bin/bash
# Test spices installation in Docker containers

# Functions:
# - create_test_workspace()    # Create test environment
# - generate_spices_config()   # Generate test .spices.yml
# - run_container_test()       # Execute test in container
# - capture_test_output()      # Capture and parse output
# - validate_test_results()    # Validate test success
```

**Key Features**:

- Container lifecycle management
- Test environment setup
- Output capture and analysis
- Result validation
- Timeout handling

**Test Scenarios**:

1. **Basic Installation Test**: Install spices and run basic commands
2. **Package Installation Test**: Test package installation functionality
3. **Configuration Validation Test**: Test configuration file parsing
4. **Error Handling Test**: Test error conditions and recovery
5. **Performance Test**: Measure installation time and resource usage

### 2.5 Parallel Execution Manager

#### `scripts/docker-tests/parallel-runner.sh`

```bash
#!/bin/bash
# Manage parallel test execution

# Functions:
# - schedule_tests()           # Schedule tests for execution
# - manage_worker_pool()       # Manage worker processes
# - monitor_progress()         # Monitor test progress
# - handle_failures()          # Handle test failures
# - collect_results()          # Collect and aggregate results
```

**Key Features**:

- Worker pool management
- Load balancing
- Progress monitoring
- Failure handling
- Resource management

## 3. Configuration Management

### 3.1 Test Configuration Template

#### `scripts/docker-tests/config/test-config.yml`

```yaml
# Test configuration template
test_settings:
  timeout: 300                    # Test timeout in seconds
  parallel_jobs: 4               # Number of parallel tests
  retry_attempts: 2              # Number of retry attempts
  cleanup_after_test: true      # Cleanup containers after test

spices_config:
  version: 1
  managers:
    debian:
      dependencies:
        - procps
        - curl
      postinstall: |
        echo "Installation completed on {{ distro }}:{{ version }}"
    alpine:
      dependencies:
        - procps
        - curl
      postinstall: |
        echo "Installation completed on {{ distro }}:{{ version }}"
    # ... other distributions

distribution_settings:
  debian:
    package_manager: apt
    test_packages: [procps, curl, wget]
    expected_commands: [apt-get, dpkg]
  alpine:
    package_manager: apk
    test_packages: [procps, curl, wget]
    expected_commands: [apk]
  # ... other distributions

test_scenarios:
  basic:
    description: "Basic installation test"
    enabled: true
    timeout: 180

  advanced:
    description: "Advanced functionality test"
    enabled: false
    timeout: 300

  performance:
    description: "Performance benchmark test"
    enabled: false
    timeout: 600
```

### 3.2 Distribution Mapping

#### `scripts/docker-tests/config/distribution-mapping.sh`

```bash
#!/bin/bash
# Distribution-specific configuration and mapping

# Distribution families
declare -A DISTRO_FAMILIES=(
    ["debian"]="debian ubuntu raspbian"
    ["redhat"]="centos fedora oracle redhat amazonlinux"
    ["alpine"]="alpine busybox cirros"
    ["arch"]="archlinux"
    ["suse"]="opensuse"
    ["gentoo"]="gentoo"
    ["coreos"]="coreos"
)

# Package managers by distribution
declare -A PACKAGE_MANAGERS=(
    ["debian"]="apt"
    ["ubuntu"]="apt"
    ["centos"]="yum"
    ["fedora"]="dnf"
    ["alpine"]="apk"
    ["archlinux"]="pacman"
    ["gentoo"]="portage"
    ["opensuse"]="zypper"
)

# Test priorities
declare -A TEST_PRIORITIES=(
    ["debian"]="high"
    ["ubuntu"]="high"
    ["centos"]="high"
    ["fedora"]="medium"
    ["alpine"]="medium"
    ["archlinux"]="low"
)
```

## 4. Utility Functions

### 4.1 Logging Utilities

#### `scripts/docker-tests/utils/logging.sh`

```bash
#!/bin/bash
# Logging utilities for Docker tests

# Functions:
# - setup_logging()            # Initialize logging
# - log_info()                 # Log info messages
# - log_warn()                 # Log warning messages
# - log_error()                # Log error messages
# - log_debug()                # Log debug messages
# - log_test_result()          # Log test results
# - rotate_logs()              # Rotate old log files
```

**Features**:

- Multiple log levels
- Structured logging
- Log rotation
- Colored output for terminal
- JSON format for machine parsing

### 4.2 Docker Utilities

#### `scripts/docker-tests/utils/docker-utils.sh`

```bash
#!/bin/bash
# Docker helper functions

# Functions:
# - check_docker_available()   # Check Docker availability
# - cleanup_containers()       # Cleanup test containers
# - cleanup_images()           # Cleanup test images
# - get_image_info()           # Get image information
# - monitor_container()        # Monitor container execution
# - extract_logs()             # Extract container logs
```

**Features**:

- Docker environment validation
- Container lifecycle management
- Image management
- Resource monitoring
- Log extraction

### 4.3 Validation Utilities

#### `scripts/docker-tests/utils/validation.sh`

```bash
#!/bin/bash
# Validation utilities

# Functions:
# - validate_dockerfile()      # Validate Dockerfile syntax
# - validate_config()          # Validate configuration files
# - validate_test_results()    # Validate test outputs
# - check_dependencies()       # Check script dependencies
# - verify_permissions()       # Verify required permissions
```

## 5. Report Generation

### 5.1 Report Generator

#### `scripts/docker-tests/reports/generate-report.sh`

```bash
#!/bin/bash
# Generate comprehensive test reports

# Functions:
# - generate_html_report()     # Generate HTML report
# - generate_json_report()     # Generate JSON report
# - generate_summary()         # Generate summary report
# - create_charts()            # Create performance charts
# - send_notifications()       # Send notifications (optional)
```

**Report Features**:

- HTML dashboard with interactive charts
- JSON data for API consumption
- Test result summaries
- Performance metrics
- Failure analysis
- Historical trends

### 5.2 Report Template

#### HTML Report Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>Spices Docker Test Results</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Spices Docker Test Results</h1>

    <section id="summary">
        <h2>Test Summary</h2>
        <div class="metrics">
            <div class="metric">
                <span class="value">{{ total_tests }}</span>
                <span class="label">Total Tests</span>
            </div>
            <div class="metric success">
                <span class="value">{{ passed_tests }}</span>
                <span class="label">Passed</span>
            </div>
            <div class="metric failure">
                <span class="value">{{ failed_tests }}</span>
                <span class="label">Failed</span>
            </div>
        </div>
    </section>

    <section id="results">
        <h2>Test Results by Distribution</h2>
        <canvas id="resultsChart"></canvas>
    </section>

    <section id="details">
        <h2>Detailed Results</h2>
        <!-- Detailed test results table -->
    </section>
</body>
</html>
```

## 6. Usage Examples

### 6.1 Basic Usage

```bash
# Run all tests
./scripts/docker-tests/local-docker-test.sh

# Test specific distribution
./scripts/docker-tests/local-docker-test.sh --distro debian

# Test with custom parallelism
./scripts/docker-tests/local-docker-test.sh --parallel 8

# Generate detailed report
./scripts/docker-tests/local-docker-test.sh --report
```

### 6.2 Advanced Usage

```bash
# Test subset of distributions
./scripts/docker-tests/local-docker-test.sh --distro "debian,ubuntu,centos"

# Test with custom configuration
./scripts/docker-tests/local-docker-test.sh --config custom-test-config.yml

# Rebuild and test
./scripts/docker-tests/local-docker-test.sh --rebuild --verbose

# Cleanup only
./scripts/docker-tests/local-docker-test.sh --cleanup-only
```

### 6.3 CI Integration

```bash
# For CI environments
./scripts/docker-tests/local-docker-test.sh \
    --parallel 4 \
    --no-cleanup \
    --report \
    --config ci-config.yml \
    --quiet
```

## 7. Implementation Timeline

### Phase 1: Core Infrastructure (Week 1)

- Create directory structure
- Implement main orchestrator script
- Implement image discovery script
- Basic logging and utilities

### Phase 2: Testing Engine (Week 2)

- Implement image builder script
- Implement image tester script
- Add parallel execution support
- Error handling and recovery

### Phase 3: Configuration and Utilities (Week 3)

- Complete configuration management
- Implement all utility functions
- Add validation and error checking
- Performance optimizations

### Phase 4: Reporting and Polish (Week 4)

- Implement report generation
- Add HTML dashboard
- Performance monitoring
- Documentation and examples

## 8. Benefits of Local Testing

### 8.1 Development Benefits

- **Faster Feedback**: No need to push to GitHub for testing
- **Debugging**: Direct access to containers for debugging
- **Iteration**: Quick iteration on test configurations
- **Offline Testing**: Test without internet connectivity

### 8.2 CI/CD Integration

- **Pre-commit Testing**: Run tests before committing
- **Local CI Simulation**: Replicate CI environment locally
- **Performance Benchmarking**: Measure performance locally
- **Resource Optimization**: Optimize resource usage

### 8.3 Quality Assurance

- **Comprehensive Testing**: Test all distributions locally
- **Consistency**: Ensure consistent test results
- **Reliability**: Reduce dependency on external CI
- **Flexibility**: Customize tests for specific needs

## 9. Maintenance and Updates

### 9.1 Regular Maintenance

- Update Docker images regularly
- Monitor test execution times
- Review and update test configurations
- Clean up old logs and artifacts

### 9.2 Adding New Distributions

1. Add Dockerfile to `tests/docker/DISTRO/VERSION/`
2. Update distribution mapping configuration
3. Add distribution-specific test scenarios
4. Test and validate new configuration

### 9.3 Performance Monitoring

- Track test execution times
- Monitor resource usage
- Identify bottlenecks
- Optimize parallel execution

This comprehensive plan provides a robust foundation for local Docker testing that replicates and extends the GitHub Actions workflow while offering improved flexibility and debugging capabilities.
