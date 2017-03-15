# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
from datetime import datetime
from selenium.webdriver.chrome import service
from PIL import Image, ImageChops
import imagehash

#make screenshot
def screenshot(screenshot_folder, driver, file_index):
	#driver.save_screenshot(screenshot_folder + str(driver.title) + str(datetime.now().strftime("%S")) + ".png" )
	#screen_name = screenshot_folder + str(driver.title) + str(datetime.now().strftime("%S")) + ".png"
	driver.get_screenshot_as_file(screenshot_folder + 'screenshot' + str(file_index) + '.png')
	screen_name = screenshot_folder + 'screenshot' + str(file_index) + '.png'
	return(screen_name)


#Change resolution
def chresolution(driver, resolutiot):
	driver.set_window_size(resolution[0], resolution[1])


#Change browser
def crossbrowser(url, browser):
	if browser == "Chrome" :
                browser_attr = "webdriver." + browser + "('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')"
	elif browser == "Firefox" :
                browser_attr = "webdriver." + browser + "()"
	elif browser == "Ie" :
                browser_attr = "webdriver." + browser + "('C:\Program Files\Internet Explorer\IEDriverServer.exe')"
	elif browser == "Opera":
                webdriver_service = service.Service('C:\Program Files (x86)\Opera\operadriver.exe')
                webdriver_service.start()
                browser_attr = "webdriver.Remote(webdriver_service.service_url, webdriver.DesiredCapabilities.OPERA)"
	driver = eval(browser_attr)
	driver.implicitly_wait(60)
	driver.get(url)
	return(driver)


#Change resolution
def changeresolution(driver, brow_folder, resolution):
	resolution_folder = os.makedirs(brow_folder + "\\" + str(resolution))
	driver.set_window_size(resolution[0], resolution[1])
	screenshot_folder = brow_folder + "\\" + str(resolution) + "\\"
	return(screenshot_folder)


#Find different between imagees            
def pixelperfect(mockup, screen):
	img_mockup = Image.open(mockup)
	img_screen = Image.open(screen)
	size_mockup = img_mockup.size
	size_screen = img_screen.size
	if size_mockup != size_screen:
		min_height = min(size_mockup[1], size_screen[1])
		min_width = min(size_mockup[0], size_screen[0])
		resolution = (min_width, min_height)
		img_mockup.resize(resolution, Image.ANTIALIAS)
		img_screen.resize(resolution, Image.ANTIALIAS)
	differents = ImageChops.difference(img_mockup, img_screen).save(screen + "dif.jpg")


#Find duplicate by phash
def perhash(image1, image2):
	test1 = imagehash.phash(Image.open(image1))
	test2 = imagehash.phash(Image.open(image2))
	result = test2 - test1
	print(test1)
	print(test2)
	print(result)
	if result == 0 :
		print("Изображения идентичны")
	else :
		print("Степерь отличия : " , result)


#determine the number of elements in DOM
def elements_in_dom(driver):
	dom_number = driver.execute_script("return(document.getElementsByTagName('*').length)")
	return(dom_number)
		
		
#Сравнение по DOM
def dom_deference(number_elements, driver):
	driver = driver
	new_elements = elements_in_dom(driver)
	if number_elements != new_elements :
		result = True
	else :
		result = False
	return(result)	