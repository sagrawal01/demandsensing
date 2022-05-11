import pandas as pd
import sys
from sqlalchemy.engine import url as sa_url
from sqlalchemy import create_engine

from cryptography.fernet import Fernet
import json

def decrypt(input_file, key_file):
    with open (key_file, 'rb') as k:
        key=k.read()
    with open (input_file, 'rb') as f:
        data = f.read()

    fernet=Fernet(key)
    decrypted = fernet.decrypt(data)
    config=json.loads(decrypted)

    return config

def getapodata():
    credentials=decrypt('../config/encrypted', '../config/key.txt')
    db_connect_url = sa_url.URL(
        drivername=credentials['drivername'],
        username=credentials['username'],
        password=credentials['password'],
        host=credentials['host'],
        port=credentials['port'],
        database=credentials['database'],
    )
    query='''select * from mv_demand_historical where "Country key" = '{country}' and "Product" = '{product}';'''.format(country=sys.argv[1], product=sys.argv[2])

    conredshift=create_engine(db_connect_url)
    data = pd.read_sql_query(query, conredshift)
    data=data[['Country key','Product','Product Name','Calendar year / week','Cal. year / month', 'Demand']]
    data.columns=["Country","Product_Key", "Product_Name","Week","Month", "Demand"]
    return data

def getcomdata(input_file):
    data=pd.read_excel(input_file, engine='openpyxl', sheet_name='Sheet1')
    data=data[data['NDC #']==int(sys.argv[3])]
    return data
