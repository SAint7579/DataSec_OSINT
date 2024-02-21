#!/usr/bin/env python3
import face_utils
import requests
import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from requests_testadapter import Resp
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
import importlib
import os
from bs4 import BeautifulSoup
from collections import OrderedDict


class LocalFileAdapter(requests.adapters.HTTPAdapter):
    def build_response_from_file(self, request):
        file_path = request.url[7:]
        with open(file_path, 'rb') as file:
            buff = bytearray(os.path.getsize(file_path))
            file.readinto(buff)
            resp = Resp(buff)
            r = self.build_response(request, resp)

            return r

    def send(self, request, stream=False, timeout=None,
             verify=True, cert=None, proxies=None):

        return self.build_response_from_file(request)


def start_browser():
    #Setup browser
    print("Opening Browser...")
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
    options.add_argument("--start-maximized")
    #options.add_argument("headless")
    # options.add_experimental_option("prefs",{"profile.managed_default_content_settings.images":2})
    browser = Chrome(options=options)

    return browser

def sign_in(browser, FBEMAIL, FBPASS):
    #Sign in
    fb_start_page = 'https://www.linkedin.com/'
    fb_user = FBEMAIL
    fb_pass = FBPASS
    print("Logging in %s automatically..." % fb_user)
    browser.get(fb_start_page)
    email_id = browser.find_element(By.ID, 'session_key')
    pass_id = browser.find_element(By.ID, 'session_password')
    email_id.send_keys(fb_user)
    pass_id.send_keys(fb_pass)
    pass_id.send_keys(u'\ue007')
    time.sleep(1)

    
def get_links(subject_name, driver):
    ## Write a function to get to the search page and get all the links 
    ## of the profiles that match the subject_name
    driver.get("https://www.linkedin.com/search/results/people/?keywords="+subject_name)
    time.sleep(1)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    ## Find all anchor tags with aria-hidden="true"
    anchors = soup.find_all('span', {'class': 'entity-result__title-text'})
    ## Get all the hrefs
    hrefs = [anchor.find('a').get('href') for anchor in anchors]
    ## Filter out the None values
    hrefs = list(filter(None, hrefs))
    return hrefs

# chrome_options = webdriver.ChromeOptions()
# prefs = {"profile.default_content_setting_values.notifications" : 2}
# chrome_options.add_experimental_option("prefs",prefs)
# chrome_options.add_argument("--headless")
# driver = webdriver.Chrome("/home/archer/Documents/OSINT_India_Police_Hackathon/chromedriver",chrome_options=chrome_options)
# # driver.maximize_window()
# print("Logging in....")
# driver.get("https://www.facebook.com/siddharth.mahajan.79")
# element = driver.find_element_by_id("email")
# element.send_keys(FBEMAIL)
# element = driver.find_element_by_id("pass")
# element.send_keys(FBPASS)
# element = driver.find_element_by_id("loginbutton")
# element.click()
# print("Logged in....")

def get_profile_pic(browser, link):
    try:
        browser.get(link)
        profile_pic = browser.find_element(By.CLASS_NAME, 'pv-top-card-profile-picture__image')
        link = profile_pic.get_attribute('src')
    except:
        print("Profile picture not found")
        return None
    return link

def fetch_profile_images(browser, name):
    links = get_links(name, browser)[:5]
    link_and_pictures = []
    for i,link in enumerate(links):
        time.sleep(1)
        pic_url = get_profile_pic(browser, link)
        ## Download pic
        if pic_url:
            pic = requests.get(pic_url)
            with open(f'Screenshot/{i}.jpg', 'wb') as f:
                f.write(pic.content)
            link_and_pictures.append((link, [f'UI/Screenshot/{i}.jpg']))

    return link_and_pictures


def validate_profile(name,images,browser):
    lnpc=fetch_profile_images(browser,name)
    recs=[]
    for i in lnpc:
        recs.append(i[1])
    print("Recognising and counting targets.")
    pidx=face_utils.count_targets(images,recs)
    profile_link=lnpc[pidx][0].split("?ref")[0]

    return profile_link
        
