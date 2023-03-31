# TODO
import json
import logging
import os
from selenium.webdriver.remote.remote_connection import LOGGER
from viddit.core.content_upload.gdrive_uploader import upload_to_google_drive
from viddit.core.mongo import initialise_db
from viddit.core.reddit_scraper import RedditPostImageScraper, SubRedditInfoScraper
from viddit.core.video_writer import generate_video_from_content
from viddit.utils.args_utils import parse_args
from viddit.utils.logging_utils import setup_logger
from viddit.core.metadata import GPTMetadata
from viddit.core.tts import GoogleCloudTTS

logger = logging.getLogger(__name__)
logging.getLogger("gtts").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("praw").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)

BASE_OUTPUT_DIR = os.path.join("output")
COMMENT_OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, "comments")
POST_DIR = os.path.join(BASE_OUTPUT_DIR, "post")
POST_AUDIO_DIR = os.path.join(POST_DIR, "audio")
POST_IMAGE_DIR = os.path.join(POST_DIR, "images")
COMMENT_AUDIO_DIR = os.path.join(COMMENT_OUTPUT_DIR, "audio")
COMMENT_IMAGE_DIR = os.path.join(COMMENT_OUTPUT_DIR, "images")
DIRECTORIES = {
    "post_audio": POST_AUDIO_DIR,
    "post_image": POST_IMAGE_DIR,
    "comment_audio": COMMENT_AUDIO_DIR,
    "comment_image": COMMENT_IMAGE_DIR,
}
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), "resources", "background.mp4")
REDDIT_CREDS_PATH = os.path.join(os.path.dirname(__file__), "resources", "reddit_credentials.json")
OPENAI_CREDS_PATH = os.path.join(os.path.dirname(__file__), "resources", "gpt_key.json")
OUATH_CREDS_PATH = os.path.join(os.path.dirname(__file__), "resources", "oauth.json")
CLIENT_SECRETS_PATH = os.path.join(os.path.dirname(__file__), "resources", "client_secrets.json")
CHROME_DRIVER_PATH = os.path.join(os.path.dirname(__file__), "resources", "chromedriver")  # Dockerfile dictates where this is
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(__file__), "resources", "tts_key.json")  # Dockerfile dictates where this is

TEMP_OUTPUT_NAME = "output"

from pydrive.auth import GoogleAuth

GoogleAuth.DEFAULT_SETTINGS["client_config_file"] = CLIENT_SECRETS_PATH


def main():
    args = parse_args()
    reddits = args.subreddits.split("|")
    setup_logger(level=args.log_level, stream_logs=args.console_log)
    reddit_creds = json.load(open(REDDIT_CREDS_PATH))
    metadata_generator = GPTMetadata(OPENAI_CREDS_PATH)
    if args.local_mode:
        db = None
        connection_status = False
    else:
        db, connection_status = initialise_db()
        if not connection_status:
            logger.error("Could not connect to MongoDB")
            raise Exception("Could not connect to MongoDB")
        
    tts_module = GoogleCloudTTS(SERVICE_ACCOUNT_PATH)

    subreddit_scraper = SubRedditInfoScraper(
        reddit_creds["client_id"],
        reddit_creds["client_secret"],
        reddit_creds["password"],
        reddit_creds["user_agent"],
        reddit_creds["username"],
    )
    comment_image_scraper = RedditPostImageScraper(DIRECTORIES,tts_module, CHROME_DRIVER_PATH, operating_sys=args.operating_sys)
    for i in range(len(reddits)):
        try:
            posts = subreddit_scraper.get_subreddit_info(
                reddits[i],
                limit=args.max_vids_per_subreddit,
                time_filter="all",
                filter_locked=True,
                filter_mod=False,
                filter_stickied=True,
                filter_original_content=False,
                filter_nsfw=False,
                min_upvotes=50,
                min_num_comments=10,
                min_upvote_ratio=0.85,
            )
    
            for j in range(len(posts)):
                try:
                    post_link = "https://www.reddit.com" + posts[j]["permalink"]
                    create = True
                    if connection_status:
                        if db.get_viddited(posts[j]["permalink"]):
                            create = False
                    if create:
                        logger.info(f"Creating video for {post_link}")
                        no_comments, post_info = comment_image_scraper.scrape_post(post_link, args.max_comments)
                        vid_input_list = [f"{POST_IMAGE_DIR}/0.png"] + [
                            f"{COMMENT_IMAGE_DIR}/{x}.png" for x in range(0, no_comments)
                        ]
                        audio_input_list = [f"{POST_AUDIO_DIR}/0.mp3"] + [f"{COMMENT_AUDIO_DIR}/{x}.mp3" for x in range(0, no_comments)]
                        generate_video_from_content(BACKGROUND_PATH, vid_input_list, audio_input_list, output_name=TEMP_OUTPUT_NAME+".mp4")
                        metadata = metadata_generator.generate_metadata_gpt(post_info)
                        with open(TEMP_OUTPUT_NAME+".json", "w") as f:
                            json.dump(metadata, f)
                        upload_to_google_drive(TEMP_OUTPUT_NAME+".mp4", OUATH_CREDS_PATH, metadata["Title"] + ".mp4")
                        upload_to_google_drive(TEMP_OUTPUT_NAME+".json", OUATH_CREDS_PATH, metadata["Title"]  + ".json")
                        if connection_status:
                            db.add_viddited(posts[j]["permalink"]) #TODO Add metadata
                except Exception as e:
                    logger.error(f"Error processing post {post_link}")
                    logger.error(e)
                    continue
        except Exception as e:
            logger.error(f"Could not scrape subreddit {reddits[i]}: {e}")
            posts = []  

if __name__ == "__main__":
    main()

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
    # save_credentials_web_server_login()
    # upload_to_google_drive(TEMP_OUTPUT_NAME)
