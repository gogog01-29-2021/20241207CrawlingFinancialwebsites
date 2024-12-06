import selenium 
from selenium import webdriver
from selenium.webdriver.common.by import By
if __name__=="__main__":
driver=webdriver.Chrome()
driver.get("https://www.china-tcm.com.cn/en/Investor/Announce")

tabs=driver.find_elements_by_css_selector(.download-llist"")
print(tabs)
print(tabs[0].text)
print(tabs[0].)

