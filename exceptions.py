
class Error(Exception):
	'''Base class for other exceptions'''
	pass


class WrongAmountOfArguments(Error):
	def __init__(self, args_count):
		'''Raised when passed wrong amount of  arguments'''
		message = f"Passed wrong amount of arguments: {args_count}"
		super().__init__(message)



class NoSubstitutionsOnDate(Error):
	def __init__(self, date):
		'''Raised when there are no substitutions on provided date'''
		message = f"There are no substitutions for provided date: {date}"
		super().__init__(message)
	


class NoSubstitutionsForClass(Error):
	def __init__(self, class_name):
		'''Raised when provided class could not be found'''
		message = f"There are no substitutions for provided class: {class_name}"
		super().__init__(message)



class NoDateAvailable(Error):
	def __init__(self, date):
		'''Raised when provided date cannot be found on main page'''
		message = f"Provided date couldn't be found on main page: {date}"
		super().__init__(message)



class CannotFindClasses(Error):
	def __init__(self, error):
		'''Raises when get_classes() fails'''
		message = f"Cannot get all classes: {error}"
		super().__init__(message)



class InvalidClassName(Error):
	def __init__(self, class_name):
		'''Raises when class name is not found'''
		message = f"Provided class name is invalid: {class_name}"
		super().__init__(message)



class CannotGetTimetable(Error):
	def __init__(self, error):
		'''Raised when get_timetable() fails'''
		message = f"Cannot get timetable: {error}"
		super().__init__(message)



class JobRemoved(Error):
	def __init__(self, error):
		'''Raised when get_timetable() fails'''
		message = f"Removed job"
		super().__init__(message)

