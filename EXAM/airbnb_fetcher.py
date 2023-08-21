
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
import numpy as np
import threading
import time


#import action chains
from selenium.webdriver.common.action_chains import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

OPTIONS = webdriver.ChromeOptions()
SERVICE = Service(ChromeDriverManager().install())

def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def get_city_url(city, checkin, checkout):
    url = f"""https://www.airbnb.dk/s/{city}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-09-01&monthly_length=3&price_filter_input_type=0&price_filter_num_nights=5&channel=EXPLORE&date_picker_type=calendar&checkin={checkin}&checkout={checkout}&source=structured_search_input_header&search_type=filter_change"""
    return url



class get_place_infoThread (threading.Thread):
   def __init__(self, urls, prices):
      threading.Thread.__init__(self)
      self._features = []
      self._info = []
      self._location = []
      self._rating = []
      self._prices = []
      self._links = []

      self.prices_in = prices


      self.urls = urls
      
   def run(self):
      driver = webdriver.Chrome(service=SERVICE, options=OPTIONS)

      third_len = int(len(self.urls) / 3)
      for i, url in enumerate(self.urls):
         time.sleep(0.5)

         if third_len < 10:
             pass
         elif i % third_len == 0:
            print(f"{i} done in thread")

         try:
            _info, location, rating, price, _features  = get_place_info(url, driver_in = driver)

            self._info.append(_info)
            self._location.append(location)
            self._rating.append(rating)
            self._prices.append(self.prices_in[i])
            self._features.append(_features)
            self._links.append(url)
            time.sleep(1)
         except Exception as e:
            print(e)
         
      driver.close()



def get_houses_and_info(driver, city, checkin, checkout, do_print=True):

    links = []

    _prices, links = get_houses_in_bin(driver,  city, checkin, checkout, do_print=do_print)

    assert len(_prices) == len(links)

    infos = []
    locations = []
    ratings = []
    prices = []
    features = []
    _links = []


    print(f"total number of stays found {len(_prices)}")
    print("getting infos from links")
    do_cookies = True
    for i, link in enumerate(links):
        
        if i % 100 == 0:
            print(f"getting info for {i}, link: {link}")

        try:
            _info, location, rating, price, _feature = get_place_info(link, None, do_cookies=do_cookies)
            #do_cookies = False
            infos.append(_info)
            locations.append(location)
            ratings.append(rating)
            prices.append(_prices[i])
            features.append(_feature)
            _links.append(link)
        except:
            print(f"Failed to get info for {link}")
            time.sleep(3)

    return _links, infos, locations, ratings, prices, features  


def get_houses_and_infoThreaded(driver, city=None, checkin=None, checkout=None, do_print=True, urls=None):
#def get_houses_and_infoThreaded(urls, do_print=True):

    links = []

    if urls is None:    
        _prices, links = get_houses_in_bin(driver,  city, checkin, checkout, do_print=do_print)
    else:
        _prices = [1] * len(urls)
        links = urls

    #links = urls
    #_prices = [0] * len(urls)

    infos = []
    locations = []
    ratings = []
    prices = []
    features = []
    _links = []

    if len(_prices) != len(links):
        print(len(_prices))
        print(len(links))
        print(_prices)
        print(links)
        return [], [], [], [], [], []


    print(f"total number of stays found {len(_prices)}")

    url_splits = chunkIt(links, 3)
    price_splits = chunkIt(_prices, 3)

    threads = []
    for i, url_s in enumerate(url_splits):
        if len(url_s) != len(price_splits[i]):
            print("len erro!")
            print(len(url_s))
            print(len(price_splits[i]))
            print(url_s)
            print(price_splits[i])
            #return [], [], [], [], [], []

        thread = get_place_infoThread(url_s, price_splits[i])
        thread.start()
        threads.append(thread)
        time.sleep(1)

    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    for t in threads:
        infos += t._info
        locations += t._location
        ratings += t._rating
        prices += t._prices
        features += t._features
        links += t._links
    

    return _links, infos, locations, ratings, prices, features  




