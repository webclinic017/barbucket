# Data migration code collection
# For manual use only

"""
/* Change data type of column in table without dependencies */

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