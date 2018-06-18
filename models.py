from sqlalchemy import *
DB_EXISTS = True

metadata = MetaData()

nodes_table = Table('nodes_table', metadata,
    Column('client_id', Integer, primary_key=True),
    Column('client_name', String),
    Column('last_ping', DateTime),
    Column('out_val', String))
