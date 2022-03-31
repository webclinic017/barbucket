# Databases
All data is stored in a SQL database of your choice. Available are all databases supported by the [SqlAlchemy ORM](https://docs.sqlalchemy.org/en/14/dialects/).

## SQLite
- [SQLite](https://www.sqlite.org/) is the default option.
- The file is located at `~/.barbucket/database.sqlite`.
- If no database file exists, it will automatically be created on application start.
- You can set the name of the file within the [config file](configuaration.md).

## PostgreSQL
- You can also use a [PostgreSQL](https://www.postgresql.org) database.
- See the [config file](configuaration.md) for the corresponding connection parameters and change them to comply with your database.
- You can also use the provided [shellscript](https://github.com/croidzen/barbucket/blob/master/resources/docker_run_postgres.sh) to run a PostgreSQL container. This will also check for an available Docker engine, download the image, and create volume and container if necessary.
- Another [shellscript](https://github.com/croidzen/barbucket/blob/master/resources/backup_postgres.sh) is available to backup a PostgreSQL database.

## Other DBMS
- Other available databases are [Microsoft SQL Server](https://www.microsoft.com/en-us/sql-server/), [MySql](https://www.mysql.com), [Oracle](https://www.oracle.com/database/), etc.
- These are not tested but should be working out of the box, as they are supported by the ORM. Please use the [config file](configuaration.md) to set up Barbucket to connect to these databases.

## Direct SQL access
- Some operations are best performed by directly accessing the database. For these, please use the SQL client of your choice, eg. [DBeaver](https://dbeaver.io).
- Some queries that I found useful, are collected in a [file](https://github.com/croidzen/barbucket/blob/master/resources/manual_db_queries.sql) within the repository, Feel free to use them.