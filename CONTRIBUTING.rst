.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/LuisAlejandro/spices/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Improve Documentation
~~~~~~~~~~~~~~~~~~~~~

Spices could always use more documentation, whether as part of the
official Spices docs, in docstrings, or even on the web in blog posts,
articles, and such.

Suggest Features
~~~~~~~~~~~~~~~~

The best way to suggest a feature is to file an issue at
https://github.com/LuisAlejandro/spices/issues.

If you are proposing a feature:

* Explain the problem you are trying to solve.
* Describe the behavior you want and any alternatives you considered.
* Keep the scope as narrow as possible, to make it easier to implement.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send other feedback is to file an issue at
https://github.com/LuisAlejandro/spices/issues.

Local Development
-----------------

Ready to contribute? Here's how to set up ``spices`` for local development.

1. Fork the `spices` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/spices.git
    $ cd spices

3. Create a branch from ``develop``::

    $ git checkout develop
    $ git checkout -b name-of-your-bugfix-or-feature

4. Start the Docker development environment::

    $ make image
    $ make console

   Use ``make console`` for an interactive shell inside the project container.

   Without Docker, run ``make virtualenv`` (installs dev tools and ``pip install -e .``),
   then ``./virtualenv/bin/tox -e lint`` and ``./virtualenv/bin/tox -e coverage``.

   After changing ``requirements-dev.txt`` or the ``Dockerfile``, rebuild the dev
   image with ``make image``. Inside the container, run ``pip install -e .`` before
   using the ``spices`` CLI when the image was built with dev deps only.

Quality Checks
--------------

The lint stack is **Ruff** (format + lint), **pydocstyle**, **bandit**, and
**Pyright**, configured in ``pyproject.toml`` and run via tox.

Before opening a pull request, run::

    $ make format
    $ make lint
    $ make test

Or on the host after ``make virtualenv``::

    $ ./virtualenv/bin/tox -e format
    $ ./virtualenv/bin/tox -e lint
    $ ./virtualenv/bin/tox -e coverage

To exercise all supported Python versions via tox::

    $ make test-all

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests for behavior changes.
2. If the pull request adds functionality, update the docs when user-facing
   behavior changes.
3. Keep the scope focused and link related issues.
4. Check https://github.com/LuisAlejandro/spices/actions and make sure CI passes.

Maintainer Notes
----------------

Releases are handled by maintainers. Contributors should not publish packages
or push release tags.
