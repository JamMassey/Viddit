
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import logging 
import time
from gtts import gTTS
from utils.file_util import make_dir_if_not_exists, delete_content_of_dir
import os
#TODO: Remove Automod comments

logger = logging.getLogger(__name__)



class RedditScraper:
    def __init__(self, directories, path_to_driver = "chromedriver.exe"):
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')  # Last I checked this was necessary.
        self.driver = webdriver.Chrome(path_to_driver, chrome_options=options)
        self.directories = directories
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
        self.driver.get("https://www.reddit.com/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Accept all')]")))
        self.driver.find_element("xpath", "//button[contains(text(), 'Accept all')]").click()
        logger.info("Cookies accepted")
        self.driver.switch_to.default_content() 

    def scrape(self, post_url, no_comments = 5):
        # Load cookies to prevent cookie overlay & other issues
        # for cookie in config['reddit_cookies'].split('; '):
        #     cookie_data = cookie.split('=')
        #     driver.add_cookie({'name':cookie_data[0],'value':cookie_data[1],'domain':'reddit.com'})

        # Fetching the post itself, text & screenshot
        self.delete_data()
        self.driver.get(post_url)
        post = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.Post')))
        post_text = post.find_element(By.CSS_SELECTOR, 'h1').text #TODO Text to speech
        post.screenshot(os.path.join(self.directories["post_image"], "0.png"))
        tts = gTTS(post_text)
        tts.save(os.path.join(self.directories["post_audio"], "0.mp3"))
        # Let comments load
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) #TODO Can be a WebDriverWait
        
        # Fetching comments & top level comment determinator
        comments = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[id^=t1_][tabindex]')))
        allowed_style = comments[0].get_attribute("style")
        
        # Filter for top only comments
        comments = [comment for comment in comments if comment.get_attribute("style") == allowed_style][:no_comments]

        # Save time & resources by only fetching X content
        for i in range(len(comments)):
            # TODO Filter out locked comments (AutoMod) 
            # Scrolling to the comment ensures that the profile picture loads
            # Credit: https://stackoverflow.com/a/57630350
            desired_y = (comments[i].size['height'] / 2) + comments[i].location['y']
            window_h = self.driver.execute_script('return window.innerHeight')
            window_y = self.driver.execute_script('return window.pageYOffset')
            current_y = (window_h / 2) + window_y
            scroll_y_by = desired_y - current_y
            self.driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)
            time.sleep(0.2)

            # Getting comment into string 
            text = "\n".join([element.text for element in comments[i].find_elements(By.CSS_SELECTOR,'.RichTextJSON-root')])
            tts = gTTS(text)
            tts.save(os.path.join(self.directories["comment_audio"], f'{i}.mp3'))
            # Screenshot & save text
            comments[i].screenshot(os.path.join(self.directories["comment_image"], f'{i}.png'))
        return len(comments)
