# Spices Documentation Plan

## Overview

Spices is a universal dependency resolver and package manager that works across different Linux distributions and package managers. It reads configuration from `.spices.yml` files and installs dependencies using the appropriate package manager for each distribution.

## 1. Documentation Structure

### 1.1 Main Documentation Files

```
docs/
├── index.rst                  # Main documentation index
├── installation.rst           # Installation guide
├── usage.rst                  # Usage examples and guides
├── configuration.rst          # Configuration file format
├── api/                       # API documentation
│   ├── index.rst
│   ├── spices.rst             # Main package
│   ├── api.rst                # API module
│   ├── core.rst               # Core module
│   └── config.rst             # Configuration module
├── examples/                  # Example configurations
│   ├── basic.rst
│   ├── advanced.rst
│   └── multi-distro.rst
├── contributing.rst           # Development guide
├── changelog.rst              # Change history
├── _static/                   # Static assets
│   ├── banner.svg
│   └── author-banner.svg
├── _templates/                # Custom templates
├── conf.py                    # Sphinx configuration
├── Makefile                   # Documentation build
└── requirements.txt           # Documentation dependencies
```

## 2. Module-by-Module Documentation Plan

### 2.1 Main Package (`spices/`)

#### 2.1.1 `spices/__init__.py`

**Purpose**: Package initialization and metadata

**Documentation needed**:

- Package-level docstring explaining the purpose of Spices
- Module metadata documentation (`__author__`, `__version__`, etc.)
- High-level architecture overview
- Quick start example

**Current state**: Has basic docstring but needs expansion

#### 2.1.2 `spices/cli.py`

**Purpose**: Command-line interface module

**Documentation needed**:

- `commandline()` function - CLI argument parsing
- Command structure and options
- Usage examples for each command
- Error handling and exit codes

**Classes/Functions to document**:

- `commandline(argv=None)` - Main CLI entry point

### 2.2 API Module (`spices/api/`)

#### 2.2.1 `spices/api/__init__.py`

**Purpose**: API package initialization

**Documentation needed**:

- API module overview
- Available functions and their purposes
- Integration examples

#### 2.2.2 `spices/api/install.py`

**Purpose**: Main installation API functions

**Documentation needed**:

- `main(**kwargs)` function - Core installation logic
- Configuration file validation
- Error handling and exceptions
- Integration with installer module

**Classes/Functions to document**:

- `main(**kwargs)` - Main installation entry point

### 2.3 Core Module (`spices/core/`)

#### 2.3.1 `spices/core/__init__.py`

**Purpose**: Core package initialization

**Documentation needed**:

- Core module overview
- Architecture explanation
- Module interdependencies

#### 2.3.2 `spices/core/distro.py`

**Purpose**: Distribution detection and management

**Documentation needed**:

- Distribution detection logic
- Supported distributions
- Derivative distribution handling

**Classes/Functions to document**:

- `Distribution` class
  - `__init__(distname, codename, version, data, distributions)`
  - `get_metadistro()` - Get parent distribution
  - `add_manager_sources()` - Add package repositories
  - `add_trusted_keys()` - Add GPG keys
  - `update_package_db()` - Update package database
  - `install()` - Install packages

#### 2.3.3 `spices/core/errors.py`

**Purpose**: Custom exception classes

**Documentation needed**:

- Exception hierarchy
- When each exception is raised
- Error handling best practices

**Classes/Functions to document**:

- `SpicesError` - Base exception class
- `SpicesAreEmpty` - Empty configuration error
- `SpicesNotFound` - Configuration file not found
- `SchemaNotFound` - Schema file not found
- `CannotIdentifyDistribution` - Distribution detection failed
- `UnsupportedDistribution` - Unsupported distribution
- `ThereAreNoCommands` - No commands to execute

#### 2.3.4 `spices/core/installer.py`

**Purpose**: Main installer orchestration

**Documentation needed**:

- Installation workflow
- Distribution detection process
- Package manager selection
- Error handling and recovery

