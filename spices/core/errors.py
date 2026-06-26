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
Spices exception hierarchy.

This module defines base and concrete exception classes raised during
distribution detection, configuration validation, and install orchestration.
"""


class SpicesError(Exception):
    """
    Base exception for all Spices errors.

    Subclasses represent specific failure modes. Do not raise this class
    directly; catch it to handle any Spices-specific error.
    """


class CannotIdentifyDistribution(SpicesError):
    """Raised when the host Linux distribution cannot be identified."""

    def __str__(self):
        """Return a user-facing message."""
        return "We could not identify your distribution."


class UnsupportedDistribution(SpicesError):
    """Raised when the detected distribution is not supported."""

    def __str__(self):
        """Return a user-facing message."""
        return "Your distribution is not supported."


class SpicesAreEmpty(SpicesError):
    """Raised when spices configuration content is empty."""

    def __str__(self):
        """Return an empty user-facing message."""
        return ""


class ThereAreNoCommands(SpicesError):
    """Raised when no install commands were generated from configuration."""

    def __str__(self):
        """Return an empty user-facing message."""
        return ""


class SpicesNotFound(SpicesError):
    """Raised when ``.spices.yml`` is missing from the working directory."""

    def __init__(self, currdir):
        """
        Initialize with the directory that was searched.

        :param currdir: current working directory path.
        """
        super().__init__(currdir)
        self.currdir = currdir

    def __str__(self):
        """Return a user-facing message with documentation link."""
        return (
            f"A .spices.yml was not found on current directory {self.currdir}"
            "\n"
            "Check https://spices.readthedocs.io/en/latest/ to know how to "
            "create a Spices file."
            "\n\n"
        )


class SchemaNotFound(SpicesError):
    """Raised when the Yamale schema file is missing from the install."""

    def __init__(self, schemadir):
        """
        Initialize with the schema directory that was searched.

        :param schemadir: path to the expected schema directory.
        """
        super().__init__(schemadir)
        self.schemadir = schemadir

    def __str__(self):
        """Return a user-facing message with documentation link."""
        return (
            f"A schema was not found on the schema directory {self.schemadir}"
            "\n"
            "Go to https://spices.readthedocs.io/en/latest/ and follow "
            "instructions to reinstall Spices."
            "\n\n"
        )


class ValidationError(SpicesError):
    """Raised when ``.spices.yml`` fails Yamale schema validation."""

    def __init__(self, details):
        """
        Initialize with validation error details.

        :param details: Yamale validation error message.
        """
        super().__init__(details)
        self.details = details

    def __str__(self):
        """Return the validation error details."""
        return f"{self.details}\n"
