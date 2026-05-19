from typing import Union
import json
import os
import re

from warlock_manager.config.base_config import BaseConfig
from warlock_manager.libs.logger import logger
from warlock_manager.libs.utils import ensure_file_parent_exists, ensure_file_ownership


class ArmaServerConfig(BaseConfig):
	def __init__(self, group_name: str, path: str):
		super().__init__(group_name)
		self.path = path
		self.group = group_name
		self.data = []
		self._name_index = {}
		self._key_index = {}
		# Match standard lines: key = value;
		self.kv_regex = re.compile(r'^([a-zA-Z0-9_\[\]]+)\s*=\s*(.*?)\s*;(?:\s*//(.*))?$')
		# Match multi-line values, common with array values
		self.k_regex = re.compile(r'^([a-zA-Z0-9_\[\]]+)\s*=\s*(?:({\s*))?(?:\s*//(.*))?$')

	def add_option(self, option_dict: dict):
		"""
		Add a configuration option to the available list

		:param name:
		:param section:
		:param key:
		:param default:
		:param val_type:
		:param help_text:
		:return:
		"""
		super().add_option(option_dict)

		if '/' in option_dict['key']:
			# Also ensure the parent key is present.
			base_key = option_dict['key'].split('/')[0]
			self._store_data(base_key, '', 'array')

	def get_value(self, name: str) -> Union[str, int, bool]:
		"""
		Get a configuration option from the config

		:param name: Name of the option
		:return:
		"""
		if name not in self.options:
			logger.error('Invalid option: %s, not present in %s configuration!' % (name, os.path.basename(self.path)))
			return ''

		opt = self.options[name]

		if '/' in opt.key:
			# This is a nested key, pull the parent value
			parent_key = opt.key.split('/')[0].lower()
			parent_index = int(opt.key.split('/')[1])

			try:
				index = self._key_index[parent_key]
				current = self.data[index]['value']
				if not isinstance(current, list):
					val = opt.default
				else:
					val = current[parent_index]
			except (IndexError, KeyError):
				val = opt.default
		else:
			# The lookup cache should contain an index if it exists, else use the default.
			try:
				index = self._name_index[name]
				val = self.data[index]['value']
			except KeyError:
				val = opt.default

		return opt.to_system_type(val)

	def set_value(self, name: str, value: Union[str, int, bool, float, list]):
		"""
		Set a configuration option in the config

		:param name: Name of the option
		:param value: Value to save
		:return:
		"""
		if name not in self.options:
			logger.error('Invalid option: %s, not present in %s configuration!' % (name, os.path.basename(self.path)))
			return

		opt = self.options[name]

		if '/' in opt.key:
			# This is a nested key, pull the parent value
			parent_key = opt.key.split('/')[0].lower()
			parent_index = int(opt.key.split('/')[1])
			try:
				index = self._key_index[parent_key]
				current = self.data[index]['value']
				if not isinstance(current, list):
					current = self._create_default_nested(parent_key)
				current[parent_index] = value
				self.data[index]['value'] = current
			except KeyError:
				# Doesn't exist, create a new one.
				current = self._create_default_nested(parent_key)
				current[parent_index] = value

				self._parse_value(parent_key, current)
		else:
			# The lookup cache should contain an index if it exists, else use the default.
			try:
				index = self._name_index[name]
				self.data[index]['value'] = value
			except KeyError:
				# Doesn't exist, create a new one.
				self._parse_value(opt.key, value)

				# Set the mapped type based on the value
				index = self._name_index[name]

			if self.data[index]['key'].endswith('[]') and isinstance(value, list):
				self.data[index]['val_type'] = 'array'
			elif opt.val_type == 'str':
				self.data[index]['val_type'] = 'str'

	def _create_default_nested(self, parent_key):
		"""
		Create the default values for a given parent key

		Useful because the game expects all values to be present for a given string if it's set.

		:param parent_key:
		:return:
		"""
		highest_index = 0
		value = {}
		for key, name in self._keys.items():
			if key.startswith(parent_key + '/'):
				index = int(key.split('/')[1])
				opt = self.options[name]
				default = opt.default
				highest_index = max(highest_index, index)
				value[index] = default
		# We need a simple ordered list, ensuring any skipped keys are present.
		ret = []
		for idx in range(highest_index + 1):
			if idx in value:
				ret.append(value[idx])
			else:
				ret.append(None)
		return ret

	def has_value(self, name: str) -> bool:
		"""
		Check if a configuration option has been set

		:param name: Name of the option
		:return:
		"""
		if name not in self.options:
			return False

		try:
			index = self._name_index[name]
			return self.data[index]['value'] != ''
		except KeyError:
			# Doesn't exist
			return False

	def exists(self) -> bool:
		"""
		Check if the config file exists on disk
		:return:
		"""
		return os.path.exists(self.path)

	def load(self):
		"""
		Load the configuration file from disk
		:return:
		"""
		if not os.path.exists(self.path):
			return

		self.data = []
		group = None
		buffer = ''
		nesting = 0
		last_key = None
		last_comment = None

		with open(self.path, 'r', encoding='utf-8') as f:
			for line_raw in f:
				line = line_raw.strip()

				# Handle multiline comments.
				if line.startswith('/*'):
					group = 'comment'
					if line != '/*':
						buffer = line[2:] + '\n'
					continue
				if group == 'comment':
					if line.endswith('*/'):
						group = None
						if line != '*/':
							buffer += line[:-2]
						self.data.append({
							'type': 'multi_comment',
							'comment': buffer.strip()
						})
						buffer = ''
					else:
						buffer += line_raw
					continue

				# Handle classes; these behave similar to multiline comments as they are not parsed.
				if group is None and line.startswith('class'):
					if line.endswith('};'):
						# Self closing class; ie: no arguments provided.
						self.data.append({
							'type': 'class',
							'value': line
						})
					else:
						group = 'class'
						buffer = line_raw
						nesting = 1 if '{' in line else 0
					continue
				if group == 'class':
					buffer += line_raw
					if '{' in line:
						nesting += 1
					if '};' in line:
						nesting -= 1
						if nesting == 0:
							self.data.append({
								'type': 'class',
								'value': buffer.strip()
							})
							group = None
							buffer = ''
					continue

				# Check for continuation of values
				if group == 'value':
					if re.match(r'.*;\s*//', line):
						# Ending line, but also contains a comment.
						last_comment = line[line.find('//') + 2:].strip()
						buffer += line[:line.find('//')]
						self._parse_value(last_key, buffer.strip(), last_comment)
						buffer = ''
						group = None
						last_comment = None
						last_key = None
					elif line.endswith(';'):
						buffer += line_raw
						self._parse_value(last_key, buffer.strip(), last_comment)
						buffer = ''
						group = None
						last_comment = None
						last_key = None
					else:
						buffer += line_raw
					continue

				if line.startswith('//'):
					self.data.append({
						'type': 'comment',
						'comment': line[2:].strip()
					})
					continue

				if line == '':
					self.data.append({
						'type': 'empty'
					})
					continue

				# Match standard Key = Value settings
				kv_match = self.kv_regex.match(line)
				if kv_match:
					line_key = kv_match.group(1).strip()
					line_val = kv_match.group(2).strip()
					line_com = kv_match.group(3)
					self._parse_value(line_key, line_val, line_com)
					continue

				k_match = self.k_regex.match(line)
				if k_match:
					# Matches complex key values where the key is defined on one line and values are on another
					group = 'value'
					last_key = k_match.group(1).strip()
					if k_match.group(2) is not None:
						buffer = k_match.group(2) + '\n'
					last_comment = k_match.group(3)

	def _parse_value(self, line_key: str, line_val: str, line_comment: str = None):
		if line_comment is not None:
			line_comment = line_comment.strip()
		else:
			line_comment = ''

		# Clean up wrapper quotes if they exist in string variables
		if line_key.endswith('[]'):
			line_type = 'array'
		elif isinstance(line_val, str) and line_val.startswith('"') and line_val.endswith('"'):
			line_val = line_val[1:-1]
			line_type = 'str'
		else:
			line_type = 'raw'

		if line_type == 'array' and isinstance(line_val, str):
			# Use JSON to translate objects to native data
			# This only applies if the value is a string, otherwise it should be a list already.
			in_quote = False
			cleaned_string = []
			for idx, char in enumerate(line_val):
				if char == '"':
					in_quote = not in_quote

				if char == '{' and not in_quote:
					cleaned_string.append('[')
				elif char == '}' and not in_quote:
					cleaned_string.append(']')
				else:
					cleaned_string.append(char)
			try:
				cleaned_string = ''.join(cleaned_string).strip().rstrip(';')
				line_val = json.loads(cleaned_string)
			except (ValueError, SyntaxError) as e:
				logger.error('Failed to parse array value: %s' % (e, ))
				# Remap to raw to prevent modifications and preserve saves
				line_type = 'raw'

		self._store_data(line_key, line_val, line_type, line_comment)

	def _store_data(self, line_key: str, line_val: str, line_type: str, line_comment: str = None):
		# Check if this key is already recorded.
		try:
			lookup_key = self._key_index[line_key.lower()]
			self.data[lookup_key]['value'] = line_val
			return
		except KeyError:
			pass

		# Record an index if this is a mapped key
		try:
			lookup_name = self._keys[line_key.lower()]
			self._name_index[lookup_name] = len(self.data)
		except KeyError:
			pass

		self._key_index[line_key.lower()] = len(self.data)

		self.data.append({
			'type': 'keyvalue',
			'key': line_key,
			'value': line_val,
			'val_type': line_type,
			'comment': line_comment
		})

	def _render_value(self, val_type: str, value):
		"""
		Render a native array into an Arma array value string

		Uses JSON for primary rendering

		:param value:
		:return:
		"""

		if val_type == 'array':
			str_val = json.dumps(value, indent=None if len(value) <= 4 else '\t')
			arma_str = []
			in_quote = False
			for idx, char in enumerate(str_val):
				if char == '"':
					in_quote = not in_quote

				if char == '[' and not in_quote:
					arma_str.append('{')
				elif char == ']' and not in_quote:
					arma_str.append('}')
				else:
					arma_str.append(char)
			return ''.join(arma_str)
		elif val_type == 'str':
			return '"%s"' % value
		else:
			return str(value)

	def fetch(self) -> str:
		"""
		Fetch the raw contents of this configuration to be saved back to the disk
		:return:
		"""
		ret = []
		for line in self.data:
			if line['type'] == 'keyvalue':
				str_val = self._render_value(line['val_type'], line['value'])
				out = '%s = %s;' % (line['key'], str_val)

				if line['comment']:
					out += '  // %s' % (line['comment'], )
				ret.append(out)
			elif line['type'] == 'comment':
				ret.append('// %s' % (line['comment'], ))
			elif line['type'] == 'empty':
				ret.append('')
			elif line['type'] == 'class':
				ret.append(line['value'])
			elif line['type'] == 'multi_comment':
				ret.append('/*\n%s\n*/' % (line['comment'], ))

		return '\n'.join(ret)

	def save(self):
		"""
		Save the configuration file back to disk
		:return:
		"""

		ensure_file_parent_exists(self.path)
		with open(self.path, 'w', encoding='utf-8') as f:
			f.write(self.fetch())
		ensure_file_ownership(self.path)