**Classes/Functions to document**:

- `Installer` class
  - `__init__(spices)` - Initialize installer
  - `populate_codename_index()` - Build codename mappings
  - `codename_index(x)` - Sort codenames by priority
  - `parse_apt_policy()` - Parse APT policy information
  - `get_codename_from_apt(origin, component)` - Get codename from APT
  - `parse_os_release(release)` - Parse OS release information
  - `cat_file(release)` - Read file contents
  - `parse_dpkg_origins(origins)` - Parse dpkg origins
  - `cmd_return_full(args, env)` - Execute command and return full output
  - `cmd_return_first_line(args, env)` - Execute command and return first line
  - `try_lsb_release_command()` - Try LSB release detection
  - `try_arch_release_file()` - Try Arch Linux detection
  - `try_gentoo_release_file()` - Try Gentoo detection
  - `try_fedora_release_file()` - Try Fedora detection
  - `try_centos_release_file()` - Try CentOS detection
  - `try_lsb_release_file()` - Try LSB release file
  - `try_os_release_file()` - Try OS release file
  - `try_dpkg_origins()` - Try dpkg origins
  - `try_apt()` - Try APT detection
  - `get_distro_data()` - Get distribution data
  - `normalize_distro_data()` - Normalize distribution data
  - `is_supported_distname()` - Check if distribution is supported
  - `is_supported_codename()` - Check if codename is supported
  - `execute()` - Execute installation
  - `add_trusted_keys()` - Add GPG keys
  - `add_manager_sources()` - Add repositories
  - `update_package_db()` - Update package database
  - `install()` - Install packages

#### 2.3.5 `spices/core/logger.py`

**Purpose**: Logging configuration and utilities

**Documentation needed**:

- Logging configuration
- Log levels and their usage
- Custom logging features

**Classes/Functions to document**:

- `logger` - Global logger instance
- `start_logger(level, logfile)` - Start logging
- `get_logger(name)` - Get named logger
- Logging configuration constants

#### 2.3.6 `spices/core/managers.py`

**Purpose**: Package manager implementations

**Documentation needed**:

- Package manager architecture
- Supported package managers
- GPG key management
- Repository management

**Classes/Functions to document**:

- `Script` class
  - `__init__(content)` - Initialize script
  - `get_execute_command()` - Get execution command
  - `create()` - Create script file
  - `execute()` - Execute script
  - `delete()` - Delete script file
  - `install()` - Install using script

- `PackageManager` class (Base class)
  - `__init__(dependencies, distro, data)` - Initialize manager
  - `_parse_dependencies()` - Parse dependencies
  - `_parse_data(data)` - Parse data
  - `get_enabled_distros()` - Get enabled distributions
  - `get_distros_per_command()` - Get distributions per command
  - `get_execute_command()` - Get execution command
  - `get_update_command()` - Get update command
  - `execute()` - Execute installation
  - `update()` - Update package database
  - `add_trusted_keys()` - Add GPG keys
  - `add_manager_sources()` - Add repositories
  - `install()` - Install packages

- `Apt` class (Debian/Ubuntu package manager)
  - `__init__(dependencies, distro)` - Initialize APT manager
  - `_parse_dependencies()` - Parse APT dependencies
  - `add_trusted_keys()` - Add GPG keys with two-layer approach
  - `_add_keys_from_spices_yml()` - Add keys from configuration
  - `_add_inferred_keys_from_sources()` - Infer keys from sources.list
  - `_get_repository_urls_from_sources()` - Extract repository URLs
  - `_extract_urls_from_file(file_path)` - Extract URLs from file
  - `_infer_and_add_repo_key(repo_url)` - Infer and add repository key
  - `_infer_key_from_release_file(repo_url)` - Infer key from Release file
  - `_add_gpg_key(gpg_key_url)` - Add single GPG key
  - `_has_apt_key()` - Check if apt-key is available
  - `_add_key_with_apt_key(key_file_path)` - Add key with apt-key
  - `_add_key_with_gpg(key_file_path, key_data)` - Add key with gpg
  - `add_manager_sources()` - Add APT repositories
  - `_add_repository(repo_url)` - Add single repository
  - `_generate_repo_name(repo_url)` - Generate repository name

