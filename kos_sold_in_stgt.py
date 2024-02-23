from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import InvalidArgumentException
import time, datetime, re

MOST_TRADED_URL = 'https://www.boerse-stuttgart.de/de-de/tools/produktsuche/umsatzspitzenreiter/?category=5111'
BASE_KO_URL = 'https://www.boerse-stuttgart.de/de-de/produkte/hebelprodukte/knock-out-produkte/stuttgart/'
SALES = '/times-and-sales'
MIN_PRICE = 2
MAX_PRICE = 20
DATE_FORMAT = '%d.%m.%Y'
TIME_FORMAT = '%H:%M'

class BoerseStgt(Chrome):
    def __init__(self):
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        Chrome.__init__(self, options = self.options)
        self.get('https://www.boerse-stuttgart.de')
        # close cookie dialog
        self.find_element(By.CLASS_NAME, 'js-bsg-cookie-layer__deny').click()

    def getKOs(self):
        '''
        Fetches a Dictionary of the most traded knock-out certificates at the stock exchange Stuttgart, DE.\n
        returns dict('ID': 'description')    
        '''
        self.get(MOST_TRADED_URL)

        # sort rows in table by their description
        sortTableBtn = self.find_elements(By.CLASS_NAME, 'tablesaw-sortable-btn')
        sortTableBtn[1].click()

        table = self.find_element(By.CLASS_NAME, 'bsg-table__tbody')
        rows = table.find_elements(By.CLASS_NAME, 'bsg-table__tr')
        print('Found %s rows in the table' % len(rows))

        # Extract table entries and store them in a dict
        certDict = {}
        for row in rows:
            certPrice = row.find_element(By.XPATH, 'td[4]').get_attribute('innerText')
            certPrice = re.search(r'^\d+(,\d+)?', certPrice).group()
            certPrice = float(certPrice.replace(',','.'))
            if not(MIN_PRICE <= certPrice <= MAX_PRICE): continue
            certID = row.find_element(By.CLASS_NAME, 'bsg-link__label').get_attribute('innerText')
            # get name of certificate
            certDict[certID] = row.find_element(By.XPATH, 'td[3]').get_attribute('innerText')
        return certDict
        
    def inspectKo(self, id: str, date: datetime.date, startTime: datetime.time, endTime: datetime.time):
        '''
        Extracts the sales for a given knock-out certificate at the stock exchange Stuttgart, DE.\n
        Sales are grouped by volume, i.e. the amount of traded certificates at the time.\n
        Returns dict('volume': [(datetime0, price0), (datetime1, price1), ...])
        '''
        self.__getSalesPages(id)
        return self.__getSales(id, date, startTime, endTime)

    def __getSalesPages(self, *ids):
        '''
        Opens the 'Times and Sales'-page for each given id (i.e. the WKN) in a seperate window. By navigating these windows, the pages can  further be dealt with.
        '''
        for id in ids:
            if len(id) != 6 or not id.isalnum():
                raise InvalidArgumentException("Invalid WKN '%s'. WKNs must be alphanumeric and 6 characters in length." % id)
            if id not in self.window_handles:
                url = BASE_KO_URL + id + SALES
                self.execute_script("window.open('{}', '{}');".format(url, id))
    
    def __getSales(self, id: str, date: datetime.date, startTime: datetime.time, endTime: datetime.time):
        '''
        Gets the sales for a given knock-out certificate at the stock exchange Stuttgart, DE.\n
        Sales are grouped by volume, i.e. the amount of traded certificates at the time.\n
        Returns dict('volume': [(datetime0, price0), (datetime1, price1), ...])
        '''
        if BASE_KO_URL + id + SALES != self.current_url:
            self.switch_to.window(id)
        
        # set date
        self.find_element(By.ID, 'bsg-filters-btn-bgs-range-filter-2').click()
        dateInput = self.find_element(By.ID, 'bsg-date-range-input-3')
        dateInput.clear()
        dateInput.send_keys(date.strftime(DATE_FORMAT))
        self.execute_script("arguments[0].click();", WebDriverWait(self, 20) \
            .until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'bsg-dropdown__btn-apply'))))
        
        # set time
        startTimeInput = self.find_element(By.ID, 'datepicker-undefined-4')
        startTimeInput.clear()
        startTimeInput.send_keys(startTime.strftime(TIME_FORMAT) + '\n')

        endTimeInput = self.find_element(By.ID, 'datepicker-undefined-5')
        endTimeInput.clear()
        endTimeInput.send_keys(endTime.strftime(TIME_FORMAT) + '\n')
        
        # wait for data loading to finish
        time.sleep(2)
        WebDriverWait(self, 30).until_not(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'bsg-table--loading')))
        time.sleep(2)

        table = self.find_element(By.CLASS_NAME, 'bsg-table__tbody')
        rows = table.find_elements(By.CLASS_NAME, 'bsg-table__tr')
        print('Found %s rows in the table' % len(rows))

        # Extract table entries and store them in a dict
        salesDict = {} 
        for row in rows:
            volume = int(row.find_element(By.XPATH, 'td[4]').get_attribute('innerText').replace('.', ''))
            if volume:
                timestamp = datetime.time.fromisoformat(row.find_element(By.XPATH, 'td[2]').get_attribute('innerText')[:8])
                timestamp = datetime.datetime.combine(date, timestamp)
                price = row.find_element(By.XPATH, 'td[3]').get_attribute('innerText')
                price = re.search(r'^\d+(,\d+)?', price).group()
                price = float(price.replace(',','.'))
                if volume in salesDict:
                    salesDict[volume].append(dict(timestamp= timestamp, price= price))
                else:
                    salesDict[volume] = [dict(timestamp= timestamp, price= price)]
        # Only return the sales at a certain volume if the number of sales is uneven 
        return {key: entries for key, entries in salesDict.items() if len(entries) % 2 != 0}

if __name__ == '__main__':
    # test for compatible driver versions
    options = Options()
    options.add_argument('--headless')
    driver= Chrome(options=options)
    browserVersion = driver.capabilities['browserVersion']
    chromedriverVersion = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
    print('Browser version:\t' + browserVersion)
    print('Chromedriver version:\t' + chromedriverVersion)
    if browserVersion[0:2] != chromedriverVersion[0:2]: 
        print("please download correct chromedriver version")
    driver.close()

    # test functions
    date = datetime.date.fromisoformat('2023-03-24')
    startTime = datetime.time.fromisoformat('08:00')
    endTime = datetime.time.fromisoformat('22:00')
    driver = BoerseStgt()
    #kos = ['MB2124', 'HG8Y8G', 'UK7GS3', 'UK5PMQ']
    kos = driver.getKOs()
    for count, ko in enumerate(kos):
        #if count == 20: break
        sales = driver.inspectKo(ko, date, startTime, endTime)
        if sales:
            print('ID: "{}"\tName: "{}"'.format(ko, kos[ko]))
            for volume in sales:
                print('Trades of %d pieces:' % volume)
                for sale in sales[volume]:
                    print((sale[0], sale[1]))