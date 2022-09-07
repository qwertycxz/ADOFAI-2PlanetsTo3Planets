from copy import deepcopy
from getopt import getopt, GetoptError
from json import dump
from os.path import basename, splitext
from sys import argv, exit
from tkinter import Button, Entry, Frame, Label, Menu, Spinbox, Tk
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter.messagebox import showwarning
from tkinter.ttk import Treeview
from webbrowser import open_new_tab
# Load a level: Convert pathData to angleData and get data of some very actions
def loadLevel(main):
	if main.__contains__('pathData'): # In the old version adofai levels, instead of angleData, there's pathData which is un-read-able. So convert pathData to angleData first
		main['angleData'] = []
		pathData = main.pop('pathData') # We don't need pathData anymore
		for c in pathData: # pathData is a string
			if c == 'R': # Ugly, but my python is too old(3.8) to do matching
				main['angleData'].append(0)
			elif c == 'p':
				main['angleData'].append(15)
			elif c == 'J':
				main['angleData'].append(30)
			elif c == 'E':
				main['angleData'].append(45)
			elif c == 'T':
				main['angleData'].append(60)
			elif c == 'o':
				main['angleData'].append(75)
			elif c == 'U':
				main['angleData'].append(90)
			elif c == 'q':
				main['angleData'].append(105)
			elif c == 'G':
				main['angleData'].append(120)
			elif c == 'Q':
				main['angleData'].append(135)
			elif c == 'H':
				main['angleData'].append(150)
			elif c == 'W':
				main['angleData'].append(165)
			elif c == 'L':
				main['angleData'].append(180)
			elif c == 'x':
				main['angleData'].append(195)
			elif c == 'N':
				main['angleData'].append(210)
			elif c == 'Z':
				main['angleData'].append(225)
			elif c == 'F':
				main['angleData'].append(240)
			elif c == 'V':
				main['angleData'].append(255)
			elif c == 'D':
				main['angleData'].append(270)
			elif c == 'Y':
				main['angleData'].append(285)
			elif c == 'B':
				main['angleData'].append(300)
			elif c == 'C':
				main['angleData'].append(315)
			elif c == 'M':
				main['angleData'].append(330)
			elif c == 'A':
				main['angleData'].append(345)
			elif c == '!':
				main['angleData'].append(999)
	accelerates, holds, multiplanets, twirls = {}, {}, {}, {} # Four different actions data
	for i, action in enumerate(main['actions']): # Enumerate all the actions
		if action['eventType'] == 'Hold': # Lots of if-else
			holds[action['floor']] = {
				'degree': action['duration'] * 360,
				'index': i,
			}
		elif action['eventType'] == 'MultiPlanet':
			multiplanets[action['floor']] = {
				'index': i,
				'planets': action['planets'],
			}
		elif action['eventType'] == 'SetSpeed':
			accelerates[action['floor']] = {
				'index': i,
				'speedType': action['speedType'],
			}
		elif action['eventType'] == 'Twirl':
			twirls[action['floor']] = True
	length = len(main['angleData']) # How many blocks do we have?
	planet = 2 # What's the number of planets now?
	planets = [] # All the planets amount. Positive number is the existed amount. Negative number is going to convert
	for i in range(length + 1): # From Block 0 to the end block
		if multiplanets.__contains__(i): # Each time acting MultiPlanets, change the planet amount
			planet = multiplanets[i]['planets']
		planets.append(planet)
	return accelerates, holds, multiplanets, twirls, length, main, planets
