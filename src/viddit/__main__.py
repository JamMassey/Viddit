#TODO 
import json
import logging
import os

from viddit.core.content_upload.gdrive_uploader import upload_to_google_drive
# from core.content_upload.youtube_uploader import YoutubeUploader
from viddit.core.mongo import initialise_db
from viddit.core.reddit_scraper import RedditPostImageScraper, SubRedditInfoScraper
from viddit.core.video_writer import generate_video_from_content
from selenium.webdriver.remote.remote_connection import LOGGER
from viddit.utils.logging_utils import setup_logger

logging.getLogger("gtts").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("praw").setLevel(logging.WARNING)

LOGGER.setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

BASE_OUTPUT_DIR = os.path.join("code","output")
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
BACKGROUND_PATH = os.path.join(os.path.dirname(__file__), 'resources', "background.mp4")
REDDIT_CREDS_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'creds', 'reddit_credentials.json')
OUATH_CREDS_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'creds', 'oauth.json')
CLIENT_SECRETS_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'creds', 'client_secrets.json')
CHROME_DRIVER_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'chromedriver') #Dockerfile dictates where this is


SUBREDDIT_LIST = ["Showerthoughts"]
MAX_VIDS_PER_SUBREDDIT = 5
NO_COMMENTS = 3
TEMP_OUTPUT_NAME = "output.mp4"
LOCAL_MODE = True



def main():
    setup_logger(level=logging.DEBUG, stream_logs=True)
    reddit_creds = json.load(open(REDDIT_CREDS_PATH))
    subreddit_scraper = SubRedditInfoScraper(
        reddit_creds["client_id"],
        reddit_creds["client_secret"],
        reddit_creds["password"],
        reddit_creds["user_agent"],
        reddit_creds["username"],
    )
    for i in range(len(SUBREDDIT_LIST)):
        posts = subreddit_scraper.get_subreddit_info(
            SUBREDDIT_LIST[i],
            limit=MAX_VIDS_PER_SUBREDDIT,
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
        if LOCAL_MODE:
            db = None
            connection_status = False
        else:
            db, connection_status = initialise_db()

        comment_image_scraper = RedditPostImageScraper(DIRECTORIES, CHROME_DRIVER_PATH)
        for j in range(len(posts)):
            post_link = "https://www.reddit.com" + posts[j]["permalink"]
            try:
                if LOCAL_MODE:
                    post_name = posts[j]["title"].replace(" ", "_")
                    no_comments = comment_image_scraper.scrape_post("https://www.reddit.com" + posts[j]["permalink"], NO_COMMENTS)
                    vid_input_list = [f"{POST_IMAGE_DIR}/0.png"] + [
                        f"{COMMENT_IMAGE_DIR}/{x}.png" for x in range(0, no_comments)
                    ]  # TODO Pass back paths from scrape
                    audio_input_list = [f"{POST_AUDIO_DIR}/0.mp3"] + [f"{COMMENT_AUDIO_DIR}/{x}.mp3" for x in range(0, no_comments)]
                    generate_video_from_content(BACKGROUND_PATH, vid_input_list, audio_input_list, output_name=post_name + ".mp4")
                    upload_to_google_drive(post_name + ".mp4", OUATH_CREDS_PATH)
                    os.remove(post_name + ".mp4")
                else:
                    if connection_status:
                        if not db.get_viddited(posts[j]["permalink"]):
                            post_name = posts[j]["title"].replace(" ", "_")
                            no_comments = comment_image_scraper.scrape_post("https://www.reddit.com" + posts[j]["permalink"], NO_COMMENTS)
                            vid_input_list = [f"{POST_IMAGE_DIR}/0.png"] + [
                                f"{COMMENT_IMAGE_DIR}/{x}.png" for x in range(0, no_comments)
                            ]  # TODO Pass back paths from scrape
                            audio_input_list = [f"{POST_AUDIO_DIR}/0.mp3"] + [f"{COMMENT_AUDIO_DIR}/{x}.mp3" for x in range(0, no_comments)]
                            generate_video_from_content(BACKGROUND_PATH, vid_input_list, audio_input_list, output_name=post_name + ".mp4")
                            upload_to_google_drive(post_name + ".mp4", OUATH_CREDS_PATH)
                            os.remove(post_name + ".mp4")
                            db.add_viddited(posts[j]["permalink"])
                    else:
                        raise Exception("Unable to connect to database while in non-local mode")
            except Exception as e:
                logger.error(f"Error processing post {post_link}")
                logger.error(e)
                continue


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
