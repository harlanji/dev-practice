import os

import json

import db_model
import youtube_model
import model

AUTH_CHANNEL_ID = None
"""
Set to None to use app level access.

Data fetched without credentials can be more liberally cached and shared among accounts.

See session_sample.json for the format.
"""

def main ():
    if not os.path.exists('.data'):
        os.mkdir('.data')
    
    if not os.path.exists('.data/yt-client-secret.json'):
        print('.data/yt-client-secret does not exist. load it up with your youtube client config')
        exit(-1)
    
    db_path = db_model.DB_PATH
    db_model.init_db( db_path )
    
    if not AUTH_CHANNEL_ID:
        print('using app level access')
    
    youtube_user = youtube_model.get_youtube_user(AUTH_CHANNEL_ID)
    
    if AUTH_CHANNEL_ID and not youtube_user:
        print('could not load auth for configured channel. exiting.')
        exit(-1)
    
    
    video_ids = [
        'Z6ih1aKeETk',
        'vE-ViyPXj4Q',
        'jfKfPfyJRdk',
        '5d7e9lj8BQw',
        '_sSBKm-CDNU'
    ]
    
    
    vid_infos = model.get_video_infos(video_ids, youtube_user=youtube_user, db_path=db_path)
    
    print(f'got videos, count={len(vid_infos)}')
    #print(json.dumps(vid_infos, indent=2))

if __name__ == '__main__':
    main()