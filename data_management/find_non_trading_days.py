from tinydb import TinyDB, Query
import pandas as pd
from tqdm import tqdm
import datetime



def update_ntd_list(exchange):
    """
    Description
    """
    
    #Get all contracts
    contracts_db = TinyDB('data_management/contracts_db.json')
    my_query = Query()
    all_instruments = contracts_db.search(my_query.Exchange == exchange)
    contracts_db.close()

    # Build initial list of dates
    start = datetime.datetime(2008, 1, 1)
    end = datetime.datetime(2019, 12, 31)
    dt_index = pd.bdate_range(start, end)
    init_vals = dt_index.strftime('%Y-%m-%d').values
    all_days = pd.Series(init_vals)
    
    # Append dates of all existing candlesticks to dates list
    for instrument in tqdm(all_instruments[:10]):
        if not instrument['Status'].startswith('data_ends'):
            continue
        filename = ('/Users/martin/Google Drive/data/screener/' + instrument['Symbol'] + '_' + exchange + '.csv')
        df_histo = pd.read_csv(filename)
        all_days = all_days.append(df_histo['date'])
        
    # Filter dates where no instrument was traded
    counts = all_days.value_counts()
    counts = counts.sort_index()
    while counts.iloc[0] == 1: # Drop trailing no-data dates
        counts = counts.drop(counts.index[0])
    while counts.iloc[-1] == 1: # Drop leading no-data dates
        counts = counts.drop(counts.index[-1])
    counts = counts.drop(counts[counts!=1].index)

    return counts


if __name__ == '__main__':
    print(update_ntd_list('FWB'))


