Configuration
#############

Grascii provides a user-level configuration file to set the defaults for its
tools.

Getting Started
***************

Create a configuration file with the following command::

  $ grascii config init <preset>

where ``<preset>`` is one of:

- ``preanniversary``: Uses the ``:preanniversary`` and
  ``:preanniversary-phrases`` dictionaries for search
- ``anniversary``: Uses the ``:anniversary`` dictionary for search

Locate the file with::

  $ grascii config path

Editing the Configuration
*************************

To change the defaults, open the generated configuration file
and make your desired changes. The available options are described
in the starter file:

.. include:: ../grascii/defaults.conf
   :code:
