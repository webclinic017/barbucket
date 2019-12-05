from tinydb import TinyDB, Query
import pandas as pd
from tqdm import tqdm
import datetime



def update_ntd_list(exchange):
    """
    Description

    exchange: string symbol of exchange, eg. 'FWB'
    """

    #Get all contracts
    contracts_db = TinyDB('data_management/contracts_db.json')
    my_query = Query()
    all_instruments = contracts_db.search(my_query.Exchange == exchange)
    contracts_db.close()

    # Build initial list of dates
    start = datetime.datetime(2008, 1, 1)
    end = datetime.datetime(2025, 12, 31)
    dt_range = pd.bdate_range(start, end)
    all_days = dt_range.strftime('%Y-%m-%d').tolist()

    # Append dates of all existing candlesticks to dates list
    for instrument in tqdm(all_instruments):
        if not instrument['Status'].startswith('data_ends'):
            continue
        filename = ('/Users/martin/Google Drive/data/screener/' \
            + instrument['Symbol'] + '_' + exchange + '.csv')
        df_histo = pd.read_csv(filename)
        all_days.extend(df_histo['date'].tolist())

    # Filter dates where no instrument was traded
    days_series = pd.Series(all_days)
    counts = days_series.value_counts()
    counts = counts.sort_index()
    while counts.iloc[0] == 1: # Drop trailing no-data dates
        counts = counts.drop(counts.index[0])
    while counts.iloc[-1] == 1: # Drop leading no-data dates
        counts = counts.drop(counts.index[-1])
    counts = counts.drop(counts[counts!=1].index)

    return counts


if __name__ == '__main__':
    exchanges = ['FWB', 'IBIS', 'LSE', 'LSEETF']
    for exchange in exchanges:
        series = update_ntd_list(exchange)
        series.to_csv(f'./data_management/non_trading_days/{exchange}.csv', \
            columns=[])


