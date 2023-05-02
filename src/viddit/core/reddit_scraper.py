import logging
import os
import random
import time

import praw
from gtts import gTTS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from viddit.utils.file_util import delete_content_of_dir, make_dir_if_not_exists

# TODO: Remove Automod comments

logger = logging.getLogger(__name__)

LANG_BASE_MODEL = "en-US-Standard-"
MODELS = ["A", "B", "C", "D", "E", "F"]


class RedditPostImageScraper:
    def __init__(self, directories, tts_module, path_to_driver="chromedriver.exe", headless=True, operating_sys="linux"):
        # check driver exists
        if operating_sys not in ["windows", "linux"]:
            raise ValueError("os must be 'windows' or 'linux'")
        if not os.path.exists(path_to_driver):
            raise FileNotFoundError("Could not find chromedriver at path: " + path_to_driver)
        options = Options()
        if operating_sys == "linux":
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--remote-debugging-port=0")
            options.add_argument(
                "--no-sandbox"
            )  # Discouraged - It is way better to run the Docker container as a non-root user. Problem for another day.
            options.add_argument("--start-maximized")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-extensions")
        if headless:
            if operating_sys == "windows":
                options.add_argument("--disable-gpu")
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(path_to_driver, options=options)
        self.directories = directories
        self.tts_module = tts_module
        self.setup()

    def setup(self):
        [make_dir_if_not_exists(directory) for directory in self.directories.values()]
        self.accept_cookies()

    def delete_data(self):
        [delete_content_of_dir(directory) for directory in self.directories.values()]

    def teardown(self):
        self.delete_data()
        self.driver.close()
        self.driver.quit()

    def accept_cookies(self):
        logger.info("Accepting Reddit cookies.")
        self.driver.get("https://www.reddit.com/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Accept all')]")))
        self.driver.find_element("xpath", "//button[contains(text(), 'Accept all')]").click()
        logger.info("Cookies accepted")
        self.driver.switch_to.default_content()

    def scrape_post(self, post_url, no_comments=5):
        post_data = {}
        logger.debug("Deleting old data...")
        self.delete_data()
        logger.info("Fetching post with URL: " + post_url)
        self.driver.get(post_url)
        new_css = False
        try:
            post = WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".Post")))
        except Exception as e:
            logger.info("Could not find post, trying alternate CSS styling...")
            try:
                post = WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.TAG_NAME, "shreddit-post")))
                new_css = True
            except Exception as e:
                logger.error("Could not find post..")
                raise e

        if new_css:
            title_text = post.get_attribute("post-title")
            try:
                post_text = post.find_element(By.CSS_SELECTOR, "div[id$='-post-rtjson-content']").text.strip()
            except Exception as e:
                logger.info("Could not find post text...")
                post_text = ""
        else:
            title_text = post.find_element(By.CSS_SELECTOR, "h1").text.strip()
            post_text = (
                post.find_element(By.CSS_SELECTOR, "div[data-test-id='post-content']")
                .find_element(By.CSS_SELECTOR, "[data-click-id='text']")
                .text.strip()
            )

        full_post_text = f"{title_text}\n{post_text}"
        post_data["Post"] = full_post_text
        post.screenshot(os.path.join(self.directories["post_image"], "0.png"))
        logger.info("Post text: " + full_post_text)
        logger.info("Post fetched, performing text to speech for main post...")
        self.tts_module.text_to_speech(
            full_post_text,
            os.path.join(self.directories["post_audio"], "0.mp3"),
            language_code="en-US",
            voice_name=LANG_BASE_MODEL + random.choice(MODELS),
            speaking_rate=1.25,
        )
        logger.debug("Waiting for comments to load...")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # TODO Can be a WebDriverWait

        if new_css:
            comments = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "shreddit-comment")))
            mod_flag = comments[0].find_element(By.XPATH, (".//*[not(self::icon-mod)]"))
        else:
            comments = WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[id^=t1_][tabindex]"))
            )
            mod_flag = comments[0].find_element(By.CSS_SELECTOR, (".icon.icon-lock_fill"))

        allowed_style = comments[0].get_attribute("style")  # Filter for top level comments
        comments = [comment for comment in comments if comment.get_attribute("style") == allowed_style][: no_comments + 1]
        logger.info(f"Found {len(comments)} comments, filtering for top level comments...")
        if mod_flag:
            logger.info("Mod comment found, removing")
            comments.pop(0)
        else:
            logger.info("Mod comment not found, removing last comment")
            comments.pop()

        for i in range(len(comments)):
            desired_y = (comments[i].size["height"] / 2) + comments[i].location["y"]
            window_h = self.driver.execute_script("return window.innerHeight")
            window_y = self.driver.execute_script("return window.pageYOffset")
            current_y = (window_h / 2) + window_y
            scroll_y_by = desired_y - current_y
            self.driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)
            time.sleep(0.2)
            if new_css:
                text = comments[i].find_element(By.CSS_SELECTOR, "#-post-rtjson-content").text.strip()
                # comments[i] = self.driver.execute_script('return arguments[0].shadowRoot.querySelector("details")', comments[i]) # This isolates the individual comment, otherwise we screenshot the tree

            else:
                text = "\n".join([element.text for element in comments[i].find_elements(By.CSS_SELECTOR, ".RichTextJSON-root")])
            logger.debug(f"Performing TTS for comment {str(i)}, text: " + text)
            self.tts_module.text_to_speech(
                text,
                os.path.join(self.directories["comment_audio"], f"{i}.mp3"),
                language_code="en-US",
                voice_name=LANG_BASE_MODEL + random.choice(MODELS),
                speaking_rate=1.25,
            )
            post_data[f"Comment_{str(i)}"] = text
            # Screenshot & save text
            comments[i].screenshot(os.path.join(self.directories["comment_image"], f"{i}.png"))
        logger.info("Post and top comments screenshoted and text to speech-ed.")
        return len(comments), post_data


