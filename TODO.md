# Spices - First Version (v1.0) TODO

This document aggregates the remaining work needed to reach the first stable release of Spices, based on the existing plans and repository state.

## 1. Unit Testing (Target: ≥80% Coverage)

*Currently at ~5% coverage. See `rosey/plans/UNIT_TESTING_PLAN.md` for details.*

- [ ] **Phase 1: Foundation**
  - [ ] Set up test infrastructure, directory structure, test fixtures, and helper utilities.
  - [ ] Implement basic unit tests for core modules.
- [ ] **Phase 2: Core Testing**
  - [ ] `spices/cli.py` (Target: 90%)
  - [ ] `spices/api/install.py` (Target: 85%)
  - [ ] `spices/core/installer.py` (Target: 80%)
  - [ ] `spices/core/managers.py` (Target: 80%)
  - [ ] `spices/core/spices.py` (Target: 90%)
  - [ ] `spices/core/distro.py` (Target: 85%)
  - [ ] `spices/core/errors.py` (Target: 100%)
- [ ] **Phase 3: Comprehensive Testing**
  - [ ] Complete unit tests for remaining modules (`logger`, `utils`, `pkgindex`, config).
  - [ ] Add integration and edge-case testing.

## 2. Local Docker Testing Infrastructure

*Replicating GitHub Actions for local dev. See `rosey/plans/LOCAL_DOCKER_TESTING_PLAN.md`.*

- [ ] **Phase 1: Core Infrastructure**
  - [ ] Create `scripts/docker-tests/local-docker-test.sh` (Main orchestrator).
  - [ ] Create `scripts/docker-tests/discover-images.sh` (Image discovery).
- [ ] **Phase 2: Testing Engine**
  - [ ] Create `scripts/docker-tests/build-image.sh` (Image builder).
  - [ ] Create `scripts/docker-tests/test-image.sh` (Image tester).
  - [ ] Add parallel execution support (`parallel-runner.sh`).
- [ ] **Phase 3 & 4: Configuration and Reporting**
  - [ ] Add distribution mapping (`config/distribution-mapping.sh`).
  - [ ] Implement validation and logging utility functions.
  - [ ] Implement HTML/JSON report generation.

## 3. Documentation

*See `rosey/plans/DOCUMENTATION_PLAN.md`.*

- [ ] **Phase 1 & 2: Setup & Module Documentation**
  - [ ] Setup Sphinx configuration and doc directory structure.
  - [ ] Document all modules with comprehensive docstrings (Google-style) and type hints.
- [ ] **Phase 3: API Reference**
  - [ ] Use `sphinx-autodoc` to generate the complete API reference.
- [ ] **Phase 4: User Guides**
  - [ ] Write `installation.rst` (Installation Guide).
  - [ ] Write `usage.rst` (Usage Examples).
  - [ ] Write `configuration.rst` (Configuration File Format).

## 4. Maintenance & Repository Health

- [ ] **Dependencies**
  - [ ] Review, update, and merge the ~20 open Dependabot pull requests (bumping `coverage`, `pytest`, `sphinx`, `tox`, `pip`, etc.).
- [ ] **Cleanup**
  - [ ] Fix any unresolved linter/formatter errors.

## 5. Release Preparation

- [ ] **Changelog & Versioning**
  - [ ] Finalize features and bugs for the milestone.
  - [ ] Generate changelog using `gitchangelog > HISTORY.rst`.
  - [ ] Bump version from `0.0.1` to `1.0.0` (or `0.1.0` if using a beta path) using `bumpversion`.
  - [ ] Publish the new version to PyPI via `make release`.
