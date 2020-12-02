Quotes downloading
==================

To download historical quotes, IB's TWS needs to be running and API access enabled.

Then execute
  ``python barbucket quotes fetch --universe my_universe``

* Right now, only daily quotes are supported
* Start-date will always be today
* Duration will be 15 years or shorter, if latest existing quote is newer
* Some adjustments to the process can be changed in the ``config.ini`` at
  ``your/local/user_directory/.barbucket/config.ini``
* IB is enforcing strict speedlimits, so downloading quotes on IB for many contracts will need some time.

