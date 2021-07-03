import configparser
from pathlib import Path


__parser = configparser.ConfigParser(allow_no_value=True)
__default_config = {
    'database': {
        '\# db location within current users home folder': '',
        'db_location': ".barbucket/database.db"},
    'contracts': {},
    'quotes': {
        'redownload_days': "5"},
    'quality_check': {
        'min_quotes_count': "250",
        'max_missing_quotes_at_end': "4",
        'max_gap_size': "4"},
    'tws_connector': {
        'non_systemic_codes': "162,200,354,2104,2106,2158",
        'ip': "127.0.0.1",
        'port': "7497",
        '\# 7497 tws paper, 4002/4003 ibg paper/real': '', 
        '\# Minimum number of business days until new download is started': "5"}}


# Create file if not present and fill with default values
def init_config_file():
    path = Path.home()
    if not Path.is_dir(path / ".barbucket"):
        Path.mkdir(path / ".barbucket")
    
    if not Path.is_dir(path / ".barbucket/tw_screener"):
        Path.mkdir(path / ".barbucket/tw_screener")
    
    path = path / ".barbucket/config.ini"
    __parser.read_dict(__default_config)
    with open(path, 'w') as file:
        __parser.write(file)


# Read values from file 
def get_config_value(section, option):
    path = Path.home() / ".barbucket/config.ini"

    if not Path.is_file(path):
        init_config_file()

    __parser.read(path)
    value = __parser.get(section, option)
    
    #If value contains comma, split by comma and change to list
    if "," in value:
        value = value.split(",")

    return value
    