- `Yum` class (Red Hat/CentOS package manager)
  - `__init__(dependencies, distro)` - Initialize YUM manager

- `Apk` class (Alpine package manager)
  - `__init__(dependencies, distro)` - Initialize APK manager

- `Pacman` class (Arch Linux package manager)
  - `__init__(dependencies, distro)` - Initialize Pacman manager

- `Portage` class (Gentoo package manager)
  - `__init__(dependencies, distro)` - Initialize Portage manager

- `Npm` class (Node.js package manager)
  - `__init__(dependencies, distro)` - Initialize NPM manager

- `Yarn` class (Node.js package manager)
  - `__init__(dependencies, distro)` - Initialize Yarn manager

- `Pip` class (Python package manager)
  - `__init__(dependencies, distro)` - Initialize Pip manager

- `Bundler` class (Ruby package manager)
  - `__init__(dependencies, distro)` - Initialize Bundler manager

#### 2.3.7 `spices/core/pkgindex.py`

**Purpose**: Package index management

**Documentation needed**:

- Package index structure
- Index generation process
- Distribution-specific handling

**Classes/Functions to document**:

- `request_first_bytes(debian_release_url)` - Request first bytes from URL
- `debian_codename_index()` - Generate Debian codename index
- `arch_codename_index()` - Generate Arch Linux codename index
- `fedora_codename_index()` - Generate Fedora codename index
- `alpine_codename_index()` - Generate Alpine codename index
- `centos_codename_index()` - Generate CentOS codename index
- `gentoo_codename_index()` - Generate Gentoo codename index

#### 2.3.8 `spices/core/spices.py`

**Purpose**: Core Spices class and logic

**Documentation needed**:

- Core application logic
- Configuration processing
- Command generation

**Classes/Functions to document**:

- `Spices` class
  - `__init__(content)` - Initialize Spices
  - `merge_data_incrementally(data_list)` - Merge configuration data
  - `generate_commandlist()` - Generate command list
  - `get_command_from_manager(manager_name, dependencies, distro, data)` - Get command from manager
  - Class attributes:
    - `native_managers_map` - Native package managers
    - `distribution_map` - Distribution to manager mapping
    - `other_managers_map` - Other package managers

#### 2.3.9 `spices/core/utils.py`

**Purpose**: Utility functions

**Documentation needed**:

- Utility function descriptions
- Usage examples
- Integration with other modules

**Classes/Functions to document**:

- `flatten_list(lst)` - Flatten nested lists
- `validate(spicespath, schemapath)` - Validate configuration file
- Other utility functions

### 2.4 Config Module (`spices/config/`)

#### 2.4.1 `spices/config/__init__.py`

**Purpose**: Configuration package initialization

**Documentation needed**:

- Configuration module overview
- Available configuration options
- Schema validation

#### 2.4.2 `spices/config/codenames.py`

**Purpose**: Distribution codename mappings

**Documentation needed**:

- Codename mapping structure
- Supported distributions and versions
- How to add new distributions

**Constants to document**:

- `debian_suites` - Debian suite names
- `fedora_version_url` - Fedora version URL
- `alpine_version_url` - Alpine version URL
- `debian_release_url_holder` - Debian release URL template
- `olddebian_version_url` - Old Debian version URL
- `base_debian_codename_index` - Base Debian codename mappings
- `olddebian_release_url_holder` - Old Debian release URL template
- `debian_oldversioning` - Debian old versioning
- `base_arch_codename_index` - Base Arch codename mappings
- `base_fedora_codename_index` - Base Fedora codename mappings
- `base_alpine_codename_index` - Base Alpine codename mappings
- `base_gentoo_codename_index` - Base Gentoo codename mappings
- `base_centos_codename_index` - Base CentOS codename mappings

