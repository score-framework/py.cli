.. module:: score.cli
.. role:: faint
.. role:: confkey

*********
score.cli
*********

Introduction
============

This module provides features for conveniently developing command line
interfaces to other modules. It makes use of the excellent click_ library and
currently provides two separate features for supporting CLI development:
command aggregation and configuration management.

.. _click: http://click.pocoo.org


CLI Command Aggregation
=======================

This module allows exposing a command line interface and grants access to all
such exposed interfaces via a command line application called ``score``. If a
module called ``foo`` allows clearing its cache via CLI, this feature might be
available via the following console command:

.. code-block:: console

    $ score foo clear-cache

Every module may register a :class:`click.Command` in its ``setup.py`` using
setuptools' formidable feature for `Dynamic Discovery of Services and
Plugins`_. The ``foo`` module just needs to add these lines to its
``setup.py`` to expose the :class:`click.Command` called ``main`` in the
package ``foo.cli``:

.. code-block:: python

    from setuptools import setup, find_packages
    setup(
        # ...
        entry_points={
            'score.cli': [
                'foo = foo.cli:main',
            ]
        },
        # ...

.. _Dynamic Discovery of Services and Plugins: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins

.. _cli_configuration_management:

Configuration Management
========================

Another feature provided by this module is easy management of configuration
files for command line applications. If your CLI application needs the path to
a configuration file for every command, for example, you might want to put the
path to that file in a configuration file so you don't have to provide it on
every command.

Two steps are needed to achieve this: setting a configuration value, and
reading the value programmatically.

Setting Values
--------------

Setting a value is as simple as calling the appropriate CLI command:

.. code-block:: console

    $ score config set foo autoclear_cache true

This command will create a folder called ``.score`` in your home directory and
write the configuration file ``score.ini`` in that folder which will have the
following content::

    [foo]
    autoclear_cache = true

*However*, if you are inside a :ref:`virtual environment <python:venv-def>`,
the configuration will not be written to the ``.score`` folder in your home
directory, but into another folder with the same name residing in the root
folder of your virtual environment. So if you are running in a virtual
environment called ``bar``, which resides in the folder ``~/.virtualenvs/bar``,
the file will be created as ``~/.virtualenvs/bar/.score/score.ini``.

You can instruct the command to write to your home directory instead, by
passing the ``--global`` flag:

.. code-block:: console

    $ score config set --global foo autoclear_cache true

Reading Values
--------------

The easiest way to list all available configuration values is via the command
line:

.. code-block:: console

    $ score config list

This will aggregate all configuration values that were defined within the
virtual environment, and those in your home folder and present them as a single
virtual config file. The exact same can be achieved programmatically:

.. autofunction:: score.cli.config.config

Generic Config Files and Folders
--------------------------------

For those rare cases, where a simple key-value storage is not enough to
configure an application, one may also make use of the more generic functions
for creating/retrieving configuration files and folders:

.. autofunction:: score.cli.config.config_file

.. autofunction:: score.cli.config.config_folder

Autocompletion
==============

It is possible to install autocompletion for all registered sub-commands in
``bash`` or ``zsh`` by executing the following command:

.. code-block:: console

    $ score autocomplete install-bash
    # or
    $ score autocomplete install-zsh

After opening a new shell, you will be able to make use of this feature:

.. code-block:: console

    $ score <tab><tab>
    autocomplete  config        foo
    $ score foo <tab>
    $ score foo clear-cache

