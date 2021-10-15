import datetime

class Timer():
	def __init__(self):
		self.update_time_dict = {}
		self.min_update_time = 30



	def update_time(self, classname):
		now = datetime.datetime.now().timestamp()
		self.update_time_dict.update({classname: now})
		self.update_time_dict.update({"app": now})


	def check_last_update(self, classname="app"):
		'''
		Checks if last update was made earlier than min_update_time
		'''
		now = datetime.datetime.now().timestamp()

		if classname in self.update_time_dict.keys():
			time_passed = now - self.update_time_dict[classname]
			if time_passed < self.min_update_time*60:
				return False

		if classname == "app" or classname == "substitutions":
			return False
			
		return True



if __name__ == '__main__':
	x = Timer()
	x.update_time()
	print(x.check_last_update())
