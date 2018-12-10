from sqlalchemy import *

metadata = MetaData()

nodes_table = Table(
    "nodes_table",
    metadata,
    Column("client_id", Integer, primary_key=True),
    Column("client_name", String),
    Column("last_ping", DateTime),
    Column("out_val", String),
)

game_state_table = Table(
    "game_state_table",
    metadata,
    Column("game_state_id", Integer, primary_key=True),
    Column("game_state_name", String),
    Column("status", Integer),
)

gameroom_table = Table(
    "gameroom_table",
    metadata,
    Column("gameroom_id", Integer, primary_key=True),
    Column("hint_text", String),
    Column("hint_exists", Boolean),
    Column("hint_timer", Integer),
    Column("start_time", Integer),
    Column("end_time", Integer),
    Column("paused", Boolean),
    Column("gamestate", String),
)
