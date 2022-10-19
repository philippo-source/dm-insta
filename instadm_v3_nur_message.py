from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from random import randint, uniform
from time import time, sleep
import pyperclip
import logging
import sqlite3
import datetime


DEFAULT_IMPLICIT_WAIT = 30

class InstaDM(object):

    def __init__(self, username, password, headless=True, db_workspace=None, profileDir=None):
        self.selectors = {
            "accept_cookies": "//button[text()='Accept All'] | //button[text()='Alle annehmen']",
            "home_to_login_button": "//button[text()='Log In']",
            "username_field": "username",
            "password_field": "password",
            "button_login": "//button/*[text()='Log In']",
            "login_check": "//*[@aria-label='Home'] | //button[text()='Save Info'] | //button[text()='Not Now']",
            "save_later": "//button[text()='Not Now'] | //button[text()='Jetzt nicht']",
            "startseite_add": "//button[text()='Zur Startseite hinzufügen']",
            "startseite_add_Button": "//button[text()='Abbrechen']",
            "search_user": "queryBox",
            "select_user": '//div[text()="{}"]',
            "name": "((//div[@aria-labelledby]/div/span//img[@data-testid='user-avatar'])[1]//..//..//..//div[2]/div[2]/div)[1]",
            "next_button": "//button/*[text()='Next']",
            "textarea": "//textarea[@placeholder]",
            "send": "//button[text()='Send']",
            "sharePost": "//*[@aria-label='Beitrag teilen'] | //*[@aria-label='Share post']",
            "teilen": "//button/*[text()='Senden']",
            "select_user_pageLoad": '//*[text()="{}"]',
            "send_message_pageLoadCheck": '//*[text()="mylebenslauf"]'
        }

        # Selenium config
        options = webdriver.ChromeOptions()

        if profileDir:
            options.add_argument("user-data-dir=profiles/" + profileDir)

        if headless:
            options.add_argument("--headless")

        mobile_emulation = {
            #"userAgent": 'Mozilla/5.0 (Linux; Android 4.0.3; HTC One X Build/IML74K) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19'
            "userAgent": 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1'
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)

        self.driver = webdriver.Chrome(executable_path=CM().install(), options=options)
        self.driver.set_window_position(0, 0)
        #self.driver.set_window_size(414, 736)
        self.driver.set_window_size(768, 1024)

        # Instapy init DB
        self.db_workspace = db_workspace
        self.conn = None
        self.cursor = None
        if self.db_workspace is not None:
            self.conn = sqlite3.connect(self.db_workspace)
            self.cursor = self.conn.cursor()

            cursor = self.conn.execute("""
                SELECT count(*)
                FROM sqlite_master
                WHERE type='table'
                AND name='message';
            """)
            count = cursor.fetchone()[0]

            if count == 0:
                self.conn.execute("""
                    CREATE TABLE "message" (
                        "username"    TEXT NOT NULL,
                        "message"    TEXT DEFAULT NULL,
                        "sent_message_at"    TIMESTAMP
                    );
                """)

        try:
            self.login(username, password)
        except Exception as e:
            logging.error(e)
            print(str(e))

    def login(self, username, password):
        # homepage
        self.driver.get('https://instagram.com/?hl=en')
        self.__random_sleep__(2, 2)
        if self.__wait_for_element__(self.selectors['accept_cookies'], 'xpath', 2):
            self.__get_element__(self.selectors['accept_cookies'], 'xpath').click()
            self.__random_sleep__(2, 4)
        # if self.__wait_for_element__(self.selectors['home_to_login_button'], 'xpath', 4):
        #     self.__get_element__(self.selectors['home_to_login_button'], 'xpath').click()
        #     self.__random_sleep__(3, 5)

        # login
        logging.info(f'Login with {username}')
        self.__scrolldown__()
        if not self.__wait_for_element__(self.selectors['username_field'], 'name', 10):
            print('Login Failed: username field not visible')
        else:
            self.driver.find_element_by_name(self.selectors['username_field']).send_keys(username)
            self.driver.find_element_by_name(self.selectors['password_field']).send_keys(password)
            self.__get_element__(self.selectors['button_login'], 'xpath').click()
            # if self.__wait_for_element__(self.selectors['save_later'], 'xpath', 10):
            #     self.__get_element__(self.selectors['save_later'], 'xpath').click()
            # else:
            #     print('Save Later wegklicken Failed')
            self.__random_sleep__(2,5)
            #self.__random_sleep__(200,500)
            if self.__wait_for_element__(self.selectors['login_check'], 'xpath', 6):
                #self.__wait_for_element__(self.selectors['save_later'], 'xpath')
                self.__get_element__(self.selectors['save_later'], 'xpath').click()
                print('Login Successful and clicked Not now')

                self.__wait_for_element__(self.selectors['save_later'], 'xpath', 5)
                self.__get_element__(self.selectors['save_later'], 'xpath').click()
                print('Benachrichtigungen jetzt nicht aktivieren')
                self.__random_sleep__(3, 5)

                # if self.__wait_for_element__(self.selectors['startseite_add'], 'xpath', 5):
                #     print('Startseite Add Popup erscheint')
                #     self.__get_element__(self.selectors['startseite_add_Button'], 'xpath').click()
                # else:
                #     print('Startseite wegklicken Failed')
                
            else:
                print('Login Failed: Incorrect credentials')

    def createCustomGreeting(self, greeting):
        # Get username and add custom greeting
        if self.__wait_for_element__(self.selectors['name'], "xpath", 10):
            user_name = self.__get_element__(self.selectors['name'], "xpath").text
            if user_name:
                greeting = greeting + " " + user_name + ", \n\n"
        else: 
            greeting = greeting + ", \n\n"
        return greeting

    def typeMessage(self, user, message):
        # Go to page and type message
        print("bin jetzt in type message")
        if self.__wait_for_element__(self.selectors['next_button'], "xpath"):
            self.__get_element__(self.selectors['next_button'], "xpath").click()
            self.__random_sleep__(2,4)

        if self.__wait_for_element__(self.selectors['textarea'], "xpath"):

            #driver.execute_script("document.getElementById('some-random-number').innerHTML = '200';")
            self.driver.execute_script("document.querySelector('textarea').classList.add('focus-visible')")

            #self.driver.execute_script("document.querySelector('textarea').innerText = 'Das ist super 👋'")
            self.driver.execute_script(f"document.querySelector('textarea').innerHTML = '{message}'")
            self.__type_slow__(self.selectors['textarea'], "xpath", " ")
            #self.__get_element__(self.selectors['textarea'], "xpath").click()
            #pyperclip.copy('The text to be copied to the clipboard.👋')
            #paste = pyperclip.paste()
            #self.__type_slow__(self.selectors['textarea'], "xpath", message)
            self.__random_sleep__(5,10)

        if self.__wait_for_element__(self.selectors['send'], "xpath"):
            self.__get_element__(self.selectors['send'], "xpath").click()
            #self.__random_sleep__(3, 5)
            print('Message sent successfully')

            

    def getPostAndSend(self,users, message, excludeList, greeting=None):
        print(users)
        messages = 0
        i=1
        for user in users:
                    print(i)
                    if i == 13:
                        print("...SENT 12 messages, will sleep now for a bit...")
                        tm = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') 
                        print(f"INFO...[{tm}]")
                        i=1
                        self.__random_sleep__(500, 800)
                    
                    print(f'...SHARE POST...Check user: {user} to send message')
                    listA = excludeList

                    if user in listA:
                        print("...SHARE POST...Blocked user found in : ", listA)
                        continue

                    
                    self.cursor = self.conn.cursor()
                    cursor = self.conn.execute(f"""
                        SELECT count(*)
                        FROM message
                        WHERE username='{user}'
                    """)
                    count = cursor.fetchone()[0]
                    #print(count)
                    if count != 0:
                        logging.info(f'...SHARE POST...Message already sent to {user} ')
                        print(f'...SHARE POST...Message already sent to {user} ')
                        continue

                    #zeigt nur selbst gefolgte an, nicht wenn user schon folgt bzw. welchen account user folgt; DEPRECATED, wurde umgestellt
                    # cursor = self.conn.execute(f"""
                    #     SELECT count(*)
                    #     FROM followRestriction
                    #     WHERE username='{user}'
                    # """)
                    # count = cursor.fetchone()[0]
                    # #print(count)

                    #wenn user gefollowed wird, keine message...eventuell umstellen
                    # cursor = self.conn.execute(f"""
                    #     SELECT count(*)
                    #     FROM followedAccountPriv
                    #     WHERE username='{user}'
                    # """)
                    # count = cursor.fetchone()[0]

                    # if count != 0:
                    #     logging.info(f'...SHARE POST...User: {user} already followed...no message therefore.')
                    #     print(f'...SHARE POST...User: {user} already followed...no message therefore.')
                    #     continue

                    #AUSSCHLIESSEN: follower von mylebenslauf.online ausschließen, wird durch script vor starten dieses scripts in DB geschrieben
                    cursor = self.conn.execute(f"""
                        SELECT count(*)
                        FROM followersMyLebOnl
                        WHERE username='{user}'
                    """)
                    count = cursor.fetchone()[0]
                    #print(count)

                    if count != 0:
                        logging.info(f'...SHARE POST... {user} already following mylebenslauf.online')
                        print(f'...SHARE POST...Message  {user} already following mylebenslauf.online')
                        continue

                    #AUSSCHLIESSEN: business accounts
                    cursor = self.conn.execute(f"""
                        SELECT count(*)
                        FROM businessaccount
                        WHERE username='{user}'
                    """)
                    count = cursor.fetchone()[0]
                    #print(count)

                    if count != 0:
                        logging.info(f'...SHARE POST... {user} is business acc...no message therefore')
                        print(f'...SHARE POST...Message  {user} is business acc...no message therefore')
                        continue


                    #SEND MESSAGE MODULE.. WENN REIHENFOLGE ÄNDERN: Continue  und waiting time anpassen, beides ende des ersten moduls 
                    
                    #ALT: um auf profil zu checken pb business acc oder bereits follower window shared data bei profilbesuch implementieren
                    logging.info(f'Start sending message to {user}')
                    print(f'Start sending message to {user}')
                    print("Check first whether user is already following mylebenslauf")
                    self.driver.get(f"https://www.instagram.com/{user}")
                    self.__random_sleep__(2, 4)
                    wait = self.__wait_for_element__(self.selectors['select_user_pageLoad'].format(user), 'xpath', 2)
                    print(f"Wait: {wait}")
                    #print(type(wait))
                    if wait == None:
                        print("LOG...User nicht geunfden, refrehse page")
                        self.driver.execute_script("location.reload()")
                    elif wait == False:
                        print("LOG...Username nicht gefunden, wohl Namen geändert oder gelöscht, springe zu nächstem User")
                        continue

                    try:
                        followers_count = self.driver.execute_script(
                            "return window._sharedData.entry_data."
                            "ProfilePage[0].graphql.user.follows_viewer"
                        )
                    except Exception as e:
                        logging.error(e)

                    print(followers_count)
                    if followers_count == True:
                        logging.info(f'...SHARE POST... {user} already follows mylebenslauf...no message therefore')
                        print(f'...SHARE POST...Message  {user} already follows mylebenslauf...no message therefore')
                        continue
                        
                    self.driver.get('https://www.instagram.com/direct/new/?hl=en')
                    self.__random_sleep__(3, 8)

                    try:
                        self.__wait_for_element__(self.selectors['search_user'], "name")
                        self.__type_slow__(self.selectors['search_user'], "name", user)
                        self.__random_sleep__(2, 5)

                        if greeting != None:
                            greeting = self.createCustomGreeting(greeting)


                        # Select user from list
                        elements = self.driver.find_elements_by_xpath(self.selectors['select_user'].format(user))
                        if elements and len(elements) > 0:
                            elements[0].click()
                            self.__random_sleep__(2, 4)

                            if greeting != None:
                                self.typeMessage(user, greeting + message)
                            else:
                                self.typeMessage(user, message)
                            
                            tm = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            if self.conn is not None:
                                self.cursor.execute('INSERT or IGNORE INTO message (username, message, sent_message_at) VALUES(?, ?, ?)', (user, message, tm))
                                self.conn.commit()
                            self.__random_sleep__(20, 40)
                            messages += 1
                            i += 1

                            continue


                        # In case user has changed his username or has a private account
                        else:
                            print(f'User {user} not found! Skipping.')
                            continue

                        
                    except Exception as e:
                        logging.error(e)
                        continue
        print(messages)
        return messages




    def __get_element__(self, element_tag, locator):
        """Wait for element and then return when it is available"""
        try:
            locator = locator.upper()
            dr = self.driver
            if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_id(element_tag))
            elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_name(element_tag))
            elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_xpath(element_tag))
            elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTOR, element_tag):
                return WebDriverWait(dr, 15).until(lambda d: dr.find_element_by_css_selector(element_tag))
            else:
                logging.info(f"Error: Incorrect locator = {locator}")
        except Exception as e:
            logging.error(e)
        logging.info(f"Element not found with {locator} : {element_tag}")
        return None

    def is_element_present(self, how, what):
        """Check if an element is present"""
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def __wait_for_element__(self, element_tag, locator, timeout=30):
        """Wait till element present. Max 30 seconds"""
        result = False
        self.driver.implicitly_wait(0)
        locator = locator.upper()
        for i in range(timeout):
            initTime = time()
            try:
                if locator == 'ID' and self.is_element_present(By.ID, element_tag):
                    result = True
                    break
                elif locator == 'NAME' and self.is_element_present(By.NAME, element_tag):
                    result = True
                    break
                elif locator == 'XPATH' and self.is_element_present(By.XPATH, element_tag):
                    result = True
                    break
                elif locator == 'CSS' and self.is_element_present(By.CSS_SELECTORS, element_tag):
                    result = True
                    break
                else:
                    logging.info(f"Error: Incorrect locator = {locator}")
            except Exception as e:
                logging.error(e)
                print(f"Exception when __wait_for_element__ : {e}")

            # sleep(1 - (time() - initTime))
            sleep(2)
        else:
            print(f"Timed out. Element not found with {locator} : {element_tag}")
        self.driver.implicitly_wait(DEFAULT_IMPLICIT_WAIT)
        return result

    def __type_slow__(self, element_tag, locator, input_text=''):
        """Type the given input text"""
        try:
            self.__wait_for_element__(element_tag, locator, 5)
            element = self.__get_element__(element_tag, locator)
            actions = ActionChains(self.driver)
            actions.click(element).perform()
            for s in input_text:
                element.send_keys(s)
                sleep(uniform(0.25, 0.75))

        except Exception as e:
            logging.error(e)
            print(f'Exception when __typeSlow__ : {e}')

    def __random_sleep__(self, minimum=10, maximum=20):
        t = randint(minimum, maximum)
        logging.info(f'Wait {t} seconds')
        sleep(t)

    def __scrolldown__(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def teardown(self):
        self.driver.close()
        self.driver.quit()


