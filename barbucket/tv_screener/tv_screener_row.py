from dataclasses import dataclass


@dataclass
class TvScreenerRow():
    ticker: str
    exchange: str
    market_cap: int
    avg_vol_30_in_curr: int
    country: str
    employees: int
    profit: int
    revenue: int
