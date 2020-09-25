class Tools():

    def __init(self,):
        pass


    @staticmethod
    def remove_special_chars(input_string):
        special_chars = ["'"]
        result = input_string
        for char in special_chars:
            result = result.replace(char, '')
        return result


    def encode_exchange(self, exchange):
        exchange_codes = {
            'NASDAQ': "ISLAND",     # NASDAQ / Island
            'ISLAND': "ISLAND",     # NASDAQ / Island
            'NYSE': "NYSE",         # NYSE
            'ARCA': "NYSE ARCA",    # Archipelago
            'AMEX': "AMEX",         # American Stock Exchange
            'BATS': "BATS",         # Better Alternative Trading System

            'VSE': "VSE",           # Vancouver Stock Exchange

            'FWB': "FWB",           # Frankfurter Wertpapierbörse
            'IBIS': "XETR",         # XETRA
            'SWB': "SWB",           # Stuttgarter Wertpapierbörse

            'LSE': "LSE",           # London Stock Exchange
            'LSEETF': "LSEETF",     # London Stock Exchange: ETF

            'SBF': "SBF"}           # Euronext France

        return exchange_codes[exchange]


    def decode_exchange(self, exchange):
        exchange_codes = {
            'ISLAND': "NASDAQ",     # NASDAQ / Island
            'NASDAQ': "NASDAQ",     # NASDAQ / Island
            'NYSE': "NYSE",         # NYSE
            'NYSE ARCA': "ARCA",    # Archipelago
            'AMEX': "AMEX",         # American Stock Exchange
            'BATS': "BATS",         # Better Alternative Trading System

            'VSE': "VSE",           # Vancouver Stock Exchange

            'FWB': "FWB",           # Frankfurter Wertpapierbörse
            'XETR': "IBIS",         # XETRA
            'SWB': "SWB",           # Stuttgarter Wertpapierbörse

            'LSE': "LSE",           # London Stock Exchange
            'LSEETF': "LSEETF",     # London Stock Exchange: ETF

            'SBF': "SBF"}           # Euronext France

        return exchange_codes[exchange]