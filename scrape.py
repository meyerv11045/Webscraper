from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,NoSuchElementException,WebDriverException
import csv
import re

class Scraper:
    def __init__(self,input_file,output_file):
        self.input_file = input_file
        self.output_file = output_file

    def init_webdriver(self,try_again=0):
        """ Initializes and returns a new webdriver object. If there are errors
            it recursively trys again for 5 trys.
        Args:
            try_again (int, optional): Used by function for recursively trying again. Defaults to 0.

        Returns:
            webdriver object: Chrome webdriver operating in headful mode (headless doesn't work w/ kroger)
        """
        try:
            driver = webdriver.Chrome(executable_path='./chromedriver')
            return driver
        except WebDriverException:
            print('Connection Refused ... Trying Again')
            if try_again < 5:
                return self.init_webdriver(try_again= (try_again + 1))
            else: 
                return None

class KrogerNutritionFacts(Scraper):
    def __init__(self,input_file,output_file):
        super().__init__(input_file,output_file)

    @staticmethod
    def click_confirm_location(driver):
        """ Clicks Confirm Location button that is overlayed
            so that the other buttons on the page work

        Args:
            driver (webdriver object): On kroger product landing page 
        """
        try:
            confirm_xpath = '/html/body/div[1]/div[2]/div[2]/div[3]/div/div/div[6]/button[1]'
            confirm_loc_btn = WebDriverWait(driver,6).until(
                EC.presence_of_element_located((By.XPATH,confirm_xpath))
            )
            confirm_loc_btn.click()
            print('Location Confirmed')
        except TimeoutException:
            print('No Confirmation Button')

    @staticmethod
    def get_nutrition_from_xpaths(driver,calories_xpath,fat_xpath,carbs_xpath,protein_xpath):
        """Collects nutrition information from xpaths

        Args:
            driver (webdriver object): On kroger product page 
            *_xpath (str): xpaths to the different nutrition elements

        Returns:
            list: the collected nutrition info from the xpaths
        """
        calories = driver.find_element_by_xpath(calories_xpath).text
        fat = driver.find_element_by_xpath(fat_xpath).text
        carbs = driver.find_element_by_xpath(carbs_xpath).text
        protein = driver.find_element_by_xpath(protein_xpath).text

        return calories,fat,carbs,protein
    
    @staticmethod
    def click_nutrition_button(driver):
        """ Clicks the nutrition button to view the nutrition info
            on a kroger product page

        Args:
            driver (webdriver object): On kroger product page w/ confirm location btn clicked
        """
        nutrition_xpath = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/div/button[2]'
        nutritionBtn = WebDriverWait(driver,2).until(
            EC.presence_of_element_located((By.XPATH,nutrition_xpath))
        )
        nutritionBtn.click()
        print('Nutrition Btn Clicked')

    def scrape_nutrition(self,url):
        """ Scrapes nutrition info from webpage using multiple possible
            xpaths for the nutrition infos location and returns the collected
            nutrition information as a dictionary

        Args:
            url (str): Kroger product url

        Returns:
            dict: Contains collected calorie, fat, carb, and protein information
        """
        info = {
            'calories': None,
            'fat': None,
            'carbs': None,
            'protein': None
        }
        driver = self.init_webdriver()
        if driver is None: return info
        try:
            driver.get(url)
            KrogerNutritionFacts.click_confirm_location(driver)
            try:
                #Nutrition displayed on main view (No buttons to click)
                calories_xpath1 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section/div/div/div[2]/div[1]/div/div[5]/span[2]'
                fat_xpath1 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section/div/div/div[2]/div[1]/div/div[7]/div[1]/span[1]'
                carbs_xpath1 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section/div/div/div[2]/div[1]/div/div[10]/div[1]/span[1]'
                protein_xpath1 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section/div/div/div[2]/div[1]/div/div[11]/div[1]/span[1]'
                calories, fat, carbs, protein = KrogerNutritionFacts.get_nutrition_from_xpaths(driver,calories_xpath1,fat_xpath1,carbs_xpath1,protein_xpath1)
            except (TimeoutException, NoSuchElementException):
                #Nutrition Button to view Nutrition Info
                try: 
                    KrogerNutritionFacts.click_nutrition_button(driver)
                    try: #Nutrition Btn Section 2 in xpath
                        calories_xpath2 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[2]/div/div/div[2]/div[1]/div/div[5]/span[2]'             
                        fat_xpath2 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[2]/div/div/div[2]/div[1]/div/div[7]/div[1]/span[1]' 
                        carbs_xpath2 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[2]/div/div/div[2]/div[1]/div/div[10]/div[1]/span[1]'
                        protein_xpath2 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[2]/div/div/div[2]/div[1]/div/div[11]/div[1]/span[1]'
                        calories, fat, carbs, protein =  KrogerNutritionFacts.get_nutrition_from_xpaths(driver,calories_xpath2,fat_xpath2,carbs_xpath2,protein_xpath2)
                    except (TimeoutException,NoSuchElementException):
                        try: #Nutrition Btn Section 1 in xpath
                            calories_xpath3 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[1]/div/div/div[2]/div[1]/div/div[5]/span[2]'
                            fat_xpath3 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[1]/div/div/div[2]/div[1]/div/div[7]/div[1]/span[1]'
                            carbs_xpath3 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[1]/div/div/div[2]/div[1]/div/div[10]/div[1]/span[1]'
                            protein_xpath3 = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/section[1]/div/div/div[2]/div[1]/div/div[11]/div[1]/span[1]'
                            calories, fat, carbs, protein = KrogerNutritionFacts.get_nutrition_from_xpaths(driver,calories_xpath3,fat_xpath3,carbs_xpath3,protein_xpath3)
                        except (TimeoutException,NoSuchElementException):
                            print('No Nutrition Info')
                            return info
                except TimeoutException:
                    print('No Nutrition Button')
                    return info
            
            #Process the data into correct format (int)
            nums = re.compile('\d+\.?\d?',re.IGNORECASE)
            results = nums.findall(calories)
            if len(results) > 0:
                calories = round(float(results[0]))
                info['calories'] = calories
            results = nums.findall(fat)
            if len(results) > 0:
                fat = round(float(results[0]))
                info['fat'] = fat
            results = nums.findall(carbs)
            if len(results) > 0:             
                carbs = round(float(results[0]))
                info['carbs'] = carbs
            results = nums.findall(protein)
            if len(results) > 0:             
                protein = round(float(results[0]))
                info['protein'] = protein
            
            return info 
        except TimeoutException:
            print('Failed Get Request')
            return info
        finally:
            driver.quit() 
    
    def main(self):
        """ Iterates through the upcUuids and urls provided in the input csv file,
            scrapes the nutrition information, and writes it to a csv file
        """ 
        with open(self.input_file,'r') as f1, open(self.output_file,'w') as f2:
            reader, writer = csv.reader(f1), csv.writer(f2)
            next(reader)
            writer.writerow(['upcUuid','krogerUrl','fat','fatUnits','carbs','carbsUnits','protein','proteinUnits','calories','caloriesUnits'])
            for val,line in enumerate(reader,1):
                upcUuid, url = line[0],line[1] #upcUuid should be 1st col of input file and url shoudld be 2nd col 
                info = self.scrape_nutrition(url)
                print(info)
                writer.writerow([upcUuid,url,info['fat'],'g',info['carbs'],'g',info['protein'],'g',info['calories'],'cal'])
                print(f'{val}: {upcUuid} Done')
            
if __name__ == '__main__':
    input_file = input('Enter path to input csv file: ') 
    output_file = input('Enter path to output csv file')
    scraper = KrogerNutritionFacts(input_file,output_file)
    scraper.main()