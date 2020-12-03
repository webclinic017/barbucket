Sync exchange listings
======================

You can sync your local listing of available contracts to IB's exchange listing.

.. code-block:: console

    python barbucket.py contracts sync_listing --type STOCK --exchange NYSE

--type      can be ``STOCK`` or ``ETF``
--exchange  can be the code for any exchange available on IB

| Syncing actually means, that:
| - exchange contracts, that do not exist in your local database, will be added
| - local contracts, that do not exist in the exchange listing, will be deleted locally