#### 2.4.3 `spices/config/distributions.py`

**Purpose**: Distribution configuration data

**Documentation needed**:

- Distribution configuration structure
- Supported distributions
- Manager assignments

**Constants to document**:

- `distrodata` - Distribution data mapping

#### 2.4.4 `spices/config/managers.py`

**Purpose**: Package manager configurations

**Documentation needed**:

- Package manager configurations
- Command-line arguments
- Environment variables

**Constants to document**:

- `native_managers` - Native package manager configurations
- `other_managers` - Other package manager configurations

#### 2.4.5 `spices/config/schema.yml`

**Purpose**: Configuration schema validation

**Documentation needed**:

- Schema structure
- Validation rules
- Configuration examples

## 3. Documentation Content Plan

### 3.1 User Documentation

#### 3.1.1 Installation Guide (`docs/installation.rst`)

- System requirements
- Installation methods (pip, source, package managers)
- Verification steps
- Troubleshooting common issues

#### 3.1.2 Usage Guide (`docs/usage.rst`)

- Basic usage examples
- Command-line interface
- Configuration file format
- Common workflows

#### 3.1.3 Configuration Guide (`docs/configuration.rst`)

- Configuration file structure
- Schema validation
- Supported package managers
- Repository and GPG key management
- Multi-distribution support

#### 3.1.4 Examples (`docs/examples/`)

- Basic configuration examples
- Advanced scenarios
- Multi-distribution setups
- Integration with CI/CD

### 3.2 Developer Documentation

#### 3.2.1 API Documentation (`docs/api/`)

- Complete API reference
- Class hierarchy
- Method signatures
- Usage examples

#### 3.2.2 Contributing Guide (`docs/contributing.rst`)

- Development setup
- Code style guidelines
- Testing procedures
- Pull request process

## 4. Implementation Steps

### Phase 1: Setup Documentation Infrastructure

1. Create documentation directory structure
2. Setup Sphinx configuration
3. Create basic RST files
4. Configure build system

### Phase 2: Module Documentation

1. Document each module with comprehensive docstrings
2. Add type hints where appropriate
3. Include usage examples in docstrings
4. Document all public APIs

### Phase 3: API Reference Generation

1. Use Sphinx autodoc to generate API reference
2. Organize by module and class
3. Include inheritance diagrams
4. Add cross-references

### Phase 4: User Guides

1. Write installation guide
2. Create usage examples
3. Document configuration options
4. Add troubleshooting section

### Phase 5: Advanced Documentation

1. Add architectural diagrams
2. Create developer guides
3. Document extension points
4. Add performance considerations

## 5. Documentation Standards

### 5.1 Docstring Format

- Use Google-style docstrings
- Include Args, Returns, Raises sections
- Provide examples where appropriate
- Document type hints

### 5.2 Code Examples

- Include working code examples
- Test all examples
- Show common use cases
- Demonstrate error handling

### 5.3 Cross-References

- Link between related modules
- Reference configuration options
- Link to external documentation
- Maintain consistency

## 6. Maintenance Plan

### 6.1 Documentation Updates

- Update docs with each release
- Review and update examples
- Check for broken links
- Update dependencies

### 6.2 Quality Assurance

- Spell check all documentation
- Review for clarity and completeness
- Test all code examples
- Validate cross-references

## 7. Tools and Dependencies

### 7.1 Documentation Tools

- Sphinx for documentation generation
- sphinx-rtd-theme for styling
- sphinx-autodoc for API documentation
- sphinx-napoleon for Google-style docstrings

### 7.2 Additional Extensions

- sphinx-autosummary for automatic summaries
- sphinx-intersphinx for external references
- sphinx-viewcode for source code links
- sphinx-githubpages for GitHub Pages deployment

This comprehensive plan ensures that every aspect of the Spices application is properly documented, from high-level architecture to individual method signatures, making it accessible to both users and developers.
