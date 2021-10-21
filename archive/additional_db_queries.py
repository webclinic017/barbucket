######
# Additional db queries, for manual use only
######

# Change data type of column in table without dependencies
######
"""
CREATE TABLE contract_details_tw_temp AS
    SELECT
		contract_id,
		CAST (market_cap AS INTEGER) AS market_cap,
		avg_vol_30_in_curr,
		country,
		employees,
		profit,
		revenue
	FROM contract_details_tw;

CREATE TABLE contract_details_tw (
	contract_id INTEGER,
	market_cap INTEGER,
	avg_vol_30_in_curr INTEGER,
	country TEXT,
	employees INTEGER,
	profit INTEGER,
	revenue INTEGER,
	FOREIGN KEY (contract_id)
	    REFERENCES contracts (contract_id)
	        ON UPDATE CASCADE
	        ON DELETE CASCADE,
	UNIQUE (contract_id));

INSERT INTO	contract_details_tw 
	SELECT * FROM contract_details_tw_temp;

DROP TABLE contract_details_tw_temp;
"""


# Create a new universe
# Todo: Remove duplicates on multiple exchanges
######
"""
INSERT INTO universe_memberships (contract_id, universe)
	SELECT contract_id, 'stocks_germany'
		FROM all_contract_info
		WHERE (
			(contract_type_from_details IN ('COMMON'))
			AND
			(exchange IN ('IBIS', 'FWB'))
			AND
			(exchange = primary_exchange)
			AND
			(country = 'Germany')
		)
		ORDER BY market_cap DESC 
		LIMIT 1000
"""


# Find ETFs, listed only as ETF (or as STOCK)
######
"""
select exchange_symbol
from all_contract_info
where (
	(exchange = 'FWB')
	and
	(contract_type_from_details in ('ETF', 'ETC', 'ETN', 'ETP'))
	and
	(contract_type_from_listing = 'STOCK')
	and
	(exchange_symbol not in (
		select exchange_symbol
		from all_contract_info
		where (
			(exchange = 'FWB')
			and
			(contract_type_from_details in ('ETF', 'ETC', 'ETN', 'ETP'))
			and
			(contract_type_from_listing = 'ETF')
		)
	))
)
"""


# manually delete contracts and clean dependent tables (Sqlite contraints/pragma are complicated)
######
"""
delete from contracts where contract_type_from_listing = 'ETF';

delete
	from (
		contract_details_ib,
		contract_details_tv,
		quotes,
		quotes_status,
		universe_memberships
	)
	where contract_id NOT IN (
		select contract_id
			from contracts
	);
"""
