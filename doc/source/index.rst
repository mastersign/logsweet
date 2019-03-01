.. logsweet documentation master file.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to logsweet's documentation!
===========================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/core
   modules/config
   modules/colors
   modules/watch
   modules/net
   modules/mock

CLI Usage
---------

.. click:: logsweet.cli:main
    :prog: logsweet

.. click:: logsweet.cli:watch
    :prog: logsweet watch

.. click:: logsweet.cli:listen
    :prog: logsweet listen

.. click:: logsweet.cli:proxy
    :prog: logsweet proxy

.. click:: logsweet.cli:mock
    :prog: logsweet mock


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
