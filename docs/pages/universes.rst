Universes
=========

To conveniently handle the contracts, you can group them to universes.

Listing all existing universes
------------------------------
.. code-block:: console

    python barbucket.py universes list

Creating a new universe
-----------------------
.. code-block:: console

    python barbucket.py universes create --name my_universe --contract_ids 1,2,3

--name             Name of the universe to create
--contract_ids     The ``contracts_ids`` are automatically assigned to the contracts by the software on their creation and need to be obtained manually from the database.

Getting all members of a universe
---------------------------------
.. code-block:: console

    python barbucket.py universes members --name my_universe

--name             Name of the universe to get the members for

Deleting a universe
-------------------
.. code-block:: console

    python barbucket.py universes delete --name my_universe

--name             Name of the universe to delete
