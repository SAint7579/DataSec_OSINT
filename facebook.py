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
    fb_start_page = 'https://m.facebook.com/'
    fb_user = FBEMAIL
    fb_pass = FBPASS
    print("Logging in %s automatically..." % fb_user)
    browser.get(fb_start_page)
    email_id = browser.find_element(By.NAME, 'email')
    pass_id = browser.find_element(By.NAME, 'pass')
    email_id.send_keys(fb_user)
    pass_id.send_keys(fb_pass)
    pass_id.send_keys(u'\ue007')
    time.sleep(3)

    
def get_links(subject_name, driver):
    ## Write a function to get to the search page and get all the links 
    ## of the profiles that match the subject_name
    driver.get("https://www.facebook.com/search/people/?q="+subject_name)
    time.sleep(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    ## Find all anchor tags with aria-hidden="true"
    anchors = soup.find_all('a', {'aria-hidden': 'true'})
    ## Get all the hrefs
    hrefs = [anchor.get('href') for anchor in anchors]
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

def fetch_screen(name, driver):
    profiles = get_links(name,driver)[:5]
    count = 1
    linkandpic = []
    for link in profiles:
        print("Fetching profile ",count)
        # if profile.php is in link then it is a profile link
        if 'profile.php' in link:
            driver.get(link+'&sk=photos')
        else:
            driver.get(link+'/photos')
        imct=1
        driver.execute_script("window.scrollTo(0, 500)")
        linkandpic.append([link,[]])
        while imct<=2:
            time.sleep(5)
            fname="Screenshot/"+str(count)+"_"+str(imct)+".png"
            driver.save_screenshot(fname)
            linkandpic[-1][1].append(fname)
            driver.execute_script("window.scrollTo(500,1000)")
            imct+=1
        count +=1
    return linkandpic


def validate_profile(name,image,driver):
    lnpc=fetch_screen(name,driver)
    recs=[]
    for i in lnpc:
        recs.append(i[1])
    print("Recognising and counting targets.")
    pidx=face_utils.count_targets(['Test_images/Test.jpg'],recs)
    profile_link=lnpc[pidx][0].split("?ref")[0]

    return profile_link
    

def download_friends(url,browser):
    friends_html = "Friends/friends.html"
    url = list(url)
    url[10] = 'm'
    url.pop(8)
    url.pop(8)
    url = ''.join(url)
    browser.get(url + '/friends')
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, 300)") 
    # browser.find_element(By.XPATH, "//span[.='Friends']").click()
    time.sleep(2)
    # print('Scrolling to bottom...')
    # #Scroll to bottom
    # count = 0
    # while browser.find_elements_by_css_selector('#m_more_friends') and count < 5:
    #     browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     count+=1
    #     time.sleep(1)

    #Save friend list
    with open (friends_html, 'w', encoding="utf-8") as f:
        f.write(browser.page_source)
        print('%s) Downloaded' % friends_html)
        
def get_friends():
    '''
    Take friends from friends folder's dumped xml file
    '''
    requests_session = requests.session()
    requests_session.mount('file://', LocalFileAdapter())
    data = requests_session.get('file://C:/Users/Admin/Desktop/Friends/friends.html')

    fname_link = []
    for a in re.findall(r'<a href="/[A-Za-z0-9.=?]+">.*?</a>',str(data.content)) :
        a = a.split('"')
        name = a[2].split("<")[0][1:]
        link = "https://www.facebook.com"+a[1]
        fname_link.append((name,link))
    return fname_link

def get_info(profile_link, driver):
    '''
    Get the information from the profile link from facebook

    args:
        profile_link: the link to the profile
        driver: the selenium driver

    returns:
        a dictionary of the information
    '''
    username=profile_link.split("facebook.com/")[1]
    driver.get("https://mbasic.facebook.com/"+username+"/about")
    def refine_list(fb_list):
        refined = []
        for f in fb_list:
            if f[0] not in [i[0] for i in refined]:
                refined.append(f)
            ## If f is bigger than the existing list, replace existing with f
            else:
                idx = [i[0] for i in refined].index(f[0])
                if len(f) > len(refined[idx]):
                    refined[idx] = f
        return refined

    ## Use beautiful soup to parse the html
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    edu = soup.find('div', {"id":"education"})
    if edu:
        edu = [i for i in edu.find_all('div')  if (i.find('a') and i.find('span'))]
        edu = [[j.text for j in i.find_all('span')] + [i.find_all('span')[0].find('a')['href'] if i.find_all('span')[0].find('a') else None] for i in edu][2:]
        edu = refine_list(edu)

    work = soup.find('div', {"id":"work"})
    if work:
        work = [i for i in work.find_all('div')  if (i.find('a') and i.find('span'))]
        work = [[j.text for j in i.find_all('span')] + [i.find_all('span')[0].find('a')['href'] if i.find_all('span')[0].find('a') else None] for i in work][2:]
        work = refine_list(work)

    living = soup.find('div', {"id":"living"})
    if living:
        living = [i for i in living.find_all('div')  if (i.find('a') and i.find('span'))]
        living = [[i.find('span').text]  + ([j.text for j in i.find_all('a')] if i.find ('a') else [i.find('div', {"class":"el"}).text]) if [i.find('span')] else i.text for i in living][2:]
        living = refine_list(living)

    basic_info = soup.find('div', {"id":"basic-info"})
    if basic_info:
        basic_info = [i for i in basic_info.find_all('div')  if i.find('td')]
        basic_info = [[j.text for j in i.find_all('td')]for i in basic_info][2:]
        basic_info = refine_list(basic_info)

    family = soup.find('div', {"id":"family"})
    if family:
        family = [i for i in family.find_all('div')  if i.find('h3')]
        family = [[j.text for j in i.find_all('h3')] + ['https://www.facebook.com/' + i.find('h3').find('a')['href']] for i in family]
        family = [i for i in family if len(i) == 3]

    overview = soup.find('div', {"id":"year-overviews"})
    if overview:
        overview = [i for i in overview.find_all('div')  if i.find('a')]
        overview = [[i,j] for i,j in  zip([i.find('a').text for i in overview],[i.text[:4] for i in overview]) if j.isnumeric()]
        overview = refine_list(overview)

    relation = soup.find('div', {"id":"relationship"})
    if relation:
        # relation = [i for i in relation.find_all('div')  if i.find('span')]
        relation = [[i.text] for i in relation.find_all('div') if ('Relationship' not in i.text and len(i.text) > 1)]
        relation = refine_list(relation)


    return {'education':edu, 'work':work, 'living':living, 'basic_info':basic_info, 'family':family, 'relation':relation, 'overview':overview}