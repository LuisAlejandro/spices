# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2016-2022, Spices Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Package Manager Integration Module.

This module provides the core abstractions for installing dependencies through
native and third-party package managers on Linux distributions. It defines a
base ``PackageManager`` class and concrete implementations for common managers
(APT, YUM, APK, Pacman, Portage) as well as language-specific tools (npm,
yarn, pip, bundler).

The module contains:

1. **Script**: A helper for creating, executing, and removing temporary bash
   scripts used during installation workflows.

2. **PackageManager**: Base class that parses dependency metadata, builds
   install and update command lines from distribution configuration, and runs
   package manager subprocesses with merged environment variables.

3. **Distribution-specific managers**: Subclasses wired to entries in
   ``native_managers`` and ``other_managers`` from ``spices.config.distributions``.

4. **APT extensions**: Repository and GPG key handling, including two-layer key
   management (explicit keys from spices YAML plus inference from
   ``sources.list`` files).

Usage:
    Manager classes are instantiated by the installer with dependency lists and
    optional distribution data, then ``install()`` is called to update indexes
    (where applicable) and run the install command.
"""

import os
import shutil
import tempfile
from io import BytesIO
from subprocess import PIPE, Popen  # nosec B404
from tempfile import mkstemp
from urllib.request import urlopen

from ..config.distributions import distrodata, native_managers, other_managers
from .logger import logger


class Script(object):
    """Temporary bash script wrapper for installation helper commands."""

    def __init__(self, content):
        """
        Initialize a script with the given shell content.

        :param content: bash script body to write when ``create()`` is called.
        """
        self.content = content
        self.scriptpath = ""

    def get_execute_command(self):
        """Return the command argv list used to run this script."""
        return ["bash", self.scriptpath]

    def create(self):
        """Write script content to a temporary ``.sh`` file."""
        _, self.scriptpath = mkstemp(suffix=".sh", prefix="spices-script")
        with open(self.scriptpath, "w") as script:
            script.write(self.content)

    def execute(self):
        """Run the script and stream stdout lines to the application logger."""
        result = Popen(args=self.get_execute_command(), stdout=PIPE, stderr=PIPE, close_fds=True)  # nosec B603

        for line in iter((result.stdout or BytesIO(b"")).readline, ""):
            if line:
                logger.info(str(line).strip("\n"))
            else:
                break

    def delete(self):
        """Remove the temporary script file from disk."""
        os.remove(self.scriptpath)

    def install(self):
        """Create, execute, and delete the temporary script."""
        self.create()
        self.execute()
        self.delete()

    def get_enabled_distros(self):
        """Return all distribution keys known to the distro configuration."""
        return list(distrodata.keys())

    def add_trusted_keys(self):
        """No-op placeholder for GPG key setup in script-based workflows."""
        pass

    def add_manager_sources(self):
        """No-op placeholder for repository source setup."""
        pass

    def update(self):
        """No-op placeholder for package index refresh."""
        pass


class PackageManager(object):
    """Base package manager that builds and runs install/update commands."""

    def __init__(self, dependencies, distro, data=None):
        """
        Initialize manager state from dependencies and optional distro data.

        :param dependencies: package names or dependency specifiers to install.
        :param distro: target distribution key, or ``None`` for all matches.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        self.dependencies = dependencies
        self.distro = distro
        self.manager = {}
        self.enabled_distros = []
        # Extract repositories and GPG keys from dependencies if they exist
        self.repositories = []
        self.gpg_keys = []
        self._parse_dependencies()
        # Also parse from data if provided (new schema format)
        if data:
            self._parse_data(data)

    def _parse_dependencies(self):
        """Parse dependencies to extract repositories and GPG keys."""
        if not self.dependencies:
            return

        # This is a placeholder - subclasses should override this
        # to implement their own parsing logic
        pass

    def _parse_data(self, data):
        """Parse repositories and GPG keys from the data dictionary."""
        if "repositories" in data:
            self.repositories.extend(data["repositories"])
        if "gpg_keys" in data:
            self.gpg_keys.extend(data["gpg_keys"])

    def get_enabled_distros(self):
        """Return distros enabled for this manager's install command."""
        if self.distro:
            return [self.distro]
        return self.get_distros_per_command()

    def get_distros_per_command(self):
        """Return distro keys whose manager command matches this instance."""
        distros_per_command = []
        for distro, ddata in distrodata.items():
            if "managers" not in ddata:
                continue
            for mdata in ddata["managers"].values():
                if "command" not in mdata or mdata["command"] != self.manager["command"]:
                    continue
                distros_per_command.append(distro)
        return list(set(distros_per_command))

    def get_execute_command(self):
        """Build the argv list for the package install subprocess."""
        cmd = []
        cmd.extend([self.manager.get("command")])
        cmd.extend([self.manager.get("install")])
        args = self.manager.get("args", [])
        if args:
            cmd.extend(args)
        cmd.extend(self.dependencies)
        return cmd

    def get_update_command(self):
        """Build the argv list for the package index update subprocess."""
        cmd = []
        cmd.extend([self.manager.get("command")])
        cmd.extend([self.manager.get("update")])
        return cmd

    def execute(self):
        """Run the install command and log subprocess stdout."""
        # Merge manager env with current environment
        env = os.environ.copy()
        env.update(self.manager.get("env", {}))

        try:
            result = Popen(args=self.get_execute_command(), stdout=PIPE, stderr=PIPE, env=env, close_fds=True)  # nosec B603

            for line in iter((result.stdout or BytesIO(b"")).readline, ""):
                if line:
                    logger.info(str(line).strip("\n"))
                else:
                    break
        except FileNotFoundError:
            logger.error(
                (f"Command '{self.manager.get('command')}' not found. Make sure it's installed and in your PATH.")
            )
            raise

    def update(self):
        """Refresh package indexes when an update command is configured."""
        # Skip update if no update command is defined
        if not self.manager.get("update"):
            logger.info(f"No update command defined for {self.manager.get('command')}, skipping update.")
            return

        # Merge manager env with current environment
        env = os.environ.copy()
        env.update(self.manager.get("env", {}))

        result = Popen(args=self.get_update_command(), stdout=PIPE, stderr=PIPE, env=env, close_fds=True)  # nosec B603

        for line in iter((result.stdout or BytesIO(b"")).readline, ""):
            if line:
                logger.info(str(line).strip("\n"))
            else:
                break

    def add_trusted_keys(self):
        """Add GPG keys for repositories. Override in subclasses."""
        pass

    def add_manager_sources(self):
        """Add repository sources. Override in subclasses."""
        pass

    def install(self):
        """Update indexes (if configured) and install dependencies."""
        self.update()
        self.execute()


