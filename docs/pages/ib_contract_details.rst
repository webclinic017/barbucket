Contract details from IB
========================

For all locally existing contracts, additional information can be downloaded from IB over the TWS

.. code-block:: console

    python barbucket.py contracts fetch_ib_details

The provided information is about contract type and contract sector and will be stored to the local database.

As none of IB's speedlimits applies for downloading contract details, this operation is quite fast, even for a large ammount of contracts.
