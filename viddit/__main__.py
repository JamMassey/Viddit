import os
import logging
from utils.logging_utils import setup_logger
from core.reddit_scraper import RedditScraper
from core.video_writer import generate_video_from_content
from core.content_upload.youtube_uploader import YoutubeUploader
from core.content_upload.gdrive_uploader import upload_to_google_drive, save_credentials_web_server_login

logger = logging.getLogger(__name__)

NO_COMMENTS = 5
BASE_OUTPUT_DIR = "output"
COMMENT_OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, "comments")
POST_DIR = os.path.join(BASE_OUTPUT_DIR, "post")
POST_AUDIO_DIR = os.path.join(POST_DIR, "audio")
POST_IMAGE_DIR = os.path.join(POST_DIR, "images")
COMMENT_AUDIO_DIR = os.path.join(COMMENT_OUTPUT_DIR, "audio")
COMMENT_IMAGE_DIR = os.path.join(COMMENT_OUTPUT_DIR, "images")
DIRECTORIES = {"post_audio":POST_AUDIO_DIR, "post_image":POST_IMAGE_DIR, "comment_audio":COMMENT_AUDIO_DIR, "comment_image":COMMENT_IMAGE_DIR}
TEMP_OUTPUT_NAME = "temp.mp4"
if __name__ == "__main__":
    setup_logger()
    # reddit_scraper = RedditScraper(DIRECTORIES)
    # no_comments = reddit_scraper.scrape("https://www.reddit.com/r/AmItheAsshole/comments/11u6zm7/aita_for_shaving_my_stepsons_long_hair_without/", NO_COMMENTS)
    # vid_input_list = [f"{POST_IMAGE_DIR}/0.png"]+ [f"{COMMENT_IMAGE_DIR}/{i}.png" for i in range(0, no_comments)]
    # audio_input_list = [f"{POST_AUDIO_DIR}/0.mp3"]+ [f"{COMMENT_AUDIO_DIR}/{i}.mp3" for i in range(0, no_comments)]
    # generate_video_from_content("background.mp4", vid_input_list,audio_input_list, output_name=TEMP_OUTPUT_NAME)
    # youtube_uploader = YoutubeUploader(secrets_file_path='./client_secrets.json')
    # youtube_uploader.authenticate(oauth_path='./oauth.json')
    # options = {
    # "title" : "Test", # The video title
    # "description" : "Example description", # The video description
    # "tags" : ["tag1", "tag2", "tag3"],
    # "categoryId" : "22",
    # "privacyStatus" : "private", # Video privacy. Can either be "public", "private", or "unlisted"
    # "kids" : False, # Specifies if the Video if for kids or not. Defaults to False.
    # "thumbnailLink" : "https://cdn.havecamerawilltravel.com/photographer/files/2020/01/youtube-logo-new-1068x510.jpg" # Optional. Specifies video thumbnail.
    # }
    # youtube_uploader.upload(TEMP_OUTPUT_NAME, options)
    save_credentials_web_server_login()
    upload_to_google_drive(TEMP_OUTPUT_NAME)