# Math time!
def convertLevel(convert_interval, from_amount, to_amount, main, planets):
	for i, action in enumerate(main['actions']): # Enumerate all the actions
		if planets[action['floor']] == -to_amount: # All planets to convert should be from_amount / to_amount speed
			if action['eventType'] == 'AnimateTrack': # FIXME: The decorations moves are now working bad
				action['beatsAhead'] *= from_amount / to_amount
				action['beatsBehind'] *= from_amount / to_amount
			elif action['eventType'] == 'SetSpeed':
				main['actions'][i]['beatsPerMinute'] *= from_amount / to_amount
			elif action.__contains__('duration'):
				action['duration'] *= from_amount / to_amount
			elif action.__contains__('holdMidSoundDelay'):
				action['holdMidSoundDelay'] *= from_amount / to_amount
			elif action.__contains__('repetitions'):
				action['repetitions'] *= from_amount / to_amount
	# Put SetSpeed and MultiPlanet actions
	def accelerate(position, planet_amount, new_planet_amount, force_muti_planets=False):
		if not accelerates.__contains__(position): # No SetSpeed action, then add one
			accelerates[position] = {
				'index': len(main['actions']),
				'speedType': 'Multiplier',
			}
			main['actions'].append({
				'beatsPerMinute': 100,
				'bpmMultiplier': planet_amount / new_planet_amount,
				"eventType": "SetSpeed",
				'floor': position,
				'speedType': 'Multiplier',
			})
		elif accelerates[position]['speedType'] == 'Multiplier':
			main['actions'][accelerates[position]['index']]['bpmMultiplier'] *= planet_amount / new_planet_amount
		if not multiplanets.__contains__(position): # No MultiPlanet action, then add one
			main['actions'].append({
				"eventType": "MultiPlanet",
				"floor": position,
				"planets": new_planet_amount,
			})
		elif force_muti_planets:
			main['actions'][multiplanets[position]['index']]['planets'] = new_planet_amount
	for start, end in convert_interval: # Enumerate all the intervals
		if start == 1: # I don't like to place a Block-1 SetSpeed, let's just change the whole level's BPM
			main['settings']['bpm'] *= from_amount / to_amount
			main['actions'].append({
				"eventType": "MultiPlanet",
				"floor": start,
				"planets": to_amount,
			})
		else:
			accelerate(start, from_amount, to_amount, True)
		if end != length: # The goal needn't have any speed change
			accelerate(end, to_amount, from_amount)
	clockwise = True # And the real mathematics begin!
	old_angle = 999 # 999 means a midspin
	# 0 <= angle < 360, 0 < degree <= 360
	def setAngle(angle, is_degree=False):
		if angle < -360 or angle == -360 and is_degree: # Only elevator dance will take -360 degree, I suppose
			angle += 720
		elif angle < 0 or angle == 0 and is_degree:
			angle += 360
		elif angle > 360:
			angle -= 360
		return angle
	for i, angle in enumerate(main['angleData']): # Enumerate all the blocks
		if twirls.__contains__(i): # Twirls make clockwise to counterclockwise, vice versa
			clockwise = not clockwise
		if angle != 999: # 999 means a midspin
			if i > 0: # No need to convert Block 0
				if main['angleData'][i - 1] != 999: # The angles of the blocks after midspin are not as same as after normal blocks
					old_angle += 180
				delta_degree = angle - old_angle # Assume the delta to two angles is degree
				if clockwise: # Clockwise and counterclockwise don't share the same angle
					delta_degree = old_angle - angle
				degree = setAngle(delta_degree, True) # 0 < degree <= 360
				if planets[i] == -to_amount: # Convert minus amount
					if main['angleData'][i - 1] != 999: # The degrees of the blocks after midspin are not as same as after normal blocks
						degree -= (from_amount - 2) * 180 / from_amount
					degree *= from_amount / to_amount
					if main['angleData'][i - 1] != 999: # The degrees of the blocks after midspin are not as same as after normal blocks
						degree += (to_amount - 2) * 180 / to_amount
					if holds.__contains__(i): # The degrees of the blocks before hold are not as same as after normal blocks
						hold_degree = holds[i]['degree']
						if degree <= (from_amount - 2) * 180 / from_amount: # Degrees smaller than 60 degree need this
							hold_degree += 360
						hold_degree = degree + hold_degree * from_amount / to_amount # One lap used to be a 360° now is 240°
						degree = hold_degree % 360
						if degree <= (to_amount - 2) * 180 / to_amount:  # Degrees smaller than 60 degree need this
							hold_degree -= 360
						main['actions'][holds[i]['index']]['duration'] = (hold_degree - degree) / 360
				last_angle = main['angleData'][i - 2] # When midspins, angle count from i - 2 angle
				if main['angleData'][i - 1] != 999: # When not midspins, angle count from i - 1 angle
					last_angle = main['angleData'][i - 1] + 180
				delta_angle = degree + last_angle # Assume the delta to two angles is degree, but inverse operation
				if clockwise: # Clockwise and counterclockwise don't share the same angle
					delta_angle = last_angle - degree
				main['angleData'][i] = setAngle(delta_angle)
			old_angle = angle
	useless_actions = [] # FIXME: The useless-actions collect function is not working well
	for action in main['actions']: # Delate useless multiplanets and SetSpeed actions
		if action['eventType'] == 'MultiPlanet' and abs(planets[action['floor']]) == abs(planets[action['floor'] - 1]) or action['eventType'] == 'SetSpeed' and action['bpmMultiplier'] == 1 and action['speedType'] == 'Multiplier': # If a multiplanets don't change the number of planets or a SetSpeed don't change the speed, then it‘s useless
			useless_actions.append(action)
	for action in useless_actions: # Delete useless actions
		main['actions'].remove(action)
	return main
