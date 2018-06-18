from sqlalchemy import *
DB_EXISTS = True

metadata = MetaData(db)

heartbeats = Table('heartbeats', metadata,
    Column('client_id', Integer, primary_key=True),
    Column('client_name', String),
    Column('last_ping', DateTime))
if not DB_EXISTS:
    heartbeats.create()

