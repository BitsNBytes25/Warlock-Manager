import math
import os
import readline
import shutil
import subprocess
import tempfile
from typing import Union
import logging


def print_header(title: str, width: int = 80, clear: bool = False, subtitle: str = '') -> None:
	"""
	Prints a formatted header with a title and optional subtitle.

	Args:
		title (str): The main title to display.
		width (int, optional): The total width of the header. Defaults to 80.
		clear (bool, optional): Whether to clear the console before printing. Defaults to False.
	"""
	if clear:
		# Clear the terminal prior to output
		os.system('cls' if os.name == 'nt' else 'clear')
	else:
		# Just print some newlines
		print("\n" * 3)
	border = "─" * (width - 2)
	space = ' ' * (width - 2)
	print(f'┌{border}┐')
	print(f'│{title.center(width - 2)}│')
	if subtitle:
		print(f'│{space}│')
		for line in subtitle.split('\n'):
			print(f'│{line.center(width - 2)}│')
	print(f'└{border}┘')


def print_subheader(text: str):
	print('')
	print(f'== {text}')
	print('')


def get_terminal_width(default: int = 80) -> int:
	"""
	Returns the width of the terminal window in characters.
	Falls back to `default` if the size cannot be determined.
	"""
	try:
		return shutil.get_terminal_size().columns
	except (AttributeError, OSError):
		return default


def prompt_long_text(
	prompt: str = 'Enter the text in your editor and save/exit when done',
	default: str = '',
	suffix: str = '.txt'
) -> str:
	"""
	Prompt the user to edit a string in their preferred editor.

	This is generally useful for editing long text that does not fit in a simple editor line.

	:param prompt:
	:param default:
	:param suffix:
	:return:
		str: The text input provided by the user.
	"""
	print(prompt)
	input('Press Enter to open your editor, save and exit when done.')
	with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=suffix) as f:
		temp_path = f.name
		if default:
			f.write(default)

	try:
		editor = os.environ.get('EDITOR', 'vim')
		subprocess.run([editor, temp_path], check=True)

		with open(temp_path, 'r') as f:
			return f.read()
	finally:
		os.unlink(temp_path)


def prompt_text(prompt: str = 'Enter text: ', default: str = '', prefill: bool = False) -> str:
	"""
	Prompt the user to enter text input and return the entered string.

	Arguments:
		prompt (str): The prompt message to display to the user.
		default (str, optional): The default text to use if the user provides no input. Defaults to ''.
		prefill (bool, optional): If True, prefill the input with the default text. Defaults to False.
	Returns:
		str: The text input provided by the user.
	"""
	if prefill:
		readline.set_startup_hook(lambda: readline.insert_text(default))
		try:
			return input(prompt).strip()
		finally:
			readline.set_startup_hook()
	else:
		ret = input(prompt).strip()
		return default if ret == '' else ret


def prompt_yn(prompt: str = 'Yes or no?', default: str = 'y') -> bool:
	"""
	Prompt the user with a Yes/No question and return their response as a boolean.

	Args:
		prompt (str): The question to present to the user.
		default (str, optional): The default answer if the user just presses Enter.
			Must be 'y' or 'n'. Defaults to 'y'.

	Returns:
		bool: True if the user answered 'yes', False if 'no'.
	"""
	valid = {'y': True, 'n': False}
	if default not in valid:
		raise ValueError("Invalid default answer: must be 'y' or 'n'")

	prompt += " [Y/n]: " if default == "y" else " [y/N]: "

	while True:
		choice = input(prompt).strip().lower()
		if choice == "":
			return valid[default]
		elif choice in ['y', 'yes']:
			return True
		elif choice in ['n', 'no']:
			return False
		else:
			print("Please respond with 'y' or 'n'.")


def prompt_options(prompt: str = 'Enter the option number: ', options: list = None, default: str = '') -> str:
	"""
	Prompt the user with a list of options and return the selected option.

	The full text value of the option is returned, not the index!

	:param prompt: The prompt to display for input.
    :param options: The list of options to choose from.
    :param default: The default value to return if the user presses Enter.
    :return: The selected option as a string.
	"""
	if not options or not isinstance(options, list):
		# No valid options set, nothing to do
		return default

	# Display options with numbers
	for idx, opt in enumerate(options, 1):
		if opt == default:
			default_flag = '* '
		else:
			default_flag = '  '

		if idx < 10:
			print(f"{default_flag} {idx} - {opt}")
		else:
			print(f"{default_flag}{idx} - {opt}")

	print('')
	while True:
		choice = input(prompt).strip()
		if choice == '':
			return default
		if choice.isdigit():
			idx = int(choice) - 1
			if 0 <= idx < len(options):
				return options[idx]
		print("Please enter a valid option number.")


