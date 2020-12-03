Local database
==============

All data is stored in a local SQLite database. The file is located at

.. code-block:: console

    your/local/user_directory/.barbucket/database.db

Database reset
--------------

You can delete all data by resetting the database

.. code-block:: console

    python barbucket databse reset

The previously existing database will be stored as a backup in the same directory.
