from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time


class WebBrowser:
    #def __init__():
    
    def startBrowserQuiet(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def closeBrowser(self):
        self.driver.close()
        self.driver.quit()

    def getCSSScreenshotPNG(self, css, url, file):
        self.driver.get(url)
        time.sleep(2)
        self.driver.set_window_size(1920, 1000)
        time.sleep(2)
        self.driver.save_screenshot("fullSite.png")

        # identifying the element to capture the screenshot
        s= self.driver.find_element_by_css_selector(css)
        # to get the element location
        self.driver.execute_script("arguments[0].scrollIntoView(true);", s)
        location = s.location
        # to get the dimension the element
        size = s.size
        #to get the screenshot of complete page
        self.driver.save_screenshot(file)
        #to get the x axis
        x = location['x']
        #to get the y axis
        y = location['y']
        value = self.driver.execute_script("return window.pageYOffset;");
        print(value + y)
        # to get the length the element
        height = location['y']+size['height']
        # to get the width the element
        width = location['x']+size['width']
        # to open the captured image
        imgOpen = Image.open(file) 
        # to crop the captured image to size of that element
        imgOpen = imgOpen.crop((int(x), int(y-value), int(width), int(height-value)))
        # to save the cropped image
        imgOpen.save(file) 
