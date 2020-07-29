from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,NoSuchElementException,WebDriverException
import requests
import csv
import re

class Scraper:
    def __init__(self,input_file,output_file):
        self.input_file = input_file
        self.output_file = output_file
    
    def scrape_nutrition(self,url):
        #Initialize WebDriver
        try:
            options = Options()
            options.headless = True
            path = './geckodriver'
            driver = webdriver.Firefox(executable_path=path,options=options)
        except WebDriverException:
            self.scrape_nutrition(url) 

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
                confirm_loc_btn = WebDriverWait(driver,7).until(
                    EC.presence_of_element_located((By.XPATH,confirm_xpath))
                )
                confirm_loc_btn.click()
                print('Location Confirmed')
            except TimeoutException:
                pass

            try: 
                #Select the nutrition view to render the nutrition info
                nutrition_xpath = '/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div[3]/div/button[2]'
                nutritionBtn = WebDriverWait(driver,4).until(
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
                calories = driver.find_element_by_xpath(calories_xpath).text
                fat = driver.find_element_by_xpath(fat_xpath).text
                carbs = driver.find_element_by_xpath(carbs_xpath).text
                protein = driver.find_element_by_xpath(protein_xpath).text

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

                #print('Calories:',calories)
                #print('Total Fat:',fat)
                #print('Total Carbs:',carbs)
                #print('Protein:',protein)

                return info 
            
            except (TimeoutException,NoSuchElementException):
                #print('No Nutrition Info')
                return info

        except TimeoutException:
            #print('Failed Get Request')
            return info
            
        finally:
            driver.quit() 
    
    def call_api(self,upcUuid,info):
        status = []
        info['caloriesUnits'] = 'cal' 
        header = {'x-access-token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ7XCJ1dWlkXCI6XCJhMjEyMzg5NS1lZTQwLTQzMWItODA3ZC01YzBjMGQ4YWM0ZTRcIixcImVtYWlsXCI6XCJ2am1leWVyMjBAZ21haWwuY29tXCJ9IiwiaWF0IjoxNTkzNjI1ODk1MDk0LCJleHAiOjE1OTYyMTc4OTUwOTR9.8V0INxhF_B-l4JvS7GRaSsae8GKzbZHGVeso6Ts7STo'}       
        patch = requests.patch(f'https://api.foodforest.io/v2/super-admin/upcs/{upcUuid}',headers=header,data=info)
        status.append(patch.status_code)
        
        get = requests.get(f'https://api.foodforest.io/v2/admin/inventory-items/?upcUuid={upcUuid}',headers=header)
        IIUuids = []
        if get.status_code == 200:
            data = get.json()
            if 'results' in data:
                results = data['results']
                if len(results) > 0:
                    for obj in results:
                        if 'uuid' in obj: IIUuids.append(obj['uuid'])
        for uuid in IIUuids:
            patchII = requests.patch(f'https://api.foodforest.io/v2/admin/inventory-items/{uuid}',headers=header,data=info)
            status.append(patchII.status_code)

        return status


    def main(self): 
        with open(self.input_file,'r') as f1, open(self.output_file,'w') as f2:
            reader, writer = csv.reader(f1), csv.writer(f2)

            next(reader)
            writer.writerow(['upcUuid','krogerUrl','fat','fatUnits','carbs','carbsUnits','protein','proteinUnits','calories','caloriesUnits'])

            for val,line in enumerate(reader,1):
                upcUuid, url = line[0],line[1]
                info = self.scrape_nutrition(url)
                empty = True
                for item in list(info.values()):
                    if item is not None:
                        empty = False
                        break 

                if not empty:
                    status = self.call_api(upcUuid,info)
                    print(info)
                    print(status)
                    print(f'{val}: {upcUuid} Updated')
                else:
                    print(info)
                    print(f'{val}: {upcUuid} Not updated')
                
                writer.writerow([upcUuid,url,info['fat'],'g',info['carbs'],'g',info['protein'],'g',info['calories'],'cal'])

if __name__ == '__main__':
    test = Scraper('krogerUrls.csv','krogerNF.csv')
    test.main()