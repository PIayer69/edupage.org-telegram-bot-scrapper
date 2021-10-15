from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import datetime
# from pyvirtualdisplay import Display

from exceptions import *


class SubstitutionDownloader:
	def __init__(self):
		fireFoxOptions = webdriver.FirefoxOptions()
		fireFoxOptions.headless = True
		self.driver = webdriver.Firefox(options=fireFoxOptions)

		url = "https://elektryk.edupage.org/substitution/"

		self.driver.get(url)
		self.driver.implicitly_wait(5)


	def get_substitution(self, date, class_name):
		'''
		Takes date (dd.mm) and class_name and takes a screnshot of its substitution

		'''

		self.class_name = class_name
		if date == "tomorrow":
			now = datetime.datetime.now()
			tommorow = now + datetime.timedelta(days=1)
			self.date = ".".join([str(tommorow.day) if len(str(tommorow.day)) == 2 else "0" + str(tommorow.day), str(tommorow.month) if len(str(tommorow.month)) == 2 else "0" + str(tommorow.month)])
		elif date == "today":
			now = datetime.datetime.now()
			self.date = ".".join([str(now.day) if len(str(now.day)) == 2 else "0" + str(now.day), str(now.month) if len(str(now.month)) == 2 else "0" + str(now.month)])
		else:
			self.date = date


		#Gets all available substitution days
		days = self.driver.find_elements(By.XPATH, "//div[@class='cell' or @class='cell selected']")
		substitiution_days = [day.get_attribute("innerText")[3:-1] for day in days]


		if self.date in substitiution_days:
			#Changing to requested date
			date_button = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{self.date}')]")
			date_button.click()
			time.sleep(2)

			self.bs = BeautifulSoup(self.driver.page_source, "html.parser")

			if self.check_substitutions():
				# print("INFO: looking for subsitutions...")

				if __name__ == '__main__':
					print(self.scrape_substitution())
				else:
					return self.scrape_substitution()
				
			else:
				raise NoSubstitutionsOnDate(self.date)

		else:
			raise NoDateAvailable(self.date)


	def check_substitutions(self):
		#Checking if there are any substitutions for provided date
		#if so returns True, else False
		if self.bs.find(class_='print-nobreak').text == "W tym dniu nie ma żadnych zastępstw.":
			return False
		return True


	def scrape_substitution(self):
		if self.class_name == "info":
			return self.string_prettiefier([info.text for info in [div.find("span", class_="print-font-resizable") for div in self.bs.find_all("div", style="text-align:center")]], True)

		else:
			right_classes = [class_ for class_ in self.bs.find_all("td", class_='header') if self.class_name == None or self.class_name in class_.text]
			
			if len(right_classes) == len(self.bs.find_all("td", class_='header')):
				return "\n".join([self.string_prettiefier([sub.text for sub in class_.parent.parent.find_all('td')]) for class_ in right_classes])

			else:
				try:
					return self.string_prettiefier([sub.text for sub in right_classes[0].parent.parent.find_all('td')])
				except Exception as e:
					print(e)
					raise NoSubstitutionsForClass(self.class_name)


	def string_prettiefier(self, string, info=False):
		if info:
			return "\n".join(string)

		else:
			new_string = f'''Substitutions on {self.date} for: {string[0]}\n'''

			string.remove(string[0])
			number_of_substitutions = int((len(string)) / 3)
			for i in range(number_of_substitutions):
				new_string += (f"{' || '.join(string[i*3:(i+1)*3])}\n")

			return new_string


	def refresh(self):
		self.driver.refresh()








if __name__ == '__main__':
	x = SubstitutionDownloader()
	# x.get_substitution("29.09", "4ft")
	# x.get_substitution("29.09", "4")
	# x.get_substitution("29.09", "3b")
	x.check_newest_substitution()
