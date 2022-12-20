# This is a sample Python script.
links = ["https://ag.wd3.myworkdayjobs.com/en-US/Airbus/job/Blagnac---Wings-Campus/Stage-en-gestion-de-projet--f-h-_JR10149650"]
from selenium import webdriver
import time
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import path
import traceback
import link_getter
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def is_stage():
    get_p1

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
def press_button(path,sleep,xpath):
    if xpath:
        # WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.xpath, path)))
        button = driver.find_element("xpath",path)
        time.sleep(1)
        button.click()
        time.sleep(sleep)

def calendar(driver,path):
    button = driver.find_element("xpath",path)
    time.sleep(1)
    button.click()
    time.sleep(0.25)
    ActionChains(driver).send_keys("06101999").perform()
def press_button_move(path,sleep,xpath):
    if xpath:
        button = driver.find_element("xpath",path)
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView();", button)
        time.sleep(0.5)
        button.click()
        time.sleep(sleep)
def add_text(text,path,sleep,xpath):
    if xpath:
        button = driver.find_element("xpath",path)
        time.sleep(1)

        button.send_keys(text)
        time.sleep(sleep)
def apply_stage(driver):
    add_text("M1",path.semester_level_path,2,True)
    add_text("UNIVERSITÉ TOULOUSE III - PAUL SABATIER",path.uni_name_path,2,True)
    add_text("Master’s In Computer Science for Aerospace",path.course_path,2,True)
    add_text("06/24",path.finish_studies ,2,True)

    press_button(path.contract_type ,5,True)
    press_button(path.drop_dwn_path ,5,True)
    add_text("/",path.third_part_financ,2,True)
    press_button(path.mand  ,5,True)
    add_text("1/1/2023 - 1/9/2023",path.availb ,2,True)
    add_text("Until 23/9/2023",path.dur_int  ,2,True)


    press_button(path.eng_rate ,5,True)
    press_button(path.fluent ,5,True)
    press_button(path.fen_rate ,5,True)
    press_button(path.intm ,5,True)
def final_page(driver):

    button = driver.find_element("xpath",path.add_nat)

    actions = ActionChains(driver)
    actions.move_to_element(button).perform()


    calendar(driver,path.bd)
    # press_button(path.gend,1,True)
    # press_button(path.male,1,True)


    press_button(path.nation,1,True)
    press_button(path.liban,2,True)
    press_button_move(path.accept,1,True)
    press_button(path.save_cont_path,9,True)
def apply_website(driver):
    time.sleep(3)
    button = driver.find_element("xpath",path.apply_button_path)
    time.sleep(1)
    button.click()

    time.sleep(1)
    button = driver.find_element("xpath",path.use_last_button_path)
    time.sleep(1)
    button.click()

    time.sleep(9)

    try:

        x = driver.find_element("xpath",path.signin2_xpath)
        x.click()
        print("sign in twice worked")
    except:
        print("tried to sign in twice but failed")









    press_button(path.how_hear_path,2,True)
    press_button(path.career_website_button_path,2,True)
    press_button(path.save_cont_path,9,True)
    press_button(path.save_cont_path,9,True)
    apply_stage(driver)
    # import pdb; pdb.set_trace()
    press_button(path.save_cont_path,5,True)
    final_page(driver)
    press_button(path.submit,5,True)


def sign_in(driver):
    button = driver.find_element("xpath",path.signin_xpath)
    time.sleep(1)
    button.click()
    button = driver.find_element("xpath",path.signin_xpath)
    time.sleep(1)
    button.click()
    time.sleep(1)
    button = driver.find_element("xpath",path.signin2_xpath)
    time.sleep(1)
    button.click()
# Press the green button in the gutter to run the script.
if __name__ == '__main__':



    file_object = open('missed_links.txt', 'a')
    file = open('succ_links.txt', 'a')
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=C:\\Users\\moudimash\\Documents\\Selenium")
    options.add_argument("disable-infobars");
    driver = webdriver.Chrome(executable_path=r'./chromedriver',chrome_options=options)
        # options.add_argument('--profile-directory=Profile 4')
    links = link_getter.get_links()
    x = driver.get(links[1])
    time.sleep(10)
    sign_in(driver)
    i = 0
    try:
        for link in links:
            if i > 0:
                break
            try:
                x = driver.get(link)
                time.sleep(10)

                apply_website(driver)
                file.write(link+"\n")
            except Exception as err:
                file_object.write(link+"\n")
                traceback.print_exc()
                print(err)
                # import pdb; pdb.set_trace()
                # driver.quit()
    finally:
        driver.quit()
