from dataclasses import dataclass
from typing import Optional


@dataclass
class TvScreenerRow():
    ticker_symbol: str
    exchange: str
    country: str
    market_cap: Optional[int]
    avg_vol_30_in_curr: Optional[int]
    employees: Optional[int]
    profit: Optional[int]
    revenue: Optional[int]
