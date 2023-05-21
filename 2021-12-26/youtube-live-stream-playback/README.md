# YouTube Live Stream Playback Demo

Uses Mozilla WebVTT to playback captions and chat  for a video in sync.

Does not include the player or any data.

## Usage

* Fetch a VTT file from YouTube using the Captions API or YouTubeDL.
* Fetch a chat transcript via `youtube-chat-downloader` or match its format with an API script.
* Configure the locations in `index.html` toward the bottom
* May require a local webserver, eg. `python -m http.server`

## Dev Practice

* Mozilla WebVTT
* Consurrently playing back streams of events against wall time