class SubRedditInfoScraper:
    def __init__(self, client_id, client_secret, password, user_agent, username):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            password=password,
            user_agent=user_agent,
            username=username,
        )

    def get_subreddit_info(
        self,
        subreddit_name,
        limit=10,
        time_filter="day",
        filter_locked=True,
        filter_mod=False,
        filter_stickied=True,
        filter_original_content=False,
        filter_nsfw=False,
        min_upvotes=None,
        min_num_comments=None,
        min_upvote_ratio=None,
    ):
        if time_filter not in ["all", "day", "hour", "month", "week", "year"]:
            raise ValueError("time_filter must be one of 'all', 'day', 'hour', 'month', 'week', 'year'")
        subreddit = self.reddit.subreddit(subreddit_name)
        logger.info(f"Getting top {limit} posts from {subreddit_name} in {time_filter} time filter")
        info_list = []
        for submission in subreddit.top(limit=limit, time_filter=time_filter):
            if (
                (not filter_locked or not submission.locked)
                and (not filter_mod or submission.distinguished is None)
                and (not filter_stickied or not submission.stickied)
                and (not filter_original_content or submission.is_original_content)
                and (not filter_nsfw or not submission.over_18)
                and (min_upvotes is None or submission.score >= min_upvotes)
                and (min_num_comments is None or submission.num_comments >= min_num_comments)
                and (min_upvote_ratio is None or submission.upvote_ratio >= min_upvote_ratio)
            ):
                info_dict = {
                    "created_utc": submission.created_utc,
                    "distinguished": submission.distinguished,
                    "id": submission.id,
                    "is_original_content": submission.is_original_content,
                    "link_flair_text": submission.link_flair_text,
                    "locked": submission.locked,
                    "name": submission.name,
                    "num_comments": submission.num_comments,
                    "nsfw": submission.over_18,
                    "permalink": submission.permalink,
                    "score": submission.score,
                    "selftext": submission.selftext,
                    "spoiler": submission.spoiler,
                    "stickied": submission.stickied,
                    "title": submission.title,
                    "upvote_ratio": submission.upvote_ratio,
                    "url": submission.url,
                }
                info_list.append(info_dict)
        logger.info(f"Found {len(info_list)} posts in {subreddit_name} with the given filters")
        return info_list
