Contract details from TV
========================

Additional details to the existing contracts can be added from the free ``tradingview.com`` stock screener

Download
--------
* Go to ``https://www.tradingview.com/chart``
* On the bottom left, open the stock screener panel
* Select a country and set filters as you like
* Set the coulms to:
    * ``Average Volume (30 day)``
    * ``Country``
    * ``Exchange``
    * ``Gross Profit (FY)``
    * ``Market Capitalization``
    * ``Number of Employees``
    * ``Simple Moving Average (30)``
    * ``Total Revenue (FY)``
* Save the coulmn set for convenience
* Download the screener results as ``.csv`` file
* Repeat for other countries if you like

Add to local database
---------------------
* Place all downloaded ``.csv`` files into the folder ``{your_local_user_directory}/.barbucket/tv_screener``. Then execute

.. code-block:: console

    $ barbucket contracts download-tv-details

* For each contract in each file the software will try to find a corresponding contract in your local database and add the screener details.
 
 