import youtube_model
import db_model

def get_video_infos (video_ids, youtube_user, db_path):
    """
    Get YouTube video info from the cache DB if we have it, fetching and storing anything we don't already have.
    
    Fetches up to 50 videos due to API limitations and the fact we don't code to handle more.
    
    Is auth aware; returns videos fetched with the app key or auth_user_id.
    """
    auth_user_id = None
    if youtube_user:
        auth_user_id = youtube_user['id']
    
    vid_infos = db_model.load_video_infos(video_ids, auth_user_id, db_path=db_path)
    
    loaded_video_ids = set(map(lambda vid_info: vid_info['id'], vid_infos))
    
    fetch_video_ids = list(set(video_ids) - loaded_video_ids)
    
    if fetch_video_ids:
        print(f'get_video_infos: fetching videos: {fetch_video_ids}')
        fetched_vid_infos = youtube_model.fetch_video_infos(fetch_video_ids, youtube_user=youtube_user)
        
        print(f'get_video_infos: fetched videos, length={len(fetched_vid_infos)}')
        
        db_model.store_video_infos(fetched_vid_infos, auth_user_id=auth_user_id, db_path=db_path)
        
        vid_infos += fetched_vid_infos
    
    
    return vid_infos