# Spices Unit Testing Plan

## Overview

This document outlines a comprehensive unit testing strategy for the Spices application to achieve at least 80% code coverage. The plan includes detailed test cases for all modules, classes, and functions, along with mocking strategies for external dependencies.

## Current Testing Status

### Existing Tests

- `tests/test_core_logger.py` - Minimal logger tests (mostly empty)
- `tests/test_core_utils.py` - Doctest-only utils tests
- Test infrastructure uses Python's `unittest` framework
- Coverage tracking with `coverage` package (v6.3.2)

### Testing Framework

- **Primary**: Python `unittest` module
- **Coverage**: `coverage` package with `coveralls` integration
- **Mocking**: `unittest.mock` (built-in)

## 1. Test Structure and Organization

### 1.1 Proposed Test Directory Structure

```
tests/
├── __init__.py
├── fixtures/                     # Test data and fixtures
│   ├── __init__.py
│   ├── sample_configs.py         # Sample .spices.yml configurations
│   ├── mock_system_files.py      # Mock system files content
│   └── test_distributions.py     # Test distribution data
├── unit/                         # Unit tests
│   ├── __init__.py
│   ├── test_cli.py              # CLI module tests
│   ├── api/                     # API module tests
│   │   ├── __init__.py
│   │   └── test_install.py
│   ├── core/                    # Core module tests
│   │   ├── __init__.py
│   │   ├── test_distro.py
│   │   ├── test_errors.py
│   │   ├── test_installer.py
│   │   ├── test_logger.py       # Enhanced logger tests
│   │   ├── test_managers.py
│   │   ├── test_pkgindex.py
│   │   ├── test_spices.py
│   │   └── test_utils.py        # Enhanced utils tests
│   └── config/                  # Config module tests
│       ├── __init__.py
│       ├── test_codenames.py
│       ├── test_distributions.py
│       └── test_managers.py
├── integration/                  # Integration tests
│   ├── __init__.py
│   ├── test_full_install.py     # End-to-end installation tests
│   └── test_distribution_detection.py
└── helpers/                     # Test helper utilities
    ├── __init__.py
    ├── mock_helpers.py          # Common mocking utilities
    └── test_utils.py            # Test utility functions
```

## 2. Module-by-Module Testing Plan

### 2.1 Main Package Tests

#### 2.1.1 `tests/unit/test_cli.py`

**Target**: `spices/cli.py`
**Coverage Goal**: 90%

**Key Test Cases**:

- Command line argument parsing
- Version and help flags
- Install command with options
- Error handling for invalid arguments
- ArgumentParser configuration

**Mocking Strategy**:

- Mock `sys.argv` for different command line scenarios
- Mock `sys.exit` to prevent test termination
- Mock `argparse.ArgumentParser.parse_args()`

### 2.2 API Module Tests

#### 2.2.1 `tests/unit/api/test_install.py`

**Target**: `spices/api/install.py`
**Coverage Goal**: 85%

**Key Test Cases**:

- Configuration file validation
- Schema validation
- Path resolution for config and schema files
- Error handling for missing files
- Successful execution workflow

**Mocking Strategy**:

- Mock `os.path.exists()` and `os.path.isfile()`
- Mock `validate()` function
- Mock `Installer` class and its methods
- Mock file system operations

### 2.3 Core Module Tests

#### 2.3.1 `tests/unit/core/test_installer.py`

**Target**: `spices/core/installer.py`
**Coverage Goal**: 80%

**Key Test Cases**:

- Distribution detection methods (LSB, OS release files, etc.)
- Configuration file parsing
- Package manager selection
- Installation workflow
- Error handling for unsupported distributions

**Mocking Strategy**:

- Mock file system operations (`os.path.exists`, `open`)
- Mock subprocess operations (`Popen`)
- Mock external commands (`find_executable`)
- Mock distribution data and codename indices

#### 2.3.2 `tests/unit/core/test_managers.py`

**Target**: `spices/core/managers.py`
**Coverage Goal**: 80%

**Key Test Cases**:

- Package manager implementations (Apt, Yum, etc.)
- GPG key management (two-layer approach)
- Repository management
- Command execution
- Script creation and execution

**Mocking Strategy**:

- Mock file system operations
- Mock subprocess operations
- Mock network operations (`urlopen`)
- Mock temporary file operations

#### 2.3.3 `tests/unit/core/test_spices.py`

**Target**: `spices/core/spices.py`
**Coverage Goal**: 90%

