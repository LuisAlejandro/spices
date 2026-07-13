.. image:: https://raw.githubusercontent.com/LuisAlejandro/spices/develop/docs/_static/banner.svg

..

    Spices is a universal dependency resolver: declare packages once in
    ``.spices.yml`` and install them with the matching native or language
    package manager on the host.

.. image:: https://img.shields.io/pypi/v/spices.svg
   :target: https://pypi.org/project/spices/
   :alt: PyPI Package

.. image:: https://img.shields.io/github/release/LuisAlejandro/spices.svg
   :target: https://github.com/LuisAlejandro/spices/releases
   :alt: Github Releases

.. image:: https://img.shields.io/github/issues/LuisAlejandro/spices
   :target: https://github.com/LuisAlejandro/spices/issues?q=is%3Aopen
   :alt: Github Issues

.. image:: https://github.com/LuisAlejandro/spices/actions/workflows/push.yml/badge.svg
   :target: https://github.com/LuisAlejandro/spices/actions?query=workflow%3APush
   :alt: Push

.. image:: https://coveralls.io/repos/github/LuisAlejandro/spices/badge.svg?branch=develop
   :target: https://coveralls.io/github/LuisAlejandro/spices?branch=develop
   :alt: Coverage

.. image:: https://cla-assistant.io/readme/badge/LuisAlejandro/spices
   :target: https://cla-assistant.io/LuisAlejandro/spices
   :alt: Contributor License Agreement

.. image:: https://readthedocs.org/projects/spices/badge/?version=latest
   :target: https://readthedocs.org/projects/spices/?badge=latest
   :alt: Read The Docs

.. image:: https://img.shields.io/discord/809504357359157288.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2
   :target: https://discord.gg/znATt8TRm2
   :alt: Discord Channel

|
|

.. _full documentation: https://spices.readthedocs.org

Current version: 0.0.3

Spices validates a ``.spices.yml`` file and installs the declared
dependencies using the host's native package manager (apt, yum/dnf, apk,
pacman, portage) or language managers (pip, npm, yarn, bundler), with
optional repositories, GPG keys, post-install hooks, and custom scripts.

For more information, please read the `full documentation`_.

Getting started
===============

Installation
------------

.. _PyPI: https://pypi.org/project/spices

The ``spices`` program is written in python and hosted on PyPI_.
Therefore, you can use pip to install the stable version::

    $ pip install --upgrade spices

If you want to install the development version (not recommended), you can
install directly from GitHub like this::

    $ pip install --upgrade https://github.com/LuisAlejandro/spices/archive/master.tar.gz

Usage
-----

.. _USAGE: https://github.com/LuisAlejandro/spices/blob/develop/USAGE.rst

Create a ``.spices.yml``, then run ``spices install``. See USAGE_ for details
(some legacy sections may lag the current CLI).

Getting help
============

.. _Discord server: https://discord.gg/M36s8tTnYS
.. _StackOverflow: http://stackoverflow.com/questions/ask

If you have any doubts or problems, subscribe to our `Discord server`_ and ask for help. You can also
ask your question on StackOverflow_ (tag it ``spices``) or drop me an email at luis@collagelabs.org.

Contributing
============

.. _CONTRIBUTING: https://github.com/LuisAlejandro/spices/blob/develop/CONTRIBUTING.rst

See CONTRIBUTING_ for details.

Release history
===============

.. _HISTORY: https://github.com/LuisAlejandro/spices/blob/develop/HISTORY.rst

See HISTORY_ for details.

License
=======

.. _AUTHORS: https://github.com/LuisAlejandro/spices/blob/develop/AUTHORS.rst
.. _GPL-3 License: https://github.com/LuisAlejandro/spices/blob/develop/LICENSE

Copyright 2016-2022, Spices Developers (read AUTHORS_ for a full list of copyright holders).

Released under a `GPL-3 License`_.

Made with 💖 and 🍔
====================

.. image:: https://raw.githubusercontent.com/LuisAlejandro/spices/develop/docs/_static/author-banner.svg

.. _LuisAlejandroTwitter: https://twitter.com/LuisAlejandro
.. _LuisAlejandroGitHub: https://github.com/LuisAlejandro
.. _luisalejandro.org: https://luisalejandro.org

|

    Web luisalejandro.org_ · GitHub `@LuisAlejandro`__ · Twitter `@LuisAlejandro`__

__ LuisAlejandroGitHub_
__ LuisAlejandroTwitter_
