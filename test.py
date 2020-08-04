from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from selenium.webdriver.chrome.options import Options
import re

no_nutrition_url = 'https://www.kroger.com/p/kroger-grade-a-large-eggs/0001111060933' 
url = 'https://www.kroger.com/p/goldfish-flavor-blasted-xtra-cheddar-baked-snack-crackers/0001410008548' 
url2 = 'https://www.kroger.com/p/ball-park-hot-dog-buns-8-count/0005040075116'

#Initialize WebDriver
# options = Options()
# options.headless = True
driver = webdriver.Chrome(executable_path='./chromedriver')
try:
    
    driver.get(url)
    try:
        #Confirm the location (otherwise other buttons won't work)
        confirm_xpath = '/html/body/div[1]/div[2]/div[2]/div[3]/div/div/div[6]/button[1]'
        confirm_loc_btn = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.XPATH,confirm_xpath))
        )
        confirm_loc_btn.click()
        print('Location Confirmed')
    except TimeoutException:
        print('No Location Btn')

    try:
        #Select the nutrition btn to view the nutrition info
        nutrition_xpath = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/div/button[2]'
        nutritionBtn = WebDriverWait(driver,7).until(
            EC.presence_of_element_located((By.XPATH,nutrition_xpath))
        )
        nutritionBtn.click()
        print('Nutrition Btn Clicked')

        #xpaths collected from inspector
        calories_xpath = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[2]/div/div/div[2]/div[1]/div/div[5]/span[2]'
        fat_xpath = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[2]/div/div/div[2]/div[1]/div/div[7]/div[1]/span[1]' 
        carbs_xpath = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[2]/div/div/div[2]/div[1]/div/div[10]/div[1]/span[1]'
        protein_xpath = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[2]/div/div/div[2]/div[1]/div/div[11]/div[1]/span[1]'

        #Collect raw data
        calories = WebDriverWait(driver,4).until(
            EC.presence_of_element_located((By.XPATH,calories_xpath))
        ).text 
    
        fat = driver.find_element_by_xpath(fat_xpath).text
        carbs = driver.find_element_by_xpath(carbs_xpath).text
        protein = driver.find_element_by_xpath(protein_xpath).text

        #Process the data into correct format (int)
        nums = re.compile('\d+\.?\d?',re.IGNORECASE)
        calories = round(float(nums.findall(calories)[0]))
        fat = round(float(nums.findall(fat)[0]))
        carbs = round(float(nums.findall(carbs)[0]))
        protein = round(float(nums.findall(protein)[0]))

        print('Calories:',calories)
        print('Total Fat:',fat)
        print('Total Carbs:',carbs)
        print('Protein:',protein)

    except TimeoutException:
        print('No Nutrition Info')

finally:
    driver.quit()