class Apt(PackageManager):
    """APT package manager with repository and GPG key support."""

    def __init__(self, dependencies, distro, data=None):
        """
        Configure APT manager metadata from distribution configuration.

        :param dependencies: package names or ``repo:`` / ``gpg:`` specifiers.
        :param distro: target distribution key.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        super().__init__(dependencies, distro, data)
        self.manager = native_managers["apt"]

    def _parse_dependencies(self):
        """Parse dependencies to extract repositories and GPG keys for APT."""
        if not self.dependencies:
            return

        # Look for repository and GPG key specifications in dependencies
        # Format: repo:repository_url or gpg:gpg_key_url
        for dep in self.dependencies:
            if dep.startswith("repo:"):
                repo_url = dep[5:]  # Remove 'repo:' prefix
                self.repositories.append(repo_url)
            elif dep.startswith("gpg:"):
                gpg_url = dep[4:]  # Remove 'gpg:' prefix
                self.gpg_keys.append(gpg_url)

    def add_trusted_keys(self):
        """Add GPG keys for APT repositories using a two-layer approach.

        1. Add keys specified in the spices yml file
        2. Infer and add missing keys from sources.list and sources.list.d/
        """
        logger.info("Starting two-layer GPG key management...")

        # Layer 1: Add keys from spices yml file
        self._add_keys_from_spices_yml()

        # Layer 2: Infer and add missing keys from sources.list files
        self._add_inferred_keys_from_sources()

    def _add_keys_from_spices_yml(self):
        """Layer 1: Add GPG keys specified in the spices yml file."""
        if not self.gpg_keys:
            logger.info("No GPG keys specified in spices yml file")
            return

        logger.info("Layer 1: Adding GPG keys from spices yml file...")

        for gpg_key_url in self.gpg_keys:
            try:
                self._add_gpg_key(gpg_key_url)
            except Exception as e:
                logger.error(f"Failed to add GPG key from {gpg_key_url}: {e}")

    def _add_inferred_keys_from_sources(self):
        """Layer 2: Infer and add missing GPG keys from sources.list files."""
        logger.info("Layer 2: Inferring missing GPG keys from sources.list files...")

        # Get all repository URLs from sources.list files
        repo_urls = self._get_repository_urls_from_sources()

        if not repo_urls:
            logger.info("No repositories found in sources.list files")
            return

        # For each repository, try to infer and add its GPG key
        for repo_url in repo_urls:
            try:
                self._infer_and_add_repo_key(repo_url)
            except Exception as e:
                logger.error(f"Failed to infer GPG key for repository {repo_url}: {e}")

    def _get_repository_urls_from_sources(self):
        """Extract repository URLs from sources.list and sources.list.d/ files."""
        repo_urls = set()

        # Read main sources.list file
        sources_list_path = "/etc/apt/sources.list"
        if os.path.exists(sources_list_path):
            repo_urls.update(self._extract_urls_from_file(sources_list_path))

        # Read sources.list.d/ directory
        sources_list_d_path = "/etc/apt/sources.list.d/"
        if os.path.exists(sources_list_d_path):
            for filename in os.listdir(sources_list_d_path):
                if filename.endswith(".list"):
                    file_path = os.path.join(sources_list_d_path, filename)
                    repo_urls.update(self._extract_urls_from_file(file_path))

        return list(repo_urls)

    def _extract_urls_from_file(self, file_path):
        """Extract repository URLs from a sources.list file."""
        urls = set()

        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line.startswith("#") or not line:
                        continue

                    # Parse deb/deb-src lines
                    # Format: deb [arch=amd64] https://example.com/repo distribution component
                    parts = line.split()
                    if len(parts) >= 3 and parts[0] in ["deb", "deb-src"]:
                        # Find the URL part (after [arch=...] if present)
                        url_part = None
                        for part in parts[1:]:
                            if part.startswith("[") and part.endswith("]"):
                                continue  # Skip architecture specification
                            if part.startswith(("http://", "https://", "ftp://")):
                                url_part = part
                                break

                        if url_part:
                            # Extract base URL (remove distribution/component parts)
                            from urllib.parse import urlparse

                            parsed = urlparse(url_part)
                            base_url = f"{parsed.scheme}://{parsed.netloc}"
                            urls.add(base_url)

        except (IOError, OSError) as e:
            logger.warning(f"Could not read {file_path}: {e}")

        return urls

    def _infer_and_add_repo_key(self, repo_url):
        """Infer and add GPG key for a specific repository URL."""
        logger.info(f"Inferring GPG key for repository: {repo_url}")

        # Common patterns for GPG key URLs
        key_patterns = [
            f"{repo_url}/gpg",  # Direct gpg endpoint
            f"{repo_url}/key.gpg",  # Common key filename
            f"{repo_url}/keyring.gpg",  # Alternative key filename
            f"{repo_url}/Release.gpg",  # Release.gpg file
            f"{repo_url}/apt.gpg",  # apt.gpg file
        ]

        # Try each pattern to find a valid GPG key
        for key_url in key_patterns:
            try:
                logger.info(f"Trying GPG key URL: {key_url}")
                self._add_gpg_key(key_url)
                logger.info(f"Successfully added GPG key from: {key_url}")
                return  # Success, no need to try other patterns
            except Exception as e:
                logger.debug(f"Failed to add GPG key from {key_url}: {e}")
                continue

        # If no direct key URL works, try to fetch from Release file
        try:
            self._infer_key_from_release_file(repo_url)
        except Exception as e:
            logger.warning(f"Could not infer GPG key for {repo_url}: {e}")

    def _infer_key_from_release_file(self, repo_url):
        """Try to infer GPG key from Release file."""
        release_url = f"{repo_url}/dists/stable/Release"

        try:
            with urlopen(release_url) as response:
                release_content = response.read().decode("utf-8")

                # Look for GPG key fingerprint in Release file
                import re

                fingerprint_match = re.search(r"Fingerprint:\s*([A-F0-9]{40})", release_content)
                if fingerprint_match:
                    fingerprint = fingerprint_match.group(1)
                    logger.info(f"Found GPG fingerprint in Release file: {fingerprint}")
                    # Note: In a full implementation, you might want to fetch the key
                    # from a keyserver using this fingerprint
                    # For now, we'll just log it
                    return
        except Exception as e:
            logger.debug(f"Could not read Release file from {release_url}: {e}")

    def _add_gpg_key(self, gpg_key_url):
        """Add a single GPG key from URL."""
        logger.info(f"Adding GPG key from: {gpg_key_url}")

        # Download the GPG key
        with urlopen(gpg_key_url) as response:
            gpg_key_data = response.read()

        # Create a temporary file for the key
        with tempfile.NamedTemporaryFile(suffix=".gpg", delete=False) as temp_file:
            temp_file.write(gpg_key_data)
            temp_file_path = temp_file.name

        try:
            # Add the key using apt-key (for older systems) or gpg (for newer systems)
            if self._has_apt_key():
                self._add_key_with_apt_key(temp_file_path)
            else:
                self._add_key_with_gpg(temp_file_path, gpg_key_data)
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    def _has_apt_key(self):
        """Check if apt-key command is available."""
        return shutil.which("apt-key") is not None

    def _add_key_with_apt_key(self, key_file_path):
        """Add GPG key using apt-key (deprecated but still available on older systems)."""
        # Merge manager env with current environment
        env = os.environ.copy()
        env.update(self.manager.get("env", {}))

        cmd = ["apt-key", "add", key_file_path]
        result = Popen(cmd, stdout=PIPE, stderr=PIPE, env=env)  # nosec B603
        stdout, stderr = result.communicate()

        if result.returncode != 0:
            raise Exception(f"apt-key failed: {stderr.decode()}")

        logger.info("GPG key added successfully with apt-key")

    def _add_key_with_gpg(self, key_file_path, key_data):
        """Add GPG key using gpg (modern approach)."""
        # Import the key to the system keyring
        cmd = ["gpg", "--dearmor", "-o", "/etc/apt/trusted.gpg.d/spices-key.gpg", key_file_path]
        result = Popen(cmd, stdout=PIPE, stderr=PIPE)  # nosec B603
        stdout, stderr = result.communicate()

        if result.returncode != 0:
            raise Exception(f"gpg --dearmor failed: {stderr.decode()}")

        logger.info("GPG key added successfully with gpg")

    def add_manager_sources(self):
        """Add APT repository sources."""
        if not self.repositories:
            return

        logger.info("Adding APT repository sources...")

        for repo_url in self.repositories:
            try:
                self._add_repository(repo_url)
            except Exception as e:
                logger.error(f"Failed to add repository {repo_url}: {e}")

    def _add_repository(self, repo_url):
        """Add a single APT repository."""
        logger.info(f"Adding repository: {repo_url}")

        # Parse repository URL to extract components
        # Expected format: deb [arch=amd64] https://example.com/repo distribution component
        # or: deb-src [arch=amd64] https://example.com/repo distribution component

        # For now, we'll create a simple repository entry
        # In a full implementation, you'd want to parse the URL more intelligently
        repo_name = self._generate_repo_name(repo_url)
        repo_entry = f"deb {repo_url} /"

        # Write to sources.list.d
        sources_file = f"/etc/apt/sources.list.d/{repo_name}.list"

        try:
            with open(sources_file, "w") as f:
                f.write(repo_entry + "\n")
            logger.info(f"Repository added to {sources_file}")
        except PermissionError:
            logger.error(f"Permission denied writing to {sources_file}")
            raise
        except Exception as e:
            logger.error(f"Failed to write repository file: {e}")
            raise

    def _generate_repo_name(self, repo_url):
        """Generate a safe filename for the repository."""
        # Extract domain from URL and create a safe filename
        from urllib.parse import urlparse

        parsed = urlparse(repo_url)
        domain = parsed.netloc.replace(".", "_").replace("-", "_")
        return f"spices_{domain}"


class Yum(PackageManager):
    """YUM/DNF package manager implementation."""

    def __init__(self, dependencies, distro, data=None):
        """
        Configure YUM manager metadata from distribution configuration.

        :param dependencies: package names to install.
        :param distro: target distribution key.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        super().__init__(dependencies, distro, data)
        self.manager = native_managers["yum"]