class Table:
	"""
	Displays data in a table format
	"""

	def __init__(self, columns: Union[list, None] = None):
		"""
		Initialize the table with the columns to display
		:param columns:
		"""
		self.header = columns
		"""
		List of table headers to render, or None to omit
		"""

		self.align = []
		"""
		Alignment for each column, l = left, c = center, r = right

		eg: if a table has 3 columns and the first and last should be right aligned:
		table.align = ['r', 'l', 'r']
		"""

		self.data = []
		"""
		List of text data to display, add more with `add()`
		"""

		self.borders = True
		"""
		Set to False to disable borders ("|") around the table
		"""

	def _text_width(self, string: str) -> int:
		"""
		Get the visual width of a string, taking into account extended ASCII characters
		:param string:
		:return:
		"""
		width = 0
		for char in string:
			if ord(char) > 127:
				width += 2
			else:
				width += 1
		return width

	def add(self, row: list):
		self.data.append(row)

	def render(self):
		"""
		Render the table with the given list of rows

		:return:
		"""
		rows = []
		col_lengths = []
		term_width = get_terminal_width()
		total_width = 0

		if self.header is not None:
			row = []
			for col in self.header:
				col_lengths.append(self._text_width(col))
				row.append(col)
			rows.append(row)
		else:
			col_lengths = [0] * len(self.data[0])

		if self.borders and self.header is not None:
			rows.append(['-BORDER-'] * len(self.header))

		for row_data in self.data:
			row = []
			for i in range(len(row_data)):
				val = str(row_data[i])
				row.append(val)
				col_lengths[i] = max(col_lengths[i], self._text_width(val))
			rows.append(row)

		total_width = sum(col_lengths) + (3 * len(col_lengths) + 1 if self.borders else 2 * (len(col_lengths) + 1))
		if total_width > term_width:
			logging.debug(f'Total data width {total_width} exceeds terminal width {term_width}, shrinking columns')
			widest_column_width = 0
			widest_column_idx = 0
			shrunk = 0
			for i in range(len(col_lengths)):
				if col_lengths[i] > widest_column_width:
					widest_column_width = col_lengths[i]
					widest_column_idx = i
				if col_lengths[i] > 12:
					# Shrink columns down proportionally to fit the terminal width.
					new_width = math.ceil(col_lengths[i] * (term_width / total_width))
					shrunk += col_lengths[i] - new_width
					col_lengths[i] = new_width
			if total_width - shrunk > term_width:
				# Shrink the largest column the remainder to fit the width
				col_lengths[widest_column_idx] = col_lengths[widest_column_idx] - (total_width - shrunk - term_width)

			total_width = sum(col_lengths) + (3 * len(col_lengths) + 1 if self.borders else 2 * (len(col_lengths) + 1))
			logging.debug(f'Shrunk columns to {total_width}')

		for row in rows:
			vals = []
			is_border = False
			if self.borders and self.header and row[0] == '-BORDER-':
				is_border = True

			for i in range(len(row)):
				if i < len(self.align):
					align = self.align[i] if self.align[i] != '' else 'l'
				else:
					align = 'l'

				# Adjust the width of the total column width by the difference of icons within the text
				# This is required because icons are 2-characters in visual width.
				if is_border:
					width = col_lengths[i]
					if align == 'r':
						vals.append(' %s:' % ('-' * width,))
					elif align == 'c':
						vals.append(':%s:' % ('-' * width,))
					else:
						vals.append(' %s ' % ('-' * width,))
				else:
					if len(row[i]) > col_lengths[i]:
						str_val = row[i][:col_lengths[i] - 1] + '…'
					else:
						str_val = row[i]
					width = col_lengths[i] - (self._text_width(row[i]) - len(row[i]))
					if align == 'r':
						vals.append(str_val.rjust(width))
					elif align == 'c':
						vals.append(str_val.center(width))
					else:
						vals.append(str_val.ljust(width))

			if self.borders:
				if is_border:
					print('|%s|' % '|'.join(vals))
				else:
					print('| %s |' % ' | '.join(vals))
			else:
				print('  %s' % '  '.join(vals))