if len(argv) > 1: # CLI mode
	# Error happened. Print some messages to user
	def exitWithMessage(*error_message):
		print(*error_message)
		exit()
	help_message = '\n\nUsage:\n\tpython 2PlanetsTo3Planets.py [<input_path> [options]]\n\nGeneral Options:\n\t-f <number>\tSet the from-planet amount. Default 2\n\t-t <number>\tSet the to-planet amount. Default 3\n\t-s <number>\tSet the start of converting. Default the first block(-s 1).\n\t-e <number>\tSet the end of converting. Default the last block.\n\t-o <path>\tSet the output path.\n\t-m\t\tMultiple input mode. Ingore -s or -e options.' # Help
	try: # File operations always have to do a LOT of error catching
		with open(argv[1], encoding='utf-8-sig') as f: # Argv[1] is the adofai file, UTF8SIG encoded
			true = True
			false = False
			try: # Don't ask me why there's so many replacing. 7th beats is suck at JSON
				main = eval(f.read().replace(']\n', '],').replace('\n', '').replace(',,', ','))
			except SyntaxError:
				exitWithMessage('Error: Syntax error occured. This file may not be an adofai level.')
			except UnicodeDecodeError:
				exitWithMessage('Error: Decode error occured. This file may not be an adofai level.')
	except FileNotFoundError:
		exitWithMessage('Error: File not found.', help_message)
	except IndexError:
		exitWithMessage('Error: No <input_path>.', help_message)
	except PermissionError:
		exitWithMessage('Error: Input file permission error.', help_message)
	accelerates, holds, multiplanets, twirls, length, main, planets = loadLevel(main) # Load this level
	convert_interval = [[1, length]] # Default convert interval
	from_amount, to_amount = 2, 3 # Default converting 2 planets to 3 planets
	input_path, input_extension = splitext(argv[1]) # Get the input path and extension
	output_path = input_path + '(3Planets)' + input_extension # If no -o, output new file as input_path + '(3Planets)' + input_extension
	multiple_input_mode = False # Default single input mode
	try: # Options operation
		options, arguments = getopt(argv[2:],'-m-s:-e:-o:-f:-t:') # See help!
		for i, option in options: # More ugly if and else
			try: # Foolproof
				if i == '-m':
					multiple_input_mode = True
				elif i == '-s':
					convert_interval[0][0] = int(option)
				elif i == '-e':
					convert_interval[0][1] = int(option)
				elif i == '-o':
					output_path = option
				elif i == '-f':
					from_amount = int(option)
				elif i == '-t':
					to_amount = int(option)
			except ValueError:
				exitWithMessage('Error: A non-integer option inputed.', help_message)
	except GetoptError:
		exitWithMessage('Error: Option is incorrect.', help_message)
	# Giving out multiplanets information letting user don't convert 3 planets to 3 planets
	def printMultiplanetsInformation():
		if len(multiplanets) > 0: # Only print if there're multiplanets actions
			print('multiplanets information:')
			for index in multiplanets: # Print all actions
				print('Block', index, '\t', multiplanets[index]['planets'], 'planets')
	# Record how many planets do we have now (2: Two, 3: Three already exists, -3: Two to three)
	def recordPlanetsAmount(start, end, treat_warning_as_error=False):
		if start >= end: # No reverse order
			if treat_warning_as_error: # Treat warning as error if not using -m option
				exitWithMessage('Error: The start block number is larger than the end block number.')
			print('Warning: The start block number is larger than the end block number. Ingored.')
			return
		if start < 1: # NEVER CONVERT BLOCK 0 TO 3 PLANETS! Why? Try yourself
			if treat_warning_as_error: # Treat warning as error if not using -m option
				exitWithMessage('Error: The start block number is too small( < 1 ).')
			print('Warning: The start block number is too small( < 1 ). Ingored.')
			return
		if end > length: # Nonsense
			if treat_warning_as_error: # Treat warning as error if not using -m option
				exitWithMessage('Error: The end block number is too large( >', length, ').')
			print('Warning: The end block number is too large( >', length, '). Ingored.')
			return
		for i in range(start, end): # start <= range() < end
			if planets[i] != 2: # Not 2, then 3 or -3
				if treat_warning_as_error: # Treat warning as error if not using -m option
					print('Error: Converting 3 planets to 3 planets in banned.')
					printMultiplanetsInformation()
					exit()
				print('Warning: Converting 3 planets to 3 planets in banned. Ingored.')
				printMultiplanetsInformation()
				return
		for i in range(start, end): # OK to convert
			planets[i] = -3
		return True
	if multiple_input_mode: # Do multiple input
		print('Multiple input mode is on. You are supposed to input even number of integers which means the start and the end of one converting.\nMinimum: 1  Maximum:', length)
		printMultiplanetsInformation()
		print('Press Ctrl-Z then Enter to stop.')
		convert_interval = []
		while True: # ICPC told me to do so
			try: # Not only catch NAN, but also EOF
				start = int(input('Please input the start block number:'))
				end = int(input('Please input the end block number:'))
				if recordPlanetsAmount(start, end): # If record success, then this interval is legal
					convert_interval.append((start, end))
			except EOFError:
				if len(convert_interval) < 1: # No blocks, no convert
					exitWithMessage('Error: No blocks to convert.')
				break
			except ValueError:
				print('Warning: Non-integer inputed. Ingored.')
	else:
		recordPlanetsAmount(convert_interval[0][0], convert_interval[0][1], True)
	main = convertLevel(convert_interval, from_amount, to_amount, main, planets)
	try: # File operations always have to do a LOT of error catching
		with open(output_path, 'w') as f: # Finally I could dump a JSON
			dump(main, f)
	except PermissionError:
		exitWithMessage('Error: Output file permission error', help_message)
	print('Converting Complete!')
