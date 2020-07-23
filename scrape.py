from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,NoSuchElementException
import csv
import re

class Scraper:
    def __init__(self,input_file,output_file):
        self.input_file = input_file
        self.output_file = output_file
    
    def scrape_nutrition(self,url):
        #Initialize WebDriver
        options = Options()
        options.headless = True
        path = './geckodriver'
        driver = webdriver.Firefox(executable_path=path,options=options)
        
        info = {
            'calories': None,
            'fat': None,
            'carbs': None,
            'protein': None
        }

        try:
            driver.get(url)
            try: 
                #Confirm the location so other buttons work
                confirm_xpath = '/html/body/div[1]/div[2]/div[2]/div[3]/div/div/div[6]/button[1]'
                confirm_loc_btn = WebDriverWait(driver,10).until(
                    EC.presence_of_element_located((By.XPATH,confirm_xpath))
                )
                confirm_loc_btn.click()
                #print('Location Confirmed')
            except TimeoutException:
                pass

            try: 
                #Select the nutrition view to render the nutrition info
                nutrition_xpath = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/div/button[2]'
                nutritionBtn = WebDriverWait(driver,7).until(
                    EC.presence_of_element_located((By.XPATH,nutrition_xpath))
                )
                nutritionBtn.click()
                #print('Nutrition Btn Clicked')

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

                info['calories'] = calories
                info['fat'] = fat
                info['carbs'] = carbs
                info['protein'] = protein

                #print('Calories:',calories)
                #print('Total Fat:',fat)
                #print('Total Carbs:',carbs)
                #print('Protein:',protein)

                return info #filled
            
            except (TimeoutException,NoSuchElementException):
                #print('No Nutrition Info')
                return info #empty

        except TimeoutException:
            #print('Failed Get Request')
            return info #empty  

        finally:
            driver.quit() 

    def main(self):       
        with open(self.input_file,'r') as f1, open(self.output_file,'w') as f2:
            reader, writer = csv.reader(f1), csv.writer(f2)

            next(reader)
            writer.writerow(['upcUuid','krogerUrl','fat','fatUnits','carbs','carbsUnits','protein','proteinUnits','calories','caloriesUnits'])

            for val,line in enumerate(reader,1):
                upcUuid, url = line[0],line[1]
                info = self.scrape_nutrition(url)
                writer.writerow([upcUuid,url,info['fat'],'g',info['carbs'],'g',info['protein'],'g',info['calories'],'cal'])
                print(info)
                print(f'{val}: {upcUuid} Done')

if __name__ == '__main__':
    test = Scraper('kroger_urls.csv','nutrition.csv')
    test.main()