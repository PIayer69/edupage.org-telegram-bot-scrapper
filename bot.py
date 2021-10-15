from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging
import random
import datetime
import os

import exceptions
from timetable_downloader import GetTimetable
from substitution_downloader import SubstitutionDownloader
from substitution_tracker import SubstitutionTracker
from timer import Timer


class TelegramBot():
	def __init__(self):

		self.timer = Timer()
		self.timetabler = GetTimetable()
		self.substitution_downloader = SubstitutionDownloader()
		self.substitution_tracker = SubstitutionTracker()

		self.jobs_filename = "jobs"


		#Responses when waiting for result
		self.responses = ['Got it! Hold tight for a second...', 'One sec...', 'Ay, ay Captain!', 'Searching through databases...', 'Keep calm and wait for the result...', "Looking for timetables...", "Please don't turn off your PC while we're working...", "Gimmie a sec...", "Alright, be right back..."]


		logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		                     level=logging.INFO)

		updater = Updater(token="YOUR_BOT_TOKEN", use_context=True, request_kwargs={'read_timeout': 10, 'connect_timeout': 10})

		self.dispatcher = updater.dispatcher

		start_handler = CommandHandler('start', self.start)
		timetable_handler = CommandHandler("tt", self.tt)
		classes_handler = CommandHandler("classes", self.classes)
		substitution_handler = CommandHandler("ss", self.ss)
		notification_handler = CommandHandler("nn", self.notifications)
		help_handler = CommandHandler("help", self.help)

		self.dispatcher.add_handler(start_handler)
		self.dispatcher.add_handler(timetable_handler)
		self.dispatcher.add_handler(classes_handler)
		self.dispatcher.add_handler(substitution_handler)
		self.dispatcher.add_handler(notification_handler)
		self.dispatcher.add_handler(help_handler)

		self.dispatcher.add_error_handler(self.error_handler)

		updater.start_polling()

		self.import_jobs()


	def error_handler(self, update, context):
		print(f"TelegramBotError: {context.error}")
		try:
			context.bot.send_message(chat_id=update.effective_chat.id, text="Something went wrong! Try again.")
		except Exception as e:
			print(e)


	def string_handler(self, string):
		if len(string) > 2000:
			strings = []
			start_index = 0
			for i in range(int(len(string) / 2000)):
				if i+1 == int(len(string) / 2000):
					index_to_split = len(string)-1
				else:
					index_to_split = string.index("Substitutions", (i+1)*2000) - 1

				strings.append(string[start_index:index_to_split])
				start_index = index_to_split+1

			return strings

		else: return [string]


	def import_jobs(self):
		if os.path.isfile(self.jobs_filename):
			with open(self.jobs_filename, "r") as file:
				jobs = file.readlines()

			for job in jobs:
				job_id, class_name = job.split(":")
				class_name = class_name.strip()
				# print(job_id, class_name)
				self.dispatcher.job_queue.run_repeating(self.notifications_job, 1800, context=[job_id, class_name], name=job_id)
			print("Done importing")
		else:
			print("There is nothing to import!")


	def export_job(self, job_id, class_name):
		if os.path.isfile(self.jobs_filename):
			with open(self.jobs_filename, 'r') as file:
				new_jobs = [job for job in file.readlines() if not job_id in job.split(":")[0]]

		with open(self.jobs_filename, "w") as file:
			if "new_jobs" in locals():
				file.write("".join(new_jobs))

			file.write(f"{job_id}:{class_name}\n")

		print("Done exporting")



	#Response functions
	#/start 
	def start(self, update, context):
		chat_user_client = update.message.from_user.username
		print(datetime.datetime.now())
		print('Client username: ' , chat_user_client)
		print(f"Command: /start")

		string = '''Hello there! ❤️❤️❤️
			Welcome to Timetabler - 'speedo' bot to make your life simpler (well kinda...)

			Usage:
				/tt [class_name] to get fresh timetable of your class
				Example use: 
					/tt 4ft

				/classes to check available classes

				/ss [date] [class_name] to get substitutions for your class
				Example use: 
					/ss 01.10 1ct - to get substitutions for 1ct for 01.06
					/ss today info - to get info for present day (upsent teachers, classes, etc.)
					/ss tomorrow - to get all substitutions for next day

				/nn [class_name] to set notifications when new subsitutions for selected class are posted.
				We are checking every 30 minutes if there are new substitutions and if provided class has one.
					Example use: 
						/nn 4ft - to set notification for 4ft
						/nn remove - remove notification

				/help prints out how to use this bot

			-----------------------------------------

			When using commands be patient. It takes some time to get info.
			More features comming soon!'''
		context.bot.send_message(chat_id=update.effective_chat.id, text=string)


	#/tt
	def tt(self, update, context):
		string = random.choice(self.responses)
		context.bot.send_message(chat_id=update.effective_chat.id, text=string)
		try:
			if context.args[0]: 
				if len(context.args) > 1:
					class_name = " ".join(context.args)
				else:
					class_name = context.args[0]

				chat_user_client = update.message.from_user.username
				print(datetime.datetime.now())
				print('Client username: ' , chat_user_client)
				print(f"Command: /tt {' '.join(context.args)}")
				if self.timer.check_last_update(class_name):
					if self.timer.check_last_update():
						self.timetabler.refresh()
						print("Refreshing page")

					self.timetabler.get_timetable(class_name)
					self.timer.update_time(class_name)
				else:
					self.timetabler.update_real_class_name(class_name)


				filename = self.timetabler.create_filename()
				with open(filename, "rb") as image:
					image = image.read()

				context.bot.send_photo(chat_id=update.effective_chat.id, photo=image)

			else:
				raise exceptions.WrongAmountOfArguments(len(context.args))


		except exceptions.CannotGetTimetable as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="Cannot get timetable!")


		except exceptions.InvalidClassName as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="Provided class is invalid!")


		except Exception as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="Something went wrong! Check if you typed your class correctly. If you don't know which classes are available you can type: /classes")


	#/classes
	def classes(self, update, context):
		chat_user_client = update.message.from_user.username
		print(datetime.datetime.now())
		print('Client username: ' , chat_user_client)
		print("Getting classes")

		string = "Available classes:\n" + "".join([f"{class_}, " for class_ in self.timetabler.all_classes])
		string = string[0:len(string)-2] + "."
		context.bot.send_message(chat_id=update.effective_chat.id, text=string)


	#/ss
	def ss(self, update, context):
		try:
			if len(context.args) and len(context.args) <= 3:
				date = context.args[0]
				if len(context.args) == 3:
					class_name = ' '.join(context.args[1:])
				elif len(context.args) == 1:
					class_name = None
				else:
					class_name = context.args[1]

				#Printing info
				chat_user_client = update.message.from_user.username
				print(datetime.datetime.now())
				print('Client username: ' , chat_user_client)
				print(f"Command: /ss {' '.join(context.args)}")

				string = random.choice(self.responses)
				context.bot.send_message(chat_id=update.effective_chat.id, text=string)

				if self.timer.check_last_update("substitutions"):
					self.substitution_downloader.refresh()

				substitutions = self.string_handler(self.substitution_downloader.get_substitution(date, class_name))
				self.timer.update_time("substitutions")
				for substitution in substitutions:
					context.bot.send_message(chat_id=update.effective_chat.id, text=substitution)

			else:
				raise exceptions.WrongAmountOfArguments(len(context.args))


		except AttributeError as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="No arguments were passed!")


		except exceptions.WrongAmountOfArguments as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong amount of arguments were passed!")


		except exceptions.NoSubstitutionsOnDate as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="There are no substitutions for provided date!")


		except exceptions.NoSubstitutionsForClass as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="There are no substitutions for provided class!")


		except exceptions.NoDateAvailable as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="Provided date cannot be found!")


	#/nn
	def notifications(self, update, context):
		try:
			chat_id = update.message.chat_id
			chat_user_client = update.message.from_user.username
			print(datetime.datetime.now())
			print('Client username: ' , chat_user_client)
			print(f"Command: /nn {' '.join(context.args)}")

			if len(context.args):
				if len(context.args) == 2:
					class_name = " ".join(context.args)
				elif len(context.args) == 1:
					class_name = context.args[0]
				else:
					raise exceptions.WrongAmountOfArguments(len(context.args))

				if class_name == "remove":
					self.remove_job_if_exists(str(chat_id), context)
					raise exceptions.JobRemoved()

				#Finding all matching classes
				right_classes = [class_ for class_ in self.timetabler.all_classes if class_name in class_]
				try: 
					class_name = right_classes[0]
				except:
					raise exceptions.InvalidClassName(class_name)


				removed_job = self.remove_job_if_exists(str(chat_id), context)

				context.job_queue.run_repeating(self.notifications_job, 1800, context=[chat_id, class_name], name=str(chat_id))

				string = f"Notification for class: {class_name} is set!"

				if removed_job:
					string += "\nOld notification removed."

				self.export_job(str(chat_id), class_name)


				context.bot.send_message(chat_id=update.effective_chat.id, text=string)

			else:
				context.bot.send_message(chat_id=update.effective_chat.id, text="No arguments were passed!")

		except AttributeError as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="No arguments were passed!")

		except exceptions.WrongAmountOfArguments as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong amount of arguments were passed!")

		except exceptions.InvalidClassName as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text="Provided class is invalid!")

		except exceptions.JobRemoved as e:
			print(e)
			context.bot.send_message(chat_id=update.effective_chat.id, text=e)


	#Function checking if user has any notifications set, if so removing them
	def remove_job_if_exists(self, name, context):
		current_jobs = context.job_queue.get_jobs_by_name(name)
		if not current_jobs:
			return False

		for job in current_jobs:
			job.schedule_removal()
		return True


	def notifications_job(self, context):
		chat_id, class_name = context.job.context

		self.substitution_tracker.refresh()
		if self.substitution_tracker.check_newest_substitution():
			string = self.substitution_tracker.check_new_substitutions_for_class(class_name)
			if string:
				context.bot.send_message(chat_id=int(chat_id), text=string)
			else:
				pass



	#/help
	def help(self, update, context):
		chat_user_client = update.message.from_user.username
		print(datetime.datetime.now())
		print('Client username: ' , chat_user_client)
		print(f"Command: /help")

		string = '''
		Usage:
			/tt [class_name] to get fresh timetable of your class
				Example use: 
					/tt 4ft

			/classes to check available classes

			/ss [date] [class_name] to get substitutions for your class
				Example use: 
					/ss 01.10 1ct - to get substitutions for 1ct for 01.06
					/ss today info - to get info for present day (upsent teachers, classes, etc.)
					/ss tomorrow - to get all substitutions for next day

			/nn [class_name] to set notifications when new subsitutions for selected class are posted.
			We are checking every 30 minutes if there are new substitutions and if provided class has one.
				Example use: 
					/nn 4ft - to set notification for 4ft
					/nn remove - remove notification

			/help prints this message
		'''
		context.bot.send_message(chat_id=update.effective_chat.id, text=string)

	



if __name__ == '__main__':
	bot = TelegramBot()