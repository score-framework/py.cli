.. module:: score.cli
.. role:: default
.. role:: confkey

*********
score.cli
*********

This module provides features for conveniently developing command line
interfaces to other modules. It makes use of the excellent click_ library.

.. _click: http://click.pocoo.org


.. _cli_quickstart:

Quickstart
==========

.. note::

    The :ref:`tutorial <tutorial>` provides a more elaborate introduction to
    this module, so check it out if you haven't already.

This example will create a function for listing all initialized modules. We
want it to ba callable as `score modules`.

First, you need a function that handles the logic. We will assume, the next
function is in the python module `beekeeper`:

.. code-block:: python

    from random import randint

    @click.group
    @click.pass_context
    def main(clickctx):
        """
        Lists all configured modules
        """
        score = clickctx.obj['conf'].load()
        for module in score._modules:
            print(module)
            if randint(1, 10) == 1:
                print('shhhh!')


The only other thing you need is an `entry point`_ declaration in your
package's *setup.py*:

.. code-block:: python

    setup(
        # ... some other stuff
        entry_points={
            'score.cli': [
                'modules = beekeeper:main',
            ],
        },
        # ... potentially more stuff
    )

.. _entry point: http://pythonhosted.org/setuptools/pkg_resources.html#entry-points


.. _cli_configuration:

Configuration
=============

This is one of the few modules, that have no initializer: It is just here for
taking care of shell commands.


Details
=======

CLI Command Aggregation
-----------------------

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
------------------------

Another feature provided by this module is easy management of configuration
files for command line applications: we assume that you initialize score using
the same configuration file most of the time. You can manage your
configurations using the ``conf`` subcommand:

.. code-block:: console

    $ score conf list
    spam
    cheeseshop *

This command will give you a list of available configurations in your current
environment. The asterisk indicates that *cheeseshop* is the default
configuration, i.e. will be used implicitly, if you don't specify an alternate
configuration explicitly.

You can add further configurations to this list using the ``conf`` subcommand:
Setting a value is as simple as calling the appropriate CLI command:

.. code-block:: console

    $ score conf add sketches/parrot.conf
    $ score conf list
    spam
    cheeseshop *
    parrot

This command will register the given file under the name *parrot* (the filename
without its extension). It is possible to store the file under a different name
by passing a ``--name`` parameter. You can also pass the ``--paths`` option to
display the
location of each file:

.. code-block:: console

    $ score conf remove parrot
    $ score conf add --name birdie sketches/parrot.conf
    $ score conf setdefault spam
    $ score conf list --paths
    spam * (/home/sirlancelot/sketches/parrot.conf)
    cheeseshop   (/home/sirlancelot/sketches/cheeseshop.conf)
    birdie   (/home/sirlancelot/sketches/parrot.conf)

Initializing SCORE
------------------

All command line applications can access the score configuration file in
click's context object. Performing a sketch through the CLI might be
implemented the following way:

.. code-block:: python

    @click.group('sketch')
    def sketch():
        pass

    @sketch.command
    @click.pass_context
    def perform(clickctx):
        score = clickctx.obj['conf'].load()
        score.sketch.perform()

.. code-block:: console

    $ score conf list
    spam *
    cheeseshop
    birdie
    $ score sketch perform
    Spam, Spam, Spam, lovely Spam
    Wonderful Spam, Lovely Spam.
    Spam, Spam, Spam, magnificent Spam,
    ...
    $ score -c birdie sketch perform
    Mr. Praline: 'Ello, I wish to register a complaint.
    Mr. Praline: 'Ello, Miss?
    Owner: What do you mean "miss"? 
    ...

.. _score_cli_config_locations:

Configuration Locations
-----------------------

All your configuration files are stored in your a folder called ``.score`` in
your home folder. Developers may make use of various :ref:`helper functions
<score_cli_helpers>` provided by this modules to store various configurations.
The configuration files, as described above, are in a sub-folder called
``conf``:

.. code-block:: console
    
    $ ls ~/.score/conf
     __default__  __global__

The ``__global__`` configuration file will *always* be evaluated, whereas the
``__default__`` configuration is merely a pointer to your current
configuration. The other files are those you configured yourself.

Usually, though, this folder just contains the ``__global__`` and
``__default__`` configuration. The reason is that any configuration files you
register while inside a :ref:`virtual environment <python:venv-def>` are
registered in a different folder: the root folder of the currently active
virtual environment:

.. code-block:: console
    
    (sketches)$ ls $VIRTUAL_ENV/.score/conf
    birdie  cheeseshop  __default__  spam


.. _score_cli_helpers:

API
===

.. autofunction:: score.cli.conf.venv_root

.. autofunction:: score.cli.conf.rootdir

.. autofunction:: score.cli.conf.add

.. autofunction:: score.cli.conf.remove

.. autofunction:: score.cli.conf.make_default

.. autofunction:: score.cli.conf.get_file

.. autofunction:: score.cli.conf.get_default

.. autofunction:: score.cli.conf.name2file

.. autofunction:: score.cli.conf.global_file

.. autofunction:: score.cli.conf.default_file

.. autofunction:: score.cli.conf.get_origin