class Apk(PackageManager):
    """Alpine APK package manager implementation."""

    def __init__(self, dependencies, distro, data=None):
        """
        Configure APK manager metadata from distribution configuration.

        :param dependencies: package names to install.
        :param distro: target distribution key.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        super().__init__(dependencies, distro, data)
        self.manager = native_managers["apk"]


class Pacman(PackageManager):
    """Arch Linux pacman package manager implementation."""

    def __init__(self, dependencies, distro, data=None):
        """
        Configure pacman manager metadata from distribution configuration.

        :param dependencies: package names to install.
        :param distro: target distribution key.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        super().__init__(dependencies, distro, data)
        self.manager = native_managers["pacman"]


class Portage(PackageManager):
    """Gentoo Portage package manager implementation."""

    def __init__(self, dependencies, distro, data=None):
        """
        Configure Portage manager metadata from distribution configuration.

        :param dependencies: package names to install.
        :param distro: target distribution key.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        super().__init__(dependencies, distro, data)
        self.manager = native_managers["portage"]


class Npm(PackageManager):
    """npm package manager implementation."""

    def __init__(self, dependencies, distro, data=None):
        """
        Configure npm manager metadata from distribution configuration.

        :param dependencies: package names to install.
        :param distro: target distribution key.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        super().__init__(dependencies, distro, data)
        self.manager = other_managers["npm"]

    def install(self):
        """Override install to skip update step for npm."""
        # npm doesn't need an update step, just execute
        self.execute()


