## Setup:
1. `pip install selenium`
2. Download and install the Chrome browser if not installed
3. Download chromedriver (https://chromedriver.chromium.org/downloads) and install it in the project's root directory

If there are problems w/ chromedriver, download geckodriver (for firefox) and change the webdriver in `scrape.py` from Chrome to FireFox

## Input file
The input csv file should contain two columns: 
1. The first column should be the upcUuid for the product
2. The second column should be the url for the product 

To change the nutrition fact scraper to only require a csv file with urls change line 177 in `KrogerNutritionFacts.main()` to `url = line[0]`

## Scraping More Info
To scrape different information, create a new class that inherits from the `Scraper` class. This will allow you to modify what is scraped and how. Xpaths to elements can be found in the inspection panel and by clicking an element and selecting `Copy full xpath`. The scraper can be run in headless mode by adding the following but some websites cannot be scraped in headless mode (e.g. kroger.com)
```python
options = Options()
options.headless = True
driver = webdriver.Chrome(executable_path='./chromedriver',options=options)
```
