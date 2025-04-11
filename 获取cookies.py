from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pickle
driver=webdriver.Edge()

url="https://kyfw.12306.cn/otn/view/index.html"
driver.get(url)

input("手动登陆后输入enter继续......")
with open("cookies.pkl","wb") as f:
    pickle.dump(driver.get_cookies(),f)
driver.quit()



