from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from PIL import Image
import time
from exceptions import *

class GetTimetable():
	def __init__(self):
		fireFoxOptions = webdriver.FirefoxOptions()
		fireFoxOptions.headless = True
		self.driver = webdriver.Firefox(options=fireFoxOptions)
		self.driver.fullscreen_window()

		url = "https://elektryk.edupage.org/timetable"

		self.driver.get(url)
		self.driver.implicitly_wait(60)
		button_cookie = self.driver.find_element(By.XPATH, "//a[@class='flat-button flat-button-greend eu-cookie-closeBtn']")
		button_cookie.click()
		self.all_classes = self.get_classes()




	def get_timetable(self, class_name):
		self.class_name = class_name
		if self.check_if_right_class():
			try:
				button_main = self.driver.find_element(By.XPATH, "//span[@title='Oddziały (klasy)']")
				button_main.click()

				button_class = self.driver.find_element(By.XPATH, f"//a[contains(text(), '{self.class_name}')]")
				self.real_class_name = button_class.get_attribute("innerText")
				try:
					button_class.click()
				except:
					button_class.send_keys(Keys.END)


				timetable = self.driver.find_element(By.TAG_NAME, "svg")
				self.location = timetable.location
				self.size = timetable.size
				self.save_timetable()

			except Exception as e:
				raise CannotGetTimetable(e)
		else:
			raise InvalidClassName(self.class_name)


	def save_timetable(self):
		self.filename = self.create_filename()
		time.sleep(2)
		self.driver.save_screenshot(self.filename)

		x = self.location['x'];
		y = self.location['y'];
		width = self.location['x']+self.size['width'];
		height = self.location['y']+self.size['height'];

		im = Image.open(self.filename)
		im = im.crop((int(x), int(y), int(width), int(height)))
		im.save(self.filename)


	def create_filename(self):
		filename = f'{self.real_class_name} - timetable.png'
		return filename


	def check_if_right_class(self):
		for class_ in self.all_classes:
			if self.class_name in class_:
				return True
		return False


	#Update self.class_name when not downloading timetable
	def update_real_class_name(self, class_name):
		for class_ in self.all_classes:
			if class_name in class_:
				self.real_class_name = class_



	def get_classes(self):
		try:
			button_main = self.driver.find_element(By.XPATH, "//span[@title='Oddziały (klasy)']")
			button_main.click()

			class_list = self.driver.find_element(By.XPATH, "//ul[@class='dropDownPanel asc-context-menu']")
			classes_elements = class_list.find_elements(By.TAG_NAME, "li")
			classes = [class_.get_attribute("innerText") for class_ in classes_elements]
			body = self.driver.find_element(By.TAG_NAME, "body")
			body.click()
			return classes

		except Exception as e:
			raise CannotFindClasses(e)


	def refresh(self):
		self.driver.refresh()
		self.all_classes = self.get_classes()


	def quit_driver(self):
		self.driver.quit()







if __name__ == '__main__':
	x = GetTimetable()
	x.get_classes()
	x.refresh()
	x.get_timetable("4ft")
	# x = get_classes()