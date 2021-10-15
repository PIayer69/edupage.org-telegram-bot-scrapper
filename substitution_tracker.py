from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from unidecode import unidecode
import datetime
import time
import os

from substitution_downloader import SubstitutionDownloader
from exceptions import *

class SubstitutionTracker:
	def __init__(self):
		fireFoxOptions = webdriver.FirefoxOptions()
		# fireFoxOptions.headless = True
		self.driver = webdriver.Firefox(options=fireFoxOptions)
		url = "https://elektryk.edupage.org/substitution/"

		self.driver.get(url)
		self.driver.implicitly_wait(5)

		self.substitution_filename = "substitution"
		if not os.path.isfile(self.substitution_filename):
			with open(self.substitution_filename, "w") as f:
				f.write("")

		# self.check_newest_substitution()



	def read_saved_substitutions(self):
		with open(self.substitution_filename, 'r') as file:
			return file.read()


	def write_new_substitutions(self, new_substitution):
		with open(self.substitution_filename, 'w+') as file:
			file.write(new_substitution)


	def check_newest_substitution(self):
		'''
		Function checks if there are new substituions for next or present day
		If there are it returns True and saves them to substitution.txt
		'''
		today = datetime.datetime.now()
		tomorrow = today + datetime.timedelta(days=1)
		today_date = f"{'0' + str(today.day) if len(str(today.day)) == 1 else today.day}.{'0' + str(today.month) if len(str(today.month)) == 1 else today.month}"
		tomorrow_date = f"{'0' + str(tomorrow.day) if len(str(tomorrow.day)) == 1 else tomorrow.day}.{'0' + str(tomorrow.month) if len(str(tomorrow.month)) == 1 else tomorrow.month}"
		
		try:
			self.change_date(tomorrow_date)

			#Runs when there are no substitutions for next day
			if not self.check_substitutions():
				print("There are no new substitutions for tomorrow!\n")
				self.change_date(today_date)
				return self.check_if_substitution_newer()

			#Runs if there are substitutions for tomorrow
			else:
				return self.check_if_substitution_newer()
				
		except Exception as e:
			print(e)


	def change_date(self, date):
		date_button = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{date}')]")
		date_button.click()
		self.date = date

		WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
		self.bs = BeautifulSoup(self.driver.page_source, "html.parser")


	def check_substitutions(self):
		#Checking if there are any substitutions for provided date
		#Returns True when there are new substituions
		if self.bs.find("td", string='W tym dniu nie ma żadnych zastępstw.') is None:
			return True
		return False


	def check_if_substitution_newer(self):
		table = self.bs.find("table")
		if self.read_saved_substitutions() == unidecode(str(table)):
			print("Substitutions are the same!\n")
			return False
		else:
			self.write_new_substitutions(unidecode(str(table)))
			print("Found new substitutions!\n")
			return True


	def check_new_substitutions_for_class(self, class_name):
		self.bs = BeautifulSoup(self.read_saved_substitutions(), "html.parser")
		class_ = self.bs.find("td", class_="header", string=class_name)
		# print(class_name)
		# print(repr(class_name))
		# print(class_)
		if class_ is not None: 
			subs = self.string_prettiefier([sub.text for sub in class_.parent.parent.find_all("td")])
			return subs
		else:
			print(f"There are no substitutions for {class_name}!\n")
			return False
		

	def string_prettiefier(self, string):
		new_string = f'''Substitutions on {self.date} for: {string[0]}\n'''

		string.remove(string[0])
		number_of_substitutions = int((len(string)) / 3)
		for i in range(number_of_substitutions):
			new_string += (f"{' || '.join(string[i*3:(i+1)*3])}\n")

		return new_string


	def refresh(self):
		self.driver.refresh()


if __name__ == "__main__":
	x = SubstitutionTracker()
	x.check_new_substitutions_for_class("1gt")
	x.check_new_substitutions_for_class("4ft")

