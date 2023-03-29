#!/usr/bin/env python3
"""Twitter 2 WhatsApp Video Save Bot v2.0
Python bot that download and reupload videos on twitter and sends to whatsapp numbers.
"""

import tweepy
from time import sleep
import requests
from datetime import datetime
import os
import validators
import os
import platformdirs
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (UnexpectedAlertPresentException, NoSuchElementException)
from webdriver_manager.chrome import ChromeDriverManager
import src.twitter_video as twvid

def main(): 
    twitter = twitterConnect()
    whatsapp = whatsappConnect()
    sleep(20)
    wait = WebDriverWait(whatsapp, 600)
    lastfile = open("lastid.txt", "r")
    since_id = int(lastfile.readline())
    lastfile.close()
    while True:
        since_id = check_mentions(twitter, since_id, whatsapp, wait)
        lastfile2 = open("lastid.txt", "w")
        lastfile2.write(str(since_id))
        lastfile2.close()
        print("Completed a batch...")
        sleep(20)

def check_mentions(api, since_id, whatsapp, wait):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("\nChecking for mentions...", current_time)
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is None:
            print("This is not a reply, skipping...")
        else:
            print("New mention")
            try:
                tweetid = str(tweet.in_reply_to_status_id)
                tweetuser = str(tweet.user.screen_name)
                tweetuserid = str(tweet.user.id)
                video_url = ""
                print(tweetuserid)
                check_url = "https://t2w.app/includes/check.php"
                x = requests.post(check_url, data={'id': tweetuserid}).text
                if x == "NULL":
                    print("User not registered. Telling them.")
                    reply = "Not so fast, you are not registered yet.\nVisit t2w.app to link your number to receive videos."
                    api.update_status(status=reply, in_reply_to_status_id=tweet.id, auto_populate_reply_metadata=True)
                    print("Posted successfully on twitter!\n")
                else:
                    data = api.get_status(tweetid, tweet_mode='extended', include_entities=True)._json
                    if 'extended_entities' in data:
                        target = data['extended_entities']
                    elif 'entities' in data:
                        target = data['entities']
                    else:
                        target = []
                    if 'media' in target:
                        default_bitrate = -1
                        for ent in target['media']:
                            if ent['type'] == 'video':
                                for variant in ent['video_info']['variants']:
                                    if 'bitrate' in variant:
                                        if int(variant['bitrate']) > default_bitrate:
                                            response = requests.head(variant['url'], allow_redirects=True)
                                            if 'Content-Length' in response.headers:
                                                if int(response.headers['Content-Length']) < 14680064:
                                                    print(str(variant['url'])+" is "+str(response.headers['Content-Length'])+" - Eligible")
                                                    video_url = variant['url']
                                                    default_bitrate = variant['bitrate']
                                                else:
                                                    print("Too large for WhatsApp")
                    if not validators.url(video_url):
                        print("Didn't get video URL from API, lets try bruteforce")
                        video_url = twvid.get_video("https://twitter.com/twitter/status/"+tweetid)
                    if validators.url(video_url):
                        print("Got Video URL: "+video_url)
                        r = requests.get(video_url, allow_redirects=True, stream=True)
                        file = "temp/"+tweetid+".mp4"
                        with open(file, "wb") as vid:
                            for chunk in r.iter_content(chunk_size=1024):
                                if chunk:
                                    vid.write(chunk)
                        try:
                            link = "https://web.whatsapp.com/send?phone="+x+"&text&type=phone_number&app_absent=1"
                            whatsapp.get(link)
                            sleep(5)
                            sendMessage(whatsapp, wait, "Hi @"+tweetuser+", Your requested video from Twitter is ready here", x)
                            sendVideo(whatsapp, wait, file, x)
                            sleep(3)
                            print("Sent to WhatsApp successfully!\n")
                        except UnexpectedAlertPresentException as bug:
                            print(f"An exception occurred: {bug}")
                        os.remove("temp/"+tweetid+".mp4")
                    else:
                        print("We can't get video URL or tweet doesnt have a video")
            except Exception as e:
                print("Error occured.", e)
                sleep(60)
    return new_since_id

def convert_bytes_to(size, to):
    conv_to = to.upper()
    if conv_to in ["BYTES", "KB", "MB", "GB", "TB"]:
        for x in ["BYTES", "KB", "MB", "GB", "TB"]:
            if x == conv_to:
                return size
            size /= 1024.0

def find_attachment(wait):
    clipButton = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main"]/footer//*[@data-icon="clip"]/..')
        )
    )
    clipButton.click()

def send_attachment(wait):
    wait.until_not(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
        )
    )
    sendButton = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "/html/body/div[1]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div/span",
            )
        )
    )
    sendButton.click()
    wait.until_not(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
        )
    )

def sendMessage(browser, wait, message, mobile):
    try:
        inp_xpath = ('//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]')
        input_box = wait.until(EC.presence_of_element_located((By.XPATH, inp_xpath)))
        for line in message.split("\n"):
            input_box.send_keys(line)
            ActionChains(browser).key_down(Keys.SHIFT).key_down(
                Keys.ENTER
            ).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
        input_box.send_keys(Keys.ENTER)
        print(f"Message sent successfuly to {mobile}")
    except(NoSuchElementException, Exception) as bug:
        print(f"Failed to send a message to {mobile} - {bug}")

def sendVideo(browser, wait, video, mobile):
    try:
        filename = os.path.realpath(video)
        f_size = os.path.getsize(filename)
        x = convert_bytes_to(f_size, "MB")
        if x < 14:
            find_attachment(wait)
            video_button = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer//*[@data-icon="attach-image"]/../input',
                    )
                )
            )
            video_button.send_keys(filename)
            send_attachment(wait)
            print(f"Video has been successfully sent to {mobile}")
        else:
            print(f"Video larger than 14MB")
    except (NoSuchElementException, Exception) as bug:
        print(f"Failed to send a message to {mobile} - {bug}")

def twitterConnect(max_attempts=-1, seconds_between_attempts=60):
    attempt = 0
    while attempt != max_attempts:
        try:
            print('Authenticating Twitter...')
            auth = tweepy.OAuthHandler("", "")
            auth.set_access_token("", "")
            twitterAPI = tweepy.API(auth)
            twitterAPI.verify_credentials()
            print("Twitter Authentication OK!\n")
            return twitterAPI
        except Exception as error:
            print("Error during authentication", error)
            print("Retrying in {} seconds".format(seconds_between_attempts))
            sleep(seconds_between_attempts)
            attempt += 1
    raise RuntimeError("Failed to authenticate after {} attempts".format(max_attempts))

def whatsappConnect():
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=" + platformdirs.user_data_dir("t2w"))
    chrome_options.add_argument("start-maximized")
    print("WhatsApp Authentication OK!\n")
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    browser.get("https://web.whatsapp.com/")
    browser.maximize_window()
    return browser

if __name__ == '__main__':
    main()