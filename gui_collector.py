import pyautogui as gui
import csv
from time import sleep
import pyperclip

gui.FAILSAFE = True
'''
searchbar = (-1747,-222)
nutritionBtn = (-1518,740)
calories = (-1658,140)

fat = (-1815,154)
carbs = (-1750,295)
protein = (-1827,354)
'''
#Positions for Full Screen on MacBook Pro Monitor
searchBar = (147,59)
nutritionBtn = (414,469)
calories = (295,228)
fat = (117,276)
carbs = (184,417)
protein = (106,475)

#Search & Load Page
gui.click(searchBar[0],searchBar[1])
gui.typewrite('https://www.kroger.com/p/goldfish-flavor-blasted-xtra-cheddar-baked-snack-crackers/0001410008548')
gui.typewrite(['enter'])
sleep(10)

#Click Nutrition Button
gui.scroll(-10)
sleep(2)
gui.click(nutritionBtn[0],nutritionBtn[1])
sleep(4)
gui.scroll(-10)
print('Nutrition Btn Clicked')

gui.doubleClick(calories[0],calories[1])
gui.hotkey('command','c')
print(f'{pyperclip.paste()} Calories')
gui.doubleClick(fat[0],fat[1])
gui.hotkey('command','c')
print(f'{pyperclip.paste()} g of fat')
gui.doubleClick(carbs[0],carbs[1])
gui.hotkey('command','c')
print(f'{pyperclip.paste()} g of carbs')
gui.doubleClick(protein[0],protein[1])
gui.hotkey('command','c')
print(f'{pyperclip.paste()} g of protein')

class KrogerGuiCollector:
    def __init__(self,input_file,output_file):
        self.input_file = input_file
        self.output_file = output_file

    def main(self):
        with open(self.input_file,'r') as f1, open(self.output_file,'w') as f2:
            reader, writer = csv.reader(f1),csv.writer(f2)

            next(reader)
            writer.writerow(['krogerUrl','calories'])

            for row in reader:
                url = row[0]
                info = self.scrape(url)
                
    def scrape(self,url):
        return 0 
