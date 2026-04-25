import logging
import inspect
from warlock_manager.libs.sensitive_data_filter import sensitive_data_filter


class ClassNameFilter(logging.Filter):
	"""
	A filter that traverses the call stack to find the 'self' instance
	of the caller and attaches its class name to the log record.
	"""
	def filter(self, record: logging.LogRecord) -> bool:
		# Start inspecting from the current frame
		frame = inspect.currentframe()

		# We must skip frames belonging to this logger module itself
		# to avoid incorrectly identifying 'ClassNameFilter' or 'setup_logger' as the caller.
		while frame:
			# Check if 'self' exists in the local variables of the current frame
			if 'self' in frame.f_locals:
				try:
					instance = frame.f_locals['self']
					record.classname = instance.__class__.__name__
					if record.classname not in ['ClassNameFilter', 'RootLogger', 'Logger', 'Context', 'TyperGroup', 'Typer']:
						return True
				except (AttributeError, KeyError):
					pass

			frame = frame.f_back

		# Fallback if no class context is found in the stack
		record.classname = ""
		return True


def setup_logger(name: str = "warlock") -> logging.Logger:
	"""
	Configures and returns a named logger with the ClassNameFilter attached.

	:param name: The name of the logger to configure.
	:return: A configured logging.Logger instance.
	"""
	logger = logging.getLogger(name)

	# Prevent adding duplicate handlers if setup_logger is called multiple times
	if not logger.handlers:
		logger.setLevel(logging.INFO)

		# Create a StreamHandler to output to the console
		handler = logging.StreamHandler()

		# The format includes our custom 'classname' attribute
		formatter = logging.Formatter(
			'%(asctime)s [%(levelname)s] %(classname)s.%(funcName)s: %(message)s'
		)
		handler.setFormatter(formatter)

		logger.addHandler(handler)
		logger.addFilter(ClassNameFilter())
		logger.addFilter(sensitive_data_filter)

		# Set propagate to False to prevent logs from being duplicated
		# by the root logger if it is also configured.
		logger.propagate = False

	return logger


# This is the singleton instance that other libraries can import and use directly.
# Usage: from warlock_manager.libs.logger import logger
logger = setup_logger()