else:
	INFINITE = 0xffffffff # 4294967295
	gui = Tk() # main GUI
	gui.title('2 Planets To 3 Planets')
	convert_frame = Frame(gui) # Convert n planets to m planets
	convert_label_1 = Label(convert_frame, text='From') # From
	convert_label_2 = Label(convert_frame, text='planets to') # planets to
	convert_label_3 = Label(convert_frame, text='planets') # planets
	from_box, to_box = Spinbox(convert_frame, from_=2, to=INFINITE, width=10), Spinbox(convert_frame, from_=2, to=INFINITE, width=10) # 2 simple input box
	# Reset all gui
	def reset():
		gui.title(str(from_amount) + ' Planets to ' + str(to_amount) + ' Planets')
		from_box.config(state='normal')
		to_box.config(state='normal')
		open_box.config(state='normal')
		open_box.delete(0, 'end')
		open_box.config(state='readonly')
		convert_button.config(state='disabled')
		range_label.config(text='')
		apply_button.config(state='disabled')
		interval_label.config(text='Intervals converting to 3 planets:')
		planets_info.delete(*planets_info.get_children())
		interval_info.delete(*interval_info.get_children())
		reset_button.config(state='disabled')
	reset_button = Button(convert_frame, command=reset, state='disabled', text='Reset', width=10) # Click to reset
	to_box.delete(0)
	to_box.insert(0, '3')
	file_frame = Frame(gui) # Path, file-open button and convert-as button
	open_box = Entry(file_frame, state='readonly', width=40) # Don't edit manually
	from_amount = 2 # 2 Planets
	to_amount = 3 # to 3 Planets
	# Open and read a file
	def openFile():
		global accelerates, holds, multiplanets, twirls, from_amount, to_amount, length, main, planets
		try: # Should be a number
			from_amount = int(from_box.get())
			to_amount = int(to_box.get())
		except ValueError:
			showwarning('Bad Planets Amount', 'Non-integer is inputed.')
			return
		if from_amount <= 1 or to_amount <= 1: # 1 planet LOL NO
			showwarning('Bad Planets Amount', 'The planets amount is too small(<2).')
		elif from_amount >= INFINITE or to_amount >= INFINITE:
			showwarning('NO NO NO!', 'The planets amount is too large!\nYou must be kidding!')
		else:
			file_name = askopenfilename(filetypes=[('ADOFAI Levels', '*.adofai'), ('All files', '*')]) # Although not necessary, I allowed to choose all files
			try: # File operations always have to do a LOT of error catching
				with open(file_name, encoding='utf-8-sig') as f: # The level file is encoded as UTF-8-SIG
					true = True # An ADOFAI level should be a json, read by eval() should have the boolean change
					false = False # Why not just directly read the level as JSON? Because this JSON-like file actually don't follow JSON rules
					try: # Don't ask me why there's so many replacing. 7th beats is suck at JSON
						main = eval(f.read().replace(']\n', '],').replace('\n', '').replace(',,', ','))
					except SyntaxError:
						showwarning('Syntax Error', 'A syntax error occured. This file may not be an adofai level.')
						return
					except UnicodeDecodeError:
						showwarning('Unicode Decode Error', 'Decoding failed. This file may not be an adofai level.')
						return
			except PermissionError:
				showwarning('Permission Error', 'Not enough permission to read the file.')
				return
			accelerates, holds, multiplanets, twirls, length, main, planets = loadLevel(main) # Load the level
			# GUI things
			gui.title(basename(file_name) + ' - ' + str(from_amount) + ' Planets to ' + str(to_amount) + ' Planets')
			from_box.config(state='readonly')
			to_box.config(state='readonly')
			reset_button.config(state='normal')
			open_box.config(state='normal')
			open_box.delete(0, 'end')
			open_box.insert(0, file_name)
			open_box.config(state='readonly')
			convert_button.config(state='normal')
			range_label.config(text='Min: 1  Max: ' + str(length))
			start_box.config(to=length)
			end_box.config(to=length)
			apply_button.config(state='normal')
			interval_label.config(text='Intervals converting to ' + str(to_amount) + ' planets:')
			planets_info.delete(*planets_info.get_children())
			for index in multiplanets: # Display all Multiplanets actions
				planets_info.insert('', 'end', values=(index, multiplanets[index]['planets']))
			interval_info.delete(*interval_info.get_children())
	open_button = Button(file_frame, command=openFile, text='Open File', width=10) # Open a file and read it as an ADOFAI level (if possable)
	# Convert the whole level and dump it as a real json
	def convertPlanets():
		convert_interval = []
		for child in interval_info.get_children(): # Enumerate all the children
			convert_interval.append(interval_info.item(child)['values']) # Children's values are the intervals
		new_main = convertLevel(convert_interval, from_amount, to_amount, deepcopy(main), planets)
		try: # File operations always have to do a LOT of error catching
			with asksaveasfile(defaultextension='*.adofai', filetypes=(('ADOFAI Levels', '*.adofai'), )) as f: # Finally I could dump a JSON
				dump(new_main, f)
		except PermissionError:
			showwarning('Permission Error', 'Not enough permission to save the file.')
	convert_button = Button(file_frame, command=convertPlanets, state='disabled', text='Convert As', width=10) # Convert a deepcopy of main, then save as file
	range_label = Label(gui) # Max and min label
	input_frame = Frame(gui) # Label and input box of start and end with an apply button
	start_label = Label(input_frame, text='Start:') # A never-changing label
	end_label = Label(input_frame, text='End:') # A never-changing label
	start_box, end_box = Spinbox(input_frame, from_=1, to=INFINITE, width=10), Spinbox(input_frame, from_=1, to=INFINITE, width=10) # 2 simple input box
	# Add new interval
	def applyInterval():
		try: # Catch NAN
			start = int(start_box.get()) # str to int
			end = int(end_box.get()) # If error, then not a int
			# When converting planet amount is not correct, give out warnings
			def isConverting3planets():
				for i in range(start, end): # start <= range() < end
					if planets[i] != from_amount: # FIXME: I'm bad at English. How could I explain this warning message?
						showwarning('Bad Converting Interval', 'From planet amount is incorrect.')
						return True
			if start < 1: # NEVER GIVE BLOCK 0 MULTIPLANETS! Why? Try yourself
				showwarning('Bad Converting Interval', 'The start block number is too small(<1)')
			elif end > length:
				showwarning('Bad Converting Interval', 'The end block number is too large(>' + str(length) + ').')
			elif start >= end:
				showwarning('Bad Converting Interval', 'The start block number is larger than the end block number.')
			elif not isConverting3planets(): # Final test
				for i in range(start, end): # OK to convert
					planets[i] = -to_amount
				interval_info.insert('', 'end', values=(start, end))
		except ValueError:
			showwarning('Bad Converting Interval', 'Non-integer is inputed.')
	apply_button = Button(input_frame, command=applyInterval, state='disabled', text='Apply New Interval') # Add a convert to interval_label
	table_frame = Frame(gui) # 2 label and 2 table
	planets_label = Label(table_frame, text='Existing MultiPlanets blocks:') # A never-changing label
	interval_label = Label(table_frame, text='Intervals converting to 3 planets:') # A never-changing label
	planets_info = Treeview(table_frame, columns=['Block', 'Planets'], show='headings') # A table made by Treeview
	planets_info.heading('Block', text='Block')
	planets_info.column('Block', width=100)
	planets_info.heading('Planets', text='Planets')
	planets_info.column('Planets', width=100)
	interval_info = Treeview(table_frame, columns=['Start', 'End'], show='headings') # A table made by Treeview
	interval_info.heading('End', text='End')
	interval_info.column('End', width=100)
	interval_info.heading('Start', text='Start')
	interval_info.column('Start', width=100)
	selected_interval = '' # Global var, ugly but useful
	# Delete interval menu
	def deleteInterval(event):
		global selected_interval
		selected_interval = interval_info.identify_row(event.y)
		if selected_interval != '': # Don't show if nothing cilcked
			delete_menu.post(event.x + interval_info.winfo_rootx(), event.y + interval_info.winfo_rooty())
	interval_info.bind('<Button-3>', deleteInterval)
	delete_menu = Menu(gui, tearoff= False) # A popup menu
	# Remove a interval forever
	def removeInterval():
		for i in range(*interval_info.item(selected_interval)['values']): # All the to-amount deleted are should be back to from-amount
			planets[i] = from_amount
		interval_info.delete(selected_interval)
	delete_menu.add_cascade(command=removeInterval, label='Delete')
	about_label = Label(gui, text='Repo: https://github.com/qwertycxz/ADOFAI-2PlanetsTo3Planets') # About the repo :)
	about_label.bind('<Button-1>', lambda event: open_new_tab('https://github.com/qwertycxz/ADOFAI-2PlanetsTo3Planets'))
	# Pack GUI
	convert_frame.pack(pady=5)
	convert_label_1.grid(column=0, row=0)
	from_box.grid(column=1, row=0)
	convert_label_2.grid(column=2, row=0)
	to_box.grid(column=3, row=0)
	convert_label_3.grid(column=4, row=0)
	reset_button.grid(column=5, row=0)
	file_frame.pack()
	open_box.grid(column=0, row=0, padx=5)
	open_button.grid(column=1, row=0, padx=5)
	convert_button.grid(column=2, row=0, padx=5)
	range_label.pack()
	input_frame.pack()
	start_label.grid(column=0, row=0)
	start_box.grid(column=1, row=0)
	end_label.grid(column=2, row=0)
	end_box.grid(column=3, row=0)
	apply_button.grid(column=4, row=0, padx=5)
	table_frame.pack()
	planets_label.grid(column=0, row=0)
	interval_label.grid(column=1, row=0)
	planets_info.grid(column=0, row=1, padx=10)
	interval_info.grid(column=1, row=1, padx=10)
	about_label.pack()
	gui.mainloop()