def get_houses_in_bin(driver,  city, checkin, checkout, do_print=True):

    url = get_city_url(city, checkin, checkout)
    driver.get(url)
    print(url)

    time.sleep(2)

    prices = []
    texts = []

    move = ActionChains(driver)

    is_first = True    # first time we mode the slider a lot
    first_print = True # for printing 0 in first price range

    while True:
        found = False

        #is_new_elem = driver.find_elements(By.XPATH, "/html/body/div[10]/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/section/div/div[2]/div[2]/div[1]/div[1]/div[1]/div/button[1]")
        
        # waiting for loading loop
        for i in range(30):
            
            filter_but = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[3]/div[1]/div[2]/div/div/div/div/div[2]/div/div/button")
            
            if len(filter_but) > 0:
                filter_but[0].click()
            else:            
                filter_but = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div/div[2]/div/div/button")
                                                            #"/html/body/div[5]/div/div/div[1]/div/div[2]/div[1]/div[2]/div/div/div/div/div/div/div[2]/div/div/button
                filter_but[0].click()
            
            if len(filter_but) > 0:
                break

            time.sleep(0.1)
        
        time.sleep(10)
        

        # this bit waits for the price search box to open by looking for a certain element
        i = 0
        while i < 20:
                        
            num_filered = driver.find_elements(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/footer/div/div/div/div/footer/a")
            if len(num_filered) > 0:
                break

            num_filered = driver.find_elements(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/footer/div/div/div/div/footer/a")
            if len(num_filered) > 0:
                break
            
            num_filered = driver.find_elements(By.XPATH, "/html/body/div/div/section/div/div/div/div/div/div/footer/div/div/div/footer/a")
            if len(num_filered) > 0:
                break
            
            num_filered = driver.find_elements(By.XPATH, "/html/body/div[9]/div/section/div/div/div[2]/div/div[2]/footer/a")
            if len(num_filered) > 0:
                break

            i += 1
            time.sleep(0.1)

        
        if len(num_filered) == 0:
            print("trying again, no filter found")
            time.sleep(1)
            driver.close()
            driver = webdriver.Chrome(service=SERVICE, options=OPTIONS)
            prices, texts = get_houses_in_bin(driver,  city, checkin, checkout, do_print=True)
            return prices, texts


        # /html/body/div/div/div/div/div/div[2]/div[2]/main/div[2]/div/div[2]/div/div/div/div/div[1]/div[4]/div/div[2]/div/div/div/div[1]/a

        num_filered = num_filered[0]

        found_filter = False
        #print("going")

        #"/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/section/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button"

                                                    #"/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/section/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button"
        slider_max = driver.find_elements(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/main/div[2]/div/div/div/div/section/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button")
        if len(slider_max) > 0:
            #print("fiirst")
            slider_max = slider_max[0]
            found_filter = True
            min_price_elem = driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/main/div[2]/div/div/div/div/section/div[2]/div/div[1]/div[1]/label/div[2]/div/input")
            max_price_elem = driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/main/div[2]/div/div/div/div/section/div[2]/div/div[1]/div[3]/label/div[2]/div/input")
        
        if not found_filter:
            #print("im here")
            slider_max = driver.find_elements(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/section/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button")
            if len(slider_max) > 0:
                found_filter = True
                slider_max = slider_max[0]
                


                min_price_elem = driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/section/div[2]/div/div[1]/div[1]/label/div[2]/div/input")
                max_price_elem = driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/section/div[2]/div/div[1]/div[3]/label/div[2]/div/input")


        if not found_filter:
            slider_max = driver.find_elements(By.XPATH,"/html/body/div[9]/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/section/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button")
            if len(slider_max) > 0:
                max_price_elem = driver.find_element(By.XPATH, "/html/body/div[9]/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/section/div[2]/div/div[1]/div[3]/label/div[2]/div/input")
                min_price_elem = driver.find_element(By.XPATH, "/html/body/div[9]/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/section/div[2]/div/div[1]/div[1]/label/div[2]/div/input")       


        if not found_filter:
            #print("yea")
            slider_max = driver.find_elements(By.XPATH,"/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/main/div/div/div/div/section/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button")
            if len(slider_max) > 0:
                found_filter = True
                slider_max = slider_max[0]
                max_price_elem = driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/main/div[2]/div/div/div/section/div[2]/div/div[1]/div[3]/label/div[2]/div/input")
                #"/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/div/div/div[1]/div/section/div[2]/div/div[1]/div[1]/label/div[2]/div/input")
                min_price_elem = driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/main/div[2]/div/div/div/section/div[2]/div/div[1]/div[1]/label/div[2]/div/input")

        #"/html/body/div/div/section/div/div/div/div/div/div/div/div/div/div/div/section/div/div/div/div/div/div/div[2]/button"
        if not found_filter:
            slider_max = driver.find_elements(By.XPATH, "/html/body/div/div/section/div/div/div/div/div/div/div/div/div/div/div/section/div/div/div/div/div/div/div/button")
            if len(slider_max) > 0: # new layout
                print("new layout")
                found_filter = True
                slider_max = slider_max[0]
                min_price_elem = driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div/div/div/div/div/div/div/div/div/section/div/div/div/div[1]/label/div/div/input")
                
                max_price_elem = driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div/div/div/div/div/div/div/div/div/section/div/div/div/div[3]/label/div/div/input")

        if not found_filter:
            # there are two different layouts which seem random ... this checks for which elements to search for 
            #is_new_elem = driver.find_elements(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/section/div/div[2]/div[2]/div[1]/div[1]/div[1]/div/button/span")                                     
            slider_max = driver.find_elements(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/div/div/div/section/div[2]/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/button")
            # "/html/body/div/div/section/div/div/div[2]/div/div[2]/div/div/main/div[2]/div/div/div/div/section/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button"
            if len(slider_max) > 0: # new layout
                found_filter = True
                #slider_max = driver.find_element(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/div/div/div/section/div[2]/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/button")
                slider_max = slider_max[0]                                     
                min_price_elem = driver.find_element(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/div/div/div/section/div[2]/div/div/div/div[2]/div/div[2]/div[1]/label/div[2]/div/input")
                max_price_elem = driver.find_element(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/div/div/div/section/div[2]/div/div/div/div[2]/div/div[2]/div[3]/label/div[2]/div/input")
            
        #"/html/body/div/div/section/div/div/div/div/div/div/div/main/div/div/div/div/div/div/section/div/div/div/div/div/div/div/div/label/div[2]/div/input
        
        if not found_filter:
            # there are two different layouts which seem random ... this checks for which elements to search for 
            #is_new_elem = driver.find_elements(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/section/div/div[2]/div[2]/div[1]/div[1]/div[1]/div/button/span")                                     
            slider_max = driver.find_elements(By.XPATH, "/html/body/div/div/section/div/div/div/div/div/div/div/main/div/div/div/div/div/div/section/div/div/div/div/div/div/div/div/div/div[2]/button")
                                                        
                                                        #"/html/body/div[9]/div/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/div/div/div/section/div[2]/div/div/div/div[2]/div/div[2]/div[3]/label/div[2]/div/input"
            if len(slider_max) > 0: # new layout
                #"/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/div/div/div/section/div[2]/div/div/div/div[2]/div/div[2]/div[1]/label/div[2]/div/input")
                #"/html/body/div/div/section/div/div/div/div/div/div/div/main/div/div/div/div/section/div/div/div[1]/div[3]/label/div[2]/div/input
                min_price_elem = driver.find_element(By.XPATH, "/html/body/div/div/section/div/div/div/div/div/div/div/main/div/div/div/div/div/div/section/div/div/div/div/div/div/div/div[1]/label/div[2]/div/input")
                max_price_elem = driver.find_element(By.XPATH,  "/html/body/div/div/section/div/div/div/div/div/div/div/main/div/div/div/div/div/div/section/div/div/div/div/div/div/div/div[3]/label/div[2]/div/input")
                found_filter = True

        if not found_filter:   
            print(":()")                                    
            slider_max = driver.find_elements(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[2]/div/div/div/div/section/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button")                      
            if len(slider_max) > 0: # new layout
                slider_max = slider_max[0]  
                min_price_elem = driver.find_element(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[2]/div/div/div/div/section/div[2]/div/div[1]/div[1]/label/div[2]/div/input")
                max_price_elem = driver.find_element(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[2]/div/div/main/div[2]/div/div/div/div/section/div[2]/div/div[1]/div[3]/label/div[2]/div/input")

        try:
            min_price = max_price_elem.get_attribute('value')
        except:
            pass

        if not found_filter:
            print("trying again here")
            time.sleep(5)
            driver.close()
            time.sleep(1)
            driver = webdriver.Chrome(service=SERVICE, options=OPTIONS)
            prices, texts = get_houses_in_bin(driver,  city, checkin, checkout, do_print=True)
            return prices, texts




        if is_first:
            move.click_and_hold(slider_max).move_by_offset(-300, 0).release().perform()
            min_price = min_price_elem.get_attribute('value')
            is_first = False
        else: 
            for i in range(0, 5):
                min_price_elem.send_keys(Keys.BACKSPACE)
                time.sleep(0.1)
            min_price_elem.send_keys(int(min_price) + 1)
            min_price = max_price_elem.get_attribute('value')

            move.click_and_hold(slider_max).move_by_offset(150, 0).release().perform()

        time.sleep(5)
        # filter loop
        itt = 0
        firstHEre = True
        while not found and itt < 200:
            
            itt += 1

            # reading the button with the number of stays in search
            stays = num_filered.text.strip()
            #stays = 
            if stays == "Ingen ledige boliger":
                stays_count = 0
            elif stays == "Vis over 1.000 boliger":
                stays_count = 1001
            elif "over 1000" in stays.lower():
                stays_count = 1001
            #elif len(stays) < 11:
            #    return prices, texts
            else:
                vis_split = stays.split("Vis ")
                if len(vis_split) < 1:
                    print(stays)
                    return prices, texts

                stays = stays.split("Vis ")[1]
                stays = stays.split(" ophold")[0].strip()
                stays = stays.split(" steder")[0].strip()
                stays = stays.replace(".","")
                try:
                    stays_count = int(stays)
                except:
                    # bad number
                    print(stays)
                    return prices, texts

            if (stays_count <= 269): # and (stays_count >= 200):
                found = True
                break
            
            #print("here")
            # this is a bit of magic to find a price with approximatly 250 stays
            # we need around 200 because the algorithm only shows 269 at the time
            # we safe the maximum price and use that in the next iteration
            loc_x_fac = (slider_max.location['x'] / 680) ** 3 # use to accelerate in the ends if not, will spent a lot of time there

            price_now = max_price_elem.get_attribute('value') 
            price_now = int(price_now.split("+")[0].strip()) 
            price_diff = price_now - int(min_price.split("+")[0].strip())
            if (itt < 8) and (price_diff > 100):

                #if itt > 80:
                #    offset = -30
                if stays_count < 400:
                    offset = -5
                elif (stays_count > 269):
                    offset = - (stays_count / 269 ) ** 1.2 * 10 * loc_x_fac
                    offset = np.fmin(-10, offset)
                    #move.click_and_hold(slider_max).move_by_offset(offset, 0).release().perform()
                move.click_and_hold(slider_max).move_by_offset(offset, 0).release().perform()
                loc_x = slider_max.location['x']
                time.sleep(2)
                #else:
                #    offset = (stays_count / 269) ** 1.2 * 10 * loc_x_fac
            else:
                off = 0
                if firstHEre:
                    off = 10
                firstHEre = False

                if price_diff < 0: # something is wrong
                    price_now = price_now + np.abs(price_diff) + 10
                elif price_diff <= 5:
                    break
                elif price_diff < 10:
                    price_now = price_now - 2
                elif price_diff < 30:
                    price_now = price_now - 5
                elif price_diff < 200:
                    price_now = price_now - 15
                else:
                    price_now = price_now - int((price_diff / 2))


                price_now = price_now + off

                for i in range(0, 8):
                    max_price_elem.send_keys(Keys.BACKSPACE)
                    #time.sleep(0.1)
                max_price_elem.send_keys(price_now)
                time.sleep(1)
                max_price_elem.send_keys(Keys.TAB)
                time.sleep(2)
                #price_it -= 30
                
            
            time.sleep(5)           

        
        if do_print:
            min_price_dis = min_price
            if first_print:
                min_price_dis = 0
           
            first_print = False
            print(f"Found {stays_count} stays in the range {min_price_dis} - {max_price_elem.get_attribute('value')}")

        min_price = max_price_elem.get_attribute('value')
        
        num_filered.click()
        time.sleep(1)

        if stays_count < 30:
            if do_print:
                print("skipped, not enough stays")
                break

        # getting links and prices to all houses in the range found above
        p, t = get_house_prices(driver)
        prices += p
        texts += t  

        # last one
        if "+" in min_price:
            break
        
        # very few stays, might skew average A BIT to skip
        #if min_price > 3000:
        #    break
        
        price_check = int(min_price.split("+")[0].strip())
        if price_check > 10000:
            if do_print:
                print("skipped price too high")
            break


    return prices, texts


# 
def get_house_prices(driver):
    prices = []
    texts = []

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        next_but = driver.find_elements(By.CSS_SELECTOR, "#site-content > div > div.p1arl239.dir.dir-ltr > div > div > div > nav > div > a.l1ovpqvx.c1ytbx3a.dir.dir-ltr")
        if len(next_but) == 0:
            next_but = driver.find_elements(By.CSS_SELECTOR, "#site-content > div > div > div > div > div > nav > div > a.l1ovpqvx.c1ytbx3a.dir.dir-ltr")

        postings = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div/div[2]/main/div[2]/div/div[2]/div/div/div/div/div[1]/div/div/div[2]/div/div/div/div[1]")
                                                  


        for posting in postings:
            
            link = posting.find_elements(By.XPATH, "a")[0].get_attribute("href")
            price = posting.find_elements(By.XPATH, "div/div[2]/div/div/div/span")[0].text

            p = price.split(" kr DKK")[0].strip()
            #p = price.split(" kr DKK")[0]

            p = p.replace(".", "")
            try:
                p = int(p)
            except:
                link = ""
                price = -1
                #print(price)
                #print(f"error with price on {link}")
                #continue
            
            texts.append(link)
            prices.append(p)

        if len(next_but) == 0:
            break

        next_but[0].click()

        time.sleep(1)
        
    return prices, texts





# getting extra info from specfic place (link to place)
def get_place_info(url, driver_in = None, do_cookies = True):

    driver = driver_in
    if driver is None:
        driver =webdriver.Chrome(service=SERVICE, options=OPTIONS)

    driver.get(url)

    if do_cookies:
        time.sleep(1.0)
        itt = 0
        translate_button = None
        while itt < 20:
            itt += 1
                                                              
            translate_button = driver.find_elements(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[1]/button")
            #""
            if len(translate_button) > 0:
                translate_button[0].click()
                time.sleep(1)
                break
            
            time.sleep(0.1)
            translate_button = driver.find_elements(By.XPATH, "/html/body/div/div/section/div/div/div[2]/div/div[1]/button")
            if len(translate_button) > 0:
                translate_button[0].click()
                time.sleep(1)
                break

            #time.sleep(0.1)

    #if not translate_button:

    time.sleep(0.5)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(0.5)

                                               
    head_info = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[1]/div/div[1]/div/div/section/div/div/div[1]/ol/li")                              
    if len(head_info) == 0:
        head_info = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[1]/div/div[1]/div/div/div/ul/li/div[2]/div")
    _info = ""

    if len(head_info) == 0:
        head_info = driver.find_elements(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/main/div/div/div/div/div/div/div/div/div/div/ul/li/div/div")
    
    _info = ""
    for info in head_info:
        _info += info.text + "||"

    location = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[5]/div/div/div/div[2]/section/div/div/div/div/div[1]/h3")
    if len(location) > 0:
        location = location[0].text

    #rating = driver.find_elements(By.XPATH, "/html/body/div/div/div/div/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div[1]/div[2]/span/span[3]")
    #if len(rating) == 0:
    rating = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[4]/div/div/div/div[2]/section/div[1]/span[2]/h2/div/span")                                                
    if len(rating) == 0:
        rating = driver.find_elements(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/main/div/div/div/div/div/div/div/section/div/span/h2/span")

    if len(rating) > 0:
        rating = rating[0].text

    #price = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div[1]/div[1]/div/span/div/span[1]/text()[1]")
    price = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[2]/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div[1]/div[1]/div/span/div/span[1]")
    if len(price) > 0:
        price = price[0].text

    info_but = driver.find_elements(By.XPATH, "/html/body/div/div/div/div[1]/div/div[2]/div/div/div/div[1]/main/div/div[1]/div[3]/div/div[1]/div/div/div/div[2]/section/div[4]/button")
    
    if len(info_but) == 0:
        info_but = driver.find_elements(By.XPATH, "/html/body/div/div/div/div[1]/div/div[2]/div/div/div/div/div/main/div/div[1]/div[9]/div/div/div/div[2]/section/div[4]/button")

    if len(info_but) == 0:
        info_but = driver.find_elements(By.XPATH, "/html/body/div/div/div/div/div/div/div/div/div/div/div/main/div/div/div[9]/div/div/div/div[2]/section/div/button")

    
    url_info = url.split("?")[0] + "/amenities"

    driver.get(url_info)

    time.sleep(1)

    """ 
    for i in range(20):
        info_title = driver.find_elements(By.XPATH, "/html/body/div/section/div/div/div[2]/div/div[3]/div/div/div/section/div[1]/h2")
        if len(info_title) > 0:
            break
        time.sleep(0.1)
    """
    
    for i in range(20):    
        features = driver.find_elements(By.XPATH, "/html/body/div/section/div/div/div/div/div/div/div/div/section/div/div/div")

        if len(features) > 0:
            break
        
        features = driver.find_elements(By.XPATH, "/html/body/div/div/section/div/div/div/div/div/div/div/div/section/div/div/div")


        time.sleep(0.1)


    # remove not included
    features_text = ""
    for i, f in enumerate(features):
        
        #sub = f.find_elements(By.XPATH,"h3")
        #if len(sub) > 0:
        #    print(sub[0].text)

        features_text += f.text + "||"
        if "Not included" in f.text:
            break
        elif "Unavailable" in f.text:
            break


    if not driver_in:
        driver.close()

    #if len(_info) == 0:
    #    _info = 

    return _info, location, rating, price, features_text



def get_city_prices_avg(driver, city, checkin, checkout):

    url = f"""https://www.airbnb.dk/s/{city}/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-09-01&monthly_length=3&price_filter_input_type=0&price_filter_num_nights=5&channel=EXPLORE&date_picker_type=calendar&checkin={checkin}&checkout={checkout}&source=structured_search_input_header&search_type=filter_change"""

    print(url)

    driver.get(url)

    time.sleep(1)

    prices = []
    texts = []
                                              
    try:
        filter_but = driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[3]/div[1]/div[2]/div/div/div/div/div[2]/div/div/button")
        filter_but.click()
    except:
        filter_but = driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div[1]/div/div[3]/div[1]/div[2]/div/div/div/div/div/div/div[2]/div/div/button")
        filter_but.click()

    time.sleep(3)

                                             
    avg_price = driver.find_elements(By.XPATH, "/html/body/div[9]/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/div/div/div/section/div[2]/div/div/div/div[1]")

    if len(avg_price) == 0:
        avg_price = driver.find_elements(By.XPATH, "/html/body/div[9]/div/section/div/div/div[2]/div/div[2]/div/div/main/div[1]/div/div/div/div/div/section/div[2]/div/div/div/div[1]")

    if len(avg_price) > 0:
        avg_price = avg_price[0]

    avg_price = avg_price.text.split("per nat er ")[1]
    avg_price = avg_price.split(" kr DKK")[0]   
    avg_price = avg_price.replace(".","") # dot for thousandnt()
    avg_price = float(avg_price)

    return avg_price