**Key Test Cases**:

- Configuration processing
- Command list generation
- Manager mapping
- Error handling for empty configurations

**Mocking Strategy**:

- Mock manager classes (Apt, Yum, etc.)
- Mock configuration data
- Mock command generation

#### 2.3.4 `tests/unit/core/test_distro.py`

**Target**: `spices/core/distro.py`
**Coverage Goal**: 85%

**Key Test Cases**:

- Distribution detection
- Derivative handling (Ubuntu -> Debian)
- Manager coordination
- Command filtering by distribution

**Mocking Strategy**:

- Mock `Spices` class
- Mock command objects and their methods
- Mock distribution data

#### 2.3.5 `tests/unit/core/test_errors.py`

**Target**: `spices/core/errors.py`
**Coverage Goal**: 100%

**Key Test Cases**:

- All exception classes
- Error messages
- Inheritance hierarchy
- String representations

**Mocking Strategy**: None needed (pure exception testing)

## 3. Coverage Targets by Module

| Module | Current Coverage | Target Coverage | Priority |
|--------|------------------|-----------------|----------|
| `spices/cli.py` | 0% | 90% | High |
| `spices/api/install.py` | 0% | 85% | High |
| `spices/core/installer.py` | 0% | 80% | High |
| `spices/core/managers.py` | 0% | 80% | High |
| `spices/core/spices.py` | 0% | 90% | High |
| `spices/core/distro.py` | 0% | 85% | High |
| `spices/core/errors.py` | 0% | 100% | Medium |
| `spices/core/logger.py` | 20% | 90% | Medium |
| `spices/core/utils.py` | 30% | 95% | Medium |
| `spices/core/pkgindex.py` | 0% | 75% | Medium |
| `spices/config/*` | 0% | 85-95% | Low |
| **Overall Target** | **~5%** | **≥80%** | **High** |

## 4. Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)

- Set up test infrastructure and directory structure
- Create test fixtures and helper utilities
- Implement basic unit tests for core modules
- **Target**: 40% coverage

### Phase 2: Core Testing (Weeks 3-4)

- Complete unit tests for all core modules
- Implement comprehensive mocking strategies
- Add error case testing
- **Target**: 70% coverage

### Phase 3: Comprehensive Testing (Weeks 5-6)

- Complete unit tests for all modules
- Add integration tests
- Implement edge case testing
- **Target**: 80% coverage

### Phase 4: Optimization (Week 7)

- Optimize test performance
- Add additional edge case tests
- Documentation and cleanup
- **Target**: >85% coverage

## 5. Test Execution Strategy

### 5.1 Continuous Integration Commands

```bash
# Run unit tests with coverage
python -m coverage run --source=spices -m unittest discover -s tests/unit -v

# Run integration tests
python -m coverage run --append --source=spices -m unittest discover -s tests/integration -v

# Generate coverage reports
python -m coverage report -m
python -m coverage html

# Coverage threshold check
python -m coverage report --fail-under=80
```

## 6. Mocking Strategy

### 6.1 System Dependencies

- **File System**: `os.path.exists`, `os.path.isfile`, `open`, `os.listdir`
- **Subprocess**: `subprocess.Popen`, `subprocess.PIPE`
- **Network**: `urllib.request.urlopen`
- **System Commands**: `distutils.spawn.find_executable`

### 6.2 External Libraries

- **YAML**: `yamale.make_schema`, `yamale.validate`
- **HTML Parsing**: `lxml.html`
- **Version Parsing**: `packaging.version.Version`

### 6.3 Internal Dependencies

- **Logger**: Mock logger calls to avoid output during tests
- **Configuration**: Mock configuration loading and validation
- **Distribution Data**: Mock distribution detection and data

## 7. Quality Assurance

### 7.1 Test Quality Metrics

- **Coverage**: Minimum 80% line coverage
- **Test Speed**: Unit tests < 1 second each
- **Test Reliability**: No flaky tests
- **Code Quality**: All tests follow PEP 8

### 7.2 Success Criteria

- **Overall**: ≥80% line coverage
- **Critical Modules**: ≥85% coverage (installer, managers, spices)
- **Error Handling**: 100% coverage (errors module)
- All tests pass consistently
- Comprehensive error case coverage

This comprehensive testing plan provides a roadmap for achieving robust test coverage while maintaining code quality and test reliability. The phased approach ensures steady progress toward the 80% coverage target while building a solid foundation for long-term maintainability.
