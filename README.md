### What is Viddit

Viddit is a backend monolith service that automatically creates TikTok style videos from Reddit posts. It automates the process of finding interesting posts to generate content from, generating audio and video, and uploading the results to a Google drive. 
On startup Viddit simply takes a number of config params (subreddits to search, min upvotes etc) and auth config for the relevant services.

Right now Viddit uses GCP to generate the TTS, and the only upload option is Google Drive. GPTs API is used to generate the video metadata.

This project was just for fun and it's unlikely that I maintain it going forward.

If this helped you at all and you want to give back, feel free to: https://www.buymeacoffee.com/jammassey
