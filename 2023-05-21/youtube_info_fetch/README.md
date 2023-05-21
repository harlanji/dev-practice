# YouTube Info Fetch

Given a list of Video IDs, fetch them and store them to a SQLite3 DB cache for 
subsequent fetches.

Store them by authorized user and with a timestamp, so they can be fetched with 
a max age.

## Setup

A YouTube API project with client info stored in `.data/yt-client-secret.json`,
and optionally channel config stured in `.data/session_{channel_id}.json` where
channel_id is configured in `youtube_info_fetch.py` as `AUTH_CHANNEL_ID`.

A template of the format for `.data/session_{channel_id}.json` config 
can be found in `session_sample.json`. It it's not present then it uses app 
level access, which is sufficient.

It doesn't handle login or refresh token, which I think an earlier dev practice 
covered. The credentials is the `flow.credentials` from 
`google_auth_oauthlib.flow.Flow.from_client_secrets_file` after `fetch_token` is 
called.

## Usage

Run `python youtube_info_fetch.py` after setting `video_ids` and optionally `AUTH_CHANNEL_ID` at the top of the file.

Add more video_ids between runs to see cache behavior.

Data is stored in `.data/youtube.db` and can be inspected with any SQLite3 library.

## Dev Practice

This is a dev practice that touches on these themes:

* SQLite3
* Caching
* YouTube API
* Layered Code: Model

It's about the 5th practice I've done where I've broken the code into a "model" 
layer.



