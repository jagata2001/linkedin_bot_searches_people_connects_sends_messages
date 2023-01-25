from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
from queue import Queue
import threading

class Linkedin:
    search_pages = Queue()

    def __init__(self,username,password,keywords = []):
        self.username = username
        self.password = password
        self.keywords = keywords
        self.browser = webdriver.Chrome(executable_path="./chromedriver")

    def login(self,br = None):
        if br == None:
            br = self.browser
        br.get("https://linkedin.com/")
        mail_input = br.find_element_by_id("session_key")
        password_input = br.find_element_by_id("session_password")
        login_button = br.find_element_by_class_name("sign-in-form__submit-button")
        mail_input.send_keys(self.username)
        password_input.send_keys(self.password)
        login_button.click()
    def search_people(self):
        for keyword in self.keywords:
            url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SWITCH_SEARCH_VERTICAL"
            self.browser.get(url)
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            sleep(2)

            for_pages = self.browser.find_elements_by_class_name("artdeco-pagination__indicator.artdeco-pagination__indicator--number.ember-view")
            last_page = for_pages[len(for_pages)-1].find_element_by_tag_name("span")
            last_page = last_page.text

            for i in range(27,int(last_page)+1):
                self.search_pages.put(f"https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=SWITCH_SEARCH_VERTICAL&page={i}")

    def connect_to_people(self):
        connection_quantity = 0
        while self.search_pages.qsize() != 0:
            try:
                url = self.search_pages.get()
                self.browser.get(url)
                buttons_container = self.browser.find_elements_by_xpath("//div[@class='entity-result__actions entity-result__divider']")
                cc = self.browser.find_elements_by_class_name("entity-result__actions.entity-result__divider")

                for button in buttons_container:
                    bt = button.find_element_by_tag_name("button")
                    if bt.text == "Connect":
                        bt.click()
                        wait = WebDriverWait(self.browser, 5)
                        sleep(5)
                        email = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.ml1.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view'))).click()
                        connection_quantity +=1
                        sleep(5)
                        print("connection count:",connection_quantity)
                sleep(10)

                if connection_quantity >= 200:
                    break
            except:
                sleep(5)
                print("something went wrong!!")
    def collect_links_to_message(self):
        self.browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Linux; Android 11; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36'})
        self.browser.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
        count = 0
        old_count = 0
        while True:
            file = open("links.txt","r")
            links = file.read().split("===")
            file.close()

            flex_wrapper = self.browser.find_elements_by_class_name("flex-wrapper")
            old_count = count
            count = len(flex_wrapper)

            for each in flex_wrapper[old_count:count]:
                a_tags = each.find_elements_by_tag_name("a")
                link = a_tags[1].get_attribute("href")
                if link not in links:
                    links.append(link)

            file = open("links.txt","w")
            file.write("===".join(links))
            file.close()
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")


            print(old_count,count,len(links))
            if count == old_count:
                break
            sleep(5)

    def send_message(self):
        local_browser = webdriver.Chrome(executable_path="./chromedriver")
        self.login(local_browser)
        old_length = 0
        cur_length = 0
        i=0
        while True:
            local_browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Linux; Android 11; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36'})
            file = open("links.txt","r")
            links = file.read().split("===")
            file.close()
            cur_length = len(links)
            sended_file = open("sended_users.txt","r")
            sended_data = sended_file.read().split("===")
            sended_file.close()
            if old_length == cur_length:
                break
            for each in links[old_length:]:
                if each not in sended_data:
                    print("sended:", i)
                    local_browser.get(each)
                    sended_data.append(each)
                    wait = WebDriverWait(local_browser, 5)

                    wait.until(EC.visibility_of_element_located((By.ID, 'messaging-reply'))).send_keys("Hi")

                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".round-btn.component-theme.round-btn_primary.round-btn_small.message-send.js-round-btn.ripple"))).click()                                                             #round-btn.component-theme.round-btn_primary.round-btn_small.message-send.js-round-btn.ripple

                i+=1

                sended_file1 = open("sended_users.txt","w")
                sended_file1.write("===".join(sended_data))
                sended_file1.close()
                sleep(3)
                if i > 200:
                    break

            old_length = cur_length




    def __del__(self):
        print("Program Successfuly ended")
        self.browser.close()



linkedin = Linkedin("username","passwrd",["Israel real estate"])
linkedin.login()

#search and connect to people
linkedin.search_people()
print("queue size: ",linkedin.search_pages.qsize())
linkedin.connect_to_people()
'''
threading.Thread(target=linkedin.send_message).start()
threading.Thread(target=linkedin.collect_links_to_message).start()
'''
