from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time


def get_data(url, driver):
    '''
    Opening site and looking for ended football matches

    :param url: URL
    :param driver: webdriver
    :return: запись в файл
    '''

    wait = WebDriverWait(driver, 10)
    # making Selenium's object
    driver.get(url)
    # click on tab with football matches (use JavaScript)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'li2')))
    driver.execute_script('document.getElementsByClassName("li2")[0].getElementsByTagName("a")[0].click();')
    # max seven days
    for times in range(7):
        time.sleep(3)
        # waiting for download dynamic elements - main table with results
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table-main')))

        print('number of page: ', times)
        ended = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'soccer')))\
            .find_elements_by_class_name('soccer')
        # ended = ended[:5] # for test take 1st 5 elements
        result = []

        # take each game
        for item in ended:
            # take each block with games
            games = item.find_elements_by_class_name('stage-finished')
            for game in games:
                p_result = {}
                # get an id of current window in driver
                current = driver.current_window_handle
                # click on a game and open in new window this game (use JavaScript)
                driver.execute_script('arguments[0].getElementsByClassName("cell_aa")[0]'
                                      '.getElementsByTagName("span")[0].click()', game)

                # switch to the new window with game
                switch(driver, current)
                # use try-catch for searching goals. If have no goals - throw the TimeoutException.
                try:
                    details = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'detailMS')))
                    goals = details.find_elements_by_css_selector('.icon-box.soccer-ball')
                    match = driver.find_element_by_class_name('team-primary-content').text
                    p_result[match] = []
                    for goal in goals:
                        text = goal.find_element_by_xpath('..').text
                        p_result[match].append(text)
                    result.append(p_result)
                except TimeoutException:
                    print('got TimeoutException')

                driver.close()
                driver.switch_to_window(driver.window_handles[0])
        write_csv(result, times)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.day.yesterday'))).click()
    return True


def switch(driver, current):
    windows = driver.window_handles
    if current == windows[0]:
        driver.switch_to_window(windows[1])
    else:
        driver.switch_to_window(windows[0])


def write_csv(data, times):
    '''
    Redact results and write in .csv file.
    Take only name of match and times of goals.
    '''
    print(data)
    name = 'matches' + str(times) + '.csv'
    with open(name, 'a') as f:
        writer = csv.writer(f)
        for i in data:
            for k in i:
                match = ' '.join(re.split(r'\n', k))
                match = ''.join(re.split(r'\d{2}.\d{2}.\d{4}', match))
                match = ''.join(re.split(r'\d{2}:\d{2}', match))
                if len(i[k]) > 0:
                    goals = []
                    for goal in i[k]:
                        goals.append(''.join(re.split(r'\n', goal)))
                    goals = '\n'.join(goals)
                    writer.writerow((match, goals))
                else:
                    writer.writerow((match, '0-0'))


def main():
    url = 'https://www.myscore.ru/'
    # creating descriptor of options
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument('window-size=1920x935')

    driver = webdriver.Chrome('selenium_drivers/chromedriver', chrome_options=options)
    get_data(url, driver)
    driver.quit()


if __name__ == '__main__':
    main()


