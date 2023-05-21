import json

import sqlite3

DB_PATH = '.data/youtube.db'

def init_db ( path = DB_PATH ):
    db = sqlite3.connect(path)
    
    cur = db.cursor()
    
    table_exists = cur.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='youtube_videos'").fetchone()[0]
    
    if not table_exists:
        
        print(f'creating DB {path}')
        
        cur.execute("""
            create table youtube_videos (
                id text,
                ts timestamp default current_timestamp,
                auth_user_id text,
                data blob
            )
        """)
        
        cur.connection.commit()
    
    cur.close()

def store_video_infos (vid_infos, auth_user_id=None, db_path=DB_PATH):
    db = sqlite3.connect(db_path)
    
    cur = db.cursor()
    
    for vid_info in vid_infos:
        video_id = vid_info['id']
        cur.execute("""
            INSERT INTO youtube_videos (id, auth_user_id, data) VALUES(?,?,?)
        """, [video_id, auth_user_id, json.dumps(vid_info, indent=2)])
        
    cur.connection.commit()
    cur.close()


def load_video_infos (video_ids, auth_user_id=None, db_path=DB_PATH):
    db = sqlite3.connect(db_path)
    
    cur = db.cursor()
    
    params = [auth_user_id] + video_ids
    values_sql = ','.join(['?'] * (len(video_ids)))
    
    yt_video_rows = cur.execute(f"""
            SELECT data 
            FROM youtube_videos 
            WHERE 
                (auth_user_id = ? or auth_user_id is null)
                and id IN ({values_sql})
        """, params).fetchall()
        
    cur.close()
    
    vid_infos = list(map(lambda row: json.loads(row[0]), yt_video_rows))
    
    return vid_infos