class Yarn(PackageManager):
    """Yarn package manager implementation."""

    def __init__(self, dependencies, distro, data=None):
        """
        Configure Yarn manager metadata from distribution configuration.

        :param dependencies: package names to install.
        :param distro: target distribution key.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        super().__init__(dependencies, distro, data)
        self.manager = other_managers["yarn"]

    def install(self):
        """Override install to skip update step for yarn."""
        # yarn doesn't need an update step, just execute
        self.execute()


class Pip(PackageManager):
    """pip package manager implementation."""

    def __init__(self, dependencies, distro, data=None):
        """
        Configure pip manager metadata, preferring ``pip3`` when ``pip`` is absent.

        :param dependencies: package names to install.
        :param distro: target distribution key.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        super().__init__(dependencies, distro, data)
        self.manager = other_managers["pip"].copy()  # Make a copy to avoid modifying the global config

        # Check if pip is available, otherwise try pip3
        if not self._command_exists("pip") and self._command_exists("pip3"):
            logger.info("'pip' not found, using 'pip3' instead")
            self.manager["command"] = "pip3"

    def _command_exists(self, command):
        """Check if a command exists in the system PATH."""
        return shutil.which(command) is not None

    def install(self):
        """Override install to skip update step for pip."""
        # Pip doesn't need an update step, just execute
        self.execute()


class Bundler(PackageManager):
    """Ruby Bundler package manager implementation."""

    def __init__(self, dependencies, distro, data=None):
        """
        Configure Bundler manager metadata from distribution configuration.

        :param dependencies: package names to install.
        :param distro: target distribution key.
        :param data: optional spices YAML fragment with repositories and GPG keys.
        """
        super().__init__(dependencies, distro, data)
        self.manager = other_managers["bundler"]

    def install(self):
        """Override install to skip update step for bundler."""
        # bundler doesn't need an update step, just execute
        self.execute()
