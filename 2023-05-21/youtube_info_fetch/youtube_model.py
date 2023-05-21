import os

import json

import google.oauth2.credentials
import googleapiclient.discovery

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

VIDEO_PARTS = 'snippet,contentDetails,liveStreamingDetails,statistics,recordingDetails'.split(',')


def get_youtube_builder (youtube_user = None):
    
    if youtube_user:
        
        credentials = google.oauth2.credentials.Credentials(
          **youtube_user['credentials'])
        
        youtube = googleapiclient.discovery.build(
          API_SERVICE_NAME, API_VERSION, credentials=credentials)
    else:
        print('using developer key for YT api')
        
        developer_key = os.environ.get('GOOGLE_DEVELOPER_KEY')
        youtube = googleapiclient.discovery.build(
          API_SERVICE_NAME, API_VERSION, developerKey=developer_key) 
    
    return youtube

def get_youtube_user (channel_id):
    session_path = f'.data/session_{channel_id}.json'
    if os.path.exists(session_path):
        with open(session_path, 'rt', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f'No config for channel {channel_id}')
        return None

def fetch_video_infos (video_ids, video_parts=VIDEO_PARTS, max_results=50, youtube_user=None):
    youtube = get_youtube_builder(youtube_user)
    
    # FIXME add pagination
    if len(video_ids) > max_results or max_results > 50:
        raise Exception('requesting more videos than max results or supported and pagination is not supported.')
    
    videos = youtube.videos().list(id=video_ids,
        part=','.join(video_parts),
        maxResults=max_results
        ).execute()
    
    return videos['items']