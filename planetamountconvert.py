#! /usr/bin/env python
'''A simple script letting you convert an adofai level to 3 planets (and more)
	- path_data -- A dict with mapprings from pathData to angleData
	- formatLevelString -- A function formating an adofai level string to a JSON
	- Level -- A class to convert a 2-planet level to 3 planets
'''
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter, SUPPRESS
from copy import deepcopy
from json import dump, loads
from os.path import basename, splitext
from pathlib import Path
from re import sub
from sys import argv
from tkinter import Button, Entry, Frame, Label, Menu, Spinbox, Tk
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter.messagebox import showwarning
from tkinter.ttk import Treeview
from typing import Any, Callable, IO, Literal, TYPE_CHECKING
from warnings import warn
from webbrowser import open_new_tab
if TYPE_CHECKING:
	from _typeshed import FileDescriptorOrPath
else:
	FileDescriptorOrPath = Any



path_data = {
	'R': 0,
	'p': 15,
	'J': 30,
	'E': 45,
	'T': 60,
	'o': 75,
	'U': 90,
	'q': 105,
	'G': 120,
	'Q': 135,
	'H': 150,
	'W': 165,
	'L': 180,
	'x': 195,
	'N': 210,
	'Z': 225,
	'F': 240,
	'V': 255,
	'D': 270,
	'Y': 285,
	'B': 300,
	'C': 315,
	'M': 330,
	'A': 345,
	'!': 999,
}
'''A map from pathData-char to angleData-number
	- key -- char
	- value -- int
'''
formatLevelString: Callable[[str], str] = lambda string: sub(',(?=\s*[\]},])|(?<![\[{,])\s*\n(?!\s*[\]}])', '', string.replace(']\n', '],\n'))
'''Fix some wrong commas and some unnecessary next-lines. Return a JSON-like string.
	- string -- A string read from a .adofai file
'''
class Level:
	'''An adofai level, ready converting or already converted to 3 planets (and more).

	Do ``Level.loadMainFromPath(path)`` to load a level from a path-string or a Pathlib.path

	or do ``Level.loadMainFromString(string)`` to load a level from a JSON string.

	After loaded a level, use ``Level.loadLevelFromMain()`` to initialize the level.

	``Level.setPlanets(...)`` sets the goal planet amount and ``Level.resetPlanets()`` resets.

	After everything is ready, use ``Level.convertByPlanets()`` to convert the level.

	Than Level.main is converted, you can dump it with ``Level.dumpMain(file)`` or any other way.

	Use Level.getActions(...) to get actions of the level.

	See ``example.py`` to find more examples.'''
	_Real = int | float
	'Real number'
	_RealOrStr = _Real | str
	'Real number or string'
	_Action = dict[str, _RealOrStr | list[_RealOrStr]]
	'One single action or decoration'
	_actions = ('beatsAhead', 'beatsBehind', 'beatsPerMinute', 'duration', 'holdMidSoundDelay','repetitions')
	'All the multiplier need to be multiplied'


	def __init__(self, main: dict[str, str | dict[str, _RealOrStr | bool | list[_Real]] | list[_Action | _Real]] = dict()):
		'''An adofai level, ready converting or already converted to 3 planets (and more)
			- main -- A dict representing an adofai level, should have the same structure like main.adofai (default:``{}``)
		'''
		self.main = main
		'main.adofai in dict'
		self.accelerates = dict()
		'All accelerate actions'
		self.holds = dict()
		'All hold actions'
		self.multiplanets = dict()
		'All multiplanet actions'
		self.twirls = dict()
		'All twirl actions'


	def __len__(self):
		'Re-cauculate the length and return it'
		self.length = len(self.main['angleData']) if 'angleData' in self.main else len(self.main['pathData']) if 'pathData' in self.main else 0
		return self.length


	def loadMainFromString(self, string: str):
		'''Load a JSON-like string as self.main
			- string -- A json-like string
		'''
		self.main = loads(string)
		return self


	def loadMainFromPath(self, path: Path | FileDescriptorOrPath):
		'''Load a .adofai as self.main
			- path -- A pathlib.Path instance or a literal path
		'''
		with path.open(encoding = 'utf-8-sig') if isinstance(path, Path) else open(path, encoding = 'utf-8-sig') as f:
			string = formatLevelString(f.read())
		return self.loadMainFromString(string)


	def resetPlanets(self):
		'Reset or initialize the planet amount'
		self.planets = list()
		planet = 2
		for i in range(self.length + 1):
			planet = self.multiplanets[i]['planets'] if i in self.multiplanets else planet
			self.planets.append({'from': planet, 'to': planet})
		return self


	def setPlanets(self, start: int, end: int, to: int, onStartBiggerThanEnd: Callable[[str], None] = lambda message: warn(message, SyntaxWarning, 3)):
		'''Set the planet amount that is going to convert
			- start -- A positive integer
			- end -- A positive integer, must smaller than the length of the level
			- to -- A positive integer, must bigger than 2 and not too big
			- onStartBiggerThanEnd -- Callback if start is bigger than end (default:``warn``)
		'''
		if start > end:
			onStartBiggerThanEnd('End should be bigger than start. Ignored')
		for i in range(start, end + 1):
			self.planets[i]['to'] = to
		return self


	def _addHold(self, action: _Action, index: int):
		'''Call if there is a Hold action
			- action -- A dict with ``floor`` key and ``duration`` key
			- index -- A positive integer shows the action ordinal
		'''
		self.holds[action['floor']] = {
			'degree': action['duration'] * 360,
			'index': index,
		}
		return self


	def _addMultiPlanet(self, action: _Action, index: int):
		'''Call if there is a MultiPlanet action
			- action -- A dict with ``floor`` key and ``planets`` key
			- index -- A positive integer shows the action ordinal
		'''
		self.multiplanets[action['floor']] = {
			'index': index,
			'planets': action['planets'],
		}
		return self


	def _addSetSpeed(self, action: _Action, index: int):
		'''Call if there is a SetSpeed action
			- action -- A dict with ``floor`` key and ``speedType`` key
			- index -- A positive integer shows the action ordinal
		'''
		self.accelerates[action['floor']] = {
			'index': index,
			'speedType': action['speedType'],
		}
		return self


	def getActions(self, event_type: str, event_list: Literal['actions', 'decorations'] = 'actions') -> dict[int, _Action]:
		'''Get a dict with one kind of action
			- event_type -- The ``eventType`` string
			- event_list -- This action is at actions or in decorations? (default:``actions``)
		'''
		ret = dict()
		for i, action in enumerate(self.main[event_list]):
			if action['eventType'] == event_type:
				ret[action['floor']] = {
					'index': i,
					**action,
				}
				del ret[action['floor']]['eventType']
				del ret[action['floor']]['floor']
		return ret


	def loadLevelFromMain(self):
		'Load some needed action, convert pathData to angleData, round the angles, cauculate length of the level and initialize the planet amount.'
		for i, action in enumerate(self.main['actions']):
			match action['eventType']:
				case 'Hold':
					self._addHold(action, i)
				case 'MultiPlanet':
					self._addMultiPlanet(action, i)
				case 'SetSpeed':
					self._addSetSpeed(action, i)
				case 'Twirl':
					self.twirls[action['floor']] = True

		if 'pathData' in self.main:
			self.main['angleData'] = []
			for i in self.main.pop('pathData'):
				self.main['angleData'].append(path_data[i])
		else:
			self.main['angleData'] = list(map(lambda angle: round(angle, 2), self.main['angleData']))

		self.length = len(self.main['angleData'])
		return self.resetPlanets()


	def _computeAngle(self, angle: _Real, clockwise: bool, index: int, old_angle: _Real, old_planets: int):
		'''Re-cauculate the angle of block
			- angle -- Positive Real number. The old angle
			- clockwise -- True for clockwise and False for counterclockwise
			- index -- Positive integer. The index of the block
			- old_angle -- Positive Real number. The angle of the former block
			- old_planets -- Positive integer. The planet amount of the former block
		'''
		midspin = self.main['angleData'][index - 1] == 999

		old_angle += not midspin and 180
		degree = round(old_angle - angle if clockwise else angle - old_angle, 2) % 360 or 360

		if self.planets[index]['from'] != self.planets[index]['to']:
			from_degree = (self.planets[index]['from'] - 2) * 180 / self.planets[index]['from']
			to_degree = (self.planets[index]['to'] - 2) * 180 / self.planets[index]['to']
			rate = self.planets[index]['from'] / self.planets[index]['to']

			degree = degree * rate if midspin else (degree - from_degree) * rate + to_degree

			if index in self.holds:
				hold_degree = degree + (self.holds[index]['degree'] + (degree <= from_degree and 360)) * rate
				degree = hold_degree % 360
				self.main['actions'][self.holds[index]['index']]['duration'] = (hold_degree - (degree <= to_degree and 360)) // 360

		if self.planets[index]['to'] != old_planets:
			rate = (self.planets[index - 2]['to'] if midspin else self.planets[index - 1]['to']) / self.planets[index]['to']
			if not index in self.accelerates:
				self.main['actions'].append({
					'beatsPerMinute': 100,
					'bpmMultiplier': rate,
					"eventType": "SetSpeed",
					'floor': index,
					'speedType': 'Multiplier',
				})
			elif self.accelerates[index]['speedType'] == 'Multiplier':
				self.main['actions'][self.accelerates[index]['index']]['bpmMultiplier'] *= rate
			if not index in self.multiplanets:
				self.main['actions'].append({
					"eventType": "MultiPlanet",
					"floor": index,
					"planets": self.planets[index]['to'],
				})
			else:
				self.main['actions'][self.multiplanets[index]['index']]['planets'] = self.planets[index]['to']

		last_angle = self.main['angleData'][index - 2] if midspin else self.main['angleData'][index - 1] + 180
		self.main['angleData'][index] = round(last_angle - degree if clockwise else degree + last_angle, 2) % 360
		return self


	def convertByPlanets(self):
		'convert the whole level according to the planet amount set by Level.setPlanets()'
		for action in self.main['actions']:
			rate = self.planets[action['floor']]['from'] / self.planets[action['floor']]['to']
			for i in self._actions:
				if i in action:
					action[i] *= rate

		clockwise = True
		old_angle = 999
		old_planets = 2
		for i, angle in enumerate(self.main['angleData']):
			clockwise ^= i in self.twirls
			if angle != 999:
				i > 0 and self._computeAngle(angle, clockwise, i, old_angle, old_planets)
				old_angle = angle
				old_planets = self.planets[i]['to']

		useless_actions = []
		for i in self.main['actions']: # FIXME: useless bpm-changing actions cannot be removed
			i['eventType'] == 'SetSpeed' and i['bpmMultiplier'] == 1 and i['speedType'] == 'Multiplier' and useless_actions.append(i)
		for i, planet in enumerate(self.planets):
			i in self.multiplanets and (not i or planet['to'] != self.multiplanets[i] or self.planets[i - 1]['to'] == self.multiplanets[i]) and useless_actions.append(self.main['actions'][self.multiplanets[i]['index']])
		for i in useless_actions:
			self.main['actions'].remove(i)
		return self


	def dumpMain(self, file: IO[str] = None):
		'''Return (and dump) self.main.
			- file -- ``f`` from ``with open(...) as f`` (default:``None``)
		'''
		if file:
			dump(self.main, file)
		return self.main



