/* ##########
Additional db queries for manual use
########## */


/* ##########
Change view for all contract data 
########## */
create view contracts_all_data as
select 
	contracts.*, 
	contract_details_ib.stock_type, contract_details_ib.primary_exchange, contract_details_ib.industry, contract_details_ib.category, contract_details_ib.subcategory,
	contract_details_tv.market_cap, contract_details_tv.avg_vol_30_in_curr, contract_details_tv.country, contract_details_tv.employees, contract_details_tv.profit, contract_details_tv.revenue 
from contracts
left OUTER JOIN contract_details_ib ON contracts.id = contract_details_ib.contract_id
left OUTER JOIN contract_details_tv ON contracts.id = contract_details_tv.contract_id


/* ##########
SQLite: Change data type of column in table without dependencies 
########## */
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


/* ##########
Create a new universe
########## */
INSERT INTO universe_memberships (contract_id, universe)
	SELECT id, 'US_COMMON_STOCKS_TOP_3000'
		FROM contracts_all_data
		WHERE (
			(stock_type IN ('COMMON_STOCK'))
			AND
			(exchange IN ('NASDAQ', 'NYSE', 'ARCA'))
			--AND
			--(exchange = primary_exchange)
			AND
			(country IN ('United States'))
		)
		ORDER BY market_cap DESC 
		LIMIT 3000
		;


/* ##########
Find ETFs, listed only as ETF (or as STOCK)
########## */
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


/* ##########
manually delete contracts and clean dependent tables (Sqlite contraints/pragma are complicated)
########## */
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
