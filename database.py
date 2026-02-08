#from main import insert_begin, insert_end, play_next, play_prev, song_pointer, delete_song, display, curr_song
import sqlalchemy as db
#from sqlalchemy.orm import sessionmaker

engine = db.create_engine('sqlite:///songslist.db')
conn = engine.connect()

metadata = db.MetaData()

Songs = db.Table(
    "songs", metadata,
    db.Column('id', db.Integer(), primary_key = True),
    db.Column('name', db.String(50), nullable = False)
)

metadata.create_all(engine)

def insert_song_db (song_name):
    insert_statement = db.insert(Songs).values(name=song_name)
    result = conn.execute(insert_statement)
    conn.commit()
    return result.inserted_primary_key[0]

def delete_song_db (song_id):
    delete_statement = db.delete(Songs).where(Songs.c.id == song_id)
    result = conn.execute(delete_statement)
    conn.commit()

def delete_all ():
    delete_statement = db.delete(Songs)
    result = conn.execute(delete_statement)
    conn.commit()