if __name__ == '__main__':
	if len(argv) > 1:
		level = Level()
		parser = ArgumentParser(epilog = '''example:
  %(prog)s ./main.adofai 50:: :60:2
                        # Convert main.adofai
                        #   between Block 61 and the last block to 3 planets and
                        #   between the first block and Block 60 to 2 planets.
                        # The second option will override the first option.
''', formatter_class = RawDescriptionHelpFormatter, usage = '%(prog)s [-h] [<input_path> [<options>]]')
		parser.add_argument('input_path', help = SUPPRESS)
		parser.add_argument('-l', '--length', action = 'store_true', help = 'get the length of a lavel and exit')
		parser.add_argument('-o', '--output', help = 'set the output path (default: input_folder\input_file_name(3planets).adofai)', metavar = '<path>')
		parser.add_argument('-s', '--setting', help = "the converting setting (default: '::'), 0 < start_block ≤ end_block ≤ length, to_planets > 1", metavar = '[start_block]:[end_block]:[to_planets]', nargs = '+')
		args = parser.parse_args(namespace = Namespace(setting = ['::']))
		try:
			level.loadMainFromPath(args.input_path)
		except FileNotFoundError:
			parser.error('File not found.')
		except PermissionError:
			parser.error('Input file permission error.')
		except SyntaxError:
			parser.error('Syntax error occured. This file may not be an adofai level.')
		except UnicodeDecodeError:
			parser.error('Decode error occured. This file may not be an adofai level.')
		args.length and parser.exit(message = str(len(level)))
		level.loadLevelFromMain()
		for i in args.setting:
			try:
				start, end, to = i.split(':')
				level.setPlanets(1 if start == '' else int(start), level.length if end == '' else int(end), 3 if to == '' else int(to), lambda message: print(message, ' \033[93m', i, '\033[0m', sep = ''))
			except IndexError:
				parser.error('-s argument out of range: ' + '\033[93m' + i + '\033[0m')
			except ValueError:
				parser.error('Got wrong -s argument: ' + '\033[93m' + i + '\033[0m')

		input_path, input_extension = splitext(args.input_path)
		try:
			with open(args.output or input_path + '(3Planets)' + input_extension, 'w') as f:
				level.convertByPlanets().dumpMain(f)
		except PermissionError:
			parser.error('Output file permission error')
		parser.exit(message = 'Converted Success!')




	class Gui(Tk):
		def __init__(self, *args, **kargs):
			Tk.__init__(self, *args, **kargs)
			self.level = Level()
			self.main = dict()

	gui = Gui()
	gui.title('2 Planets To 3 Planets')


	def openFile():
		path = askopenfilename(filetypes = [('ADOFAI Levels', '*.adofai'), ('All files', '*')])
		level = Level()
		try:
			level.loadMainFromPath(path)
		except PermissionError:
			showwarning('Permission Error', 'Not enough permission to read the file.')
			return
		except SyntaxError:
			showwarning('Syntax Error', 'A syntax error occured. This file may not be an adofai level.')
			return
		except UnicodeDecodeError:
			showwarning('Unicode Decode Error', 'Decoding failed. This file may not be an adofai level.')
			return
		gui.level = level.loadLevelFromMain()
		gui.main = gui.level.dumpMain()

		gui.title(basename(path) + ' - 2 Planets to 3 Planets')
		open_box.config(state = 'normal')
		open_box.delete(0, 'end')
		open_box.insert(0, path)
		open_box.config(state = 'readonly')
		convert_button.config(state = 'normal')
		range_label.config(text = 'Min: 1  Max: ' + str(level.length))
		start_box.config(to = level.length)
		end_box.config(to = level.length)
		to_box.config(to = level.length)
		apply_button.config(state = 'normal')
		interval_label.config(text = 'Intervals to convert:')
		planets_info.delete(*planets_info.get_children())
		for i in level.multiplanets:
			planets_info.insert('', 'end', values=(i, level.multiplanets[i]['planets']))
		interval_info.delete(*interval_info.get_children())


	def convertPlanets():
		if not len(gui.main):
			level = deepcopy(gui.level)
			for i in interval_info.get_children():
				level.setPlanets(*interval_info.item(i)['values'])
			gui.main = level.convertByPlanets().dumpMain()
		try:
			with asksaveasfile(defaultextension = '*.adofai', filetypes=(('ADOFAI Levels', '*.adofai'), )) as f:
				dump(gui.main, f)
		except PermissionError:
			showwarning('Permission Error', 'Not enough permission to save the file.')

	file_frame = Frame(gui)
	open_box = Entry(file_frame, state = 'readonly', width = 40)
	open_button = Button(file_frame, command = openFile, text = 'Open File', width = 10)
	convert_button = Button(file_frame, command = convertPlanets, state = 'disabled', text = 'Convert As', width = 10)
	file_frame.pack()
	open_box.grid(column = 0, row = 0, padx = 5)
	open_button.grid(column = 1, row = 0, padx = 5)
	convert_button.grid(column = 2, row = 0, padx = 5)


	range_label = Label(gui)
	range_label.pack()


	# Add new interval
	def applyInterval():
		warning_message = ''
		try: # Catch NAN
			start = int(start_box.get())
			end = int(end_box.get())
			to = int(to_box.get())
			if start < 1:
				warning_message = 'The start block number is too small( < 1 ).\n'
			if end > gui.level.length:
				warning_message += 'The end block number is too large( > ' + str(gui.level.length) + ' ).\n'
			if start > end:
				warning_message += 'The start block number is larger than the end block number.\n'
			for i in interval_info.get_children():
				child_start, child_end, child_to = interval_info.item(i)['values']
				if child_start <= start <= child_end or child_start <= end <= child_end:
					warning_message += 'The internals coincide.\n'
					break
			if warning_message == '':
				interval_info.insert('', 'end', values=(start, end, to))
				gui.main = dict()
				return
		except ValueError:
			warning_message += 'Non-integer is inputed.'
		showwarning('Bad Converting Interval', warning_message)

	input_frame = Frame(gui)
	start_label = Label(input_frame, text = 'Start:')
	end_label = Label(input_frame, text = 'End:')
	to_label = Label(input_frame, text = 'To:')
	start_box, end_box, to_box = Spinbox(input_frame, from_ = 1, to = 1, width = 10), Spinbox(input_frame, from_ = 1, to = 1, width = 10), Spinbox(input_frame, from_ = 2, to = 0xffffffff, width = 10)
	apply_button = Button(input_frame, command = applyInterval, state = 'disabled', text = 'Apply New Interval')
	input_frame.pack()
	start_label.grid(column = 0, row = 0)
	start_box.grid(column = 1, row = 0)
	end_label.grid(column = 2, row = 0)
	end_box.grid(column = 3, row = 0)
	to_label.grid(column = 4, row = 0)
	to_box.grid(column = 5, row = 0)
	apply_button.grid(column = 6, row = 0, padx = 5)


	def deleteSelectedInterval(selected_interval):
		interval_info.delete(selected_interval)
		gui.main = dict()

	def postDeleteMenu(event):
		selected_interval = interval_info.identify_row(event.y)
		if selected_interval != '' or True:
			delete_menu.entryconfigure(0, command = lambda: deleteSelectedInterval(selected_interval))
			delete_menu.post(event.x + interval_info.winfo_rootx(), event.y + interval_info.winfo_rooty())

	table_frame = Frame(gui)
	planets_label = Label(table_frame, text = 'Existing MultiPlanets blocks:')
	interval_label = Label(table_frame, text = 'Intervals converting to 3 planets:')
	planets_info = Treeview(table_frame, columns = ['Block', 'Planets'], show = 'headings')
	planets_info.heading('Block', text = 'Block')
	planets_info.column('Block', width = 100)
	planets_info.heading('Planets', text = 'Planets')
	planets_info.column('Planets', width = 100)
	interval_info = Treeview(table_frame, columns = ['Start', 'End', 'To'], show = 'headings')
	interval_info.heading('Start', text = 'Start')
	interval_info.column('Start', width = 100)
	interval_info.heading('End', text = 'End')
	interval_info.column('End', width = 100)
	interval_info.heading('To', text = 'To')
	interval_info.column('To', width = 100)
	interval_info.bind('<Button-3>', postDeleteMenu)
	delete_menu = Menu(gui, tearoff= False)
	delete_menu.add_command(label='Delete')
	table_frame.pack()
	planets_label.grid(column = 0, row = 0)
	interval_label.grid(column = 1, row = 0)
	planets_info.grid(column = 0, row = 1, padx = 10)
	interval_info.grid(column = 1, row = 1, padx = 10)


	about_label = Label(gui, text = 'Repo: https://github.com/qwertycxz/ADOFAI-2PlanetsTo3Planets')
	about_label.bind('<Button-1>', lambda: open_new_tab('https://github.com/qwertycxz/ADOFAI-2PlanetsTo3Planets'))
	about_label.pack()
	gui.mainloop()