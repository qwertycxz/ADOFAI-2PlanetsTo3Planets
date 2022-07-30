from asyncio.windows_events import INFINITE
from copy import deepcopy
from json import dump
from os.path import basename
from tkinter import Button, Entry, Frame, Label, Menu, Spinbox, Tk
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter.messagebox import showwarning
from tkinter.ttk import Treeview
from webbrowser import open_new_tab
gui = Tk() # main GUI
gui.title('2 Planets To 3 Planets')
file_frame = Frame(gui) # Path, file-open button and convert-as button
open_box = Entry(file_frame, state='readonly', width=40) # Don't edit manually
accelerates, holds, main, multiplanets, twirls = {}, {}, {}, {}, {} # Record main.adofai and these 4 actions
length = 0 # How many blocks do we have?
planets = [] # Planet amount
# Open and read a file
def openFile():
	global accelerates, holds, length, main, multiplanets, planets, twirls
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
	fifteen = set()
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
			else:
				fifteen.add(c)
	print(fifteen)
	accelerates, holds, multiplanets, twirls = {}, {}, {}, {}
	for i, action in enumerate(main['actions']): # Enumerate all the actions
		if action['eventType'] == 'Hold' and action['duration'] > 0: # Only record holds more than 1 lap
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
	length = len(main['angleData'])
	planet = 2 # What's the number of planets now?
	planets = []
	for i in range(length + 1): # From Block 0 to the end block
		if multiplanets.__contains__(i): # Each time acting MultiPlanets, change the planet amount
			planet = multiplanets[i]['planets']
		planets.append(planet)
	# GUI things
	gui.title(basename(file_name) + ' - 2 Planets to 3 Planets')
	open_box.config(state='normal')
	open_box.select_clear()
	open_box.insert(0, file_name)
	open_box.config(state='readonly')
	convert_button.config(state='normal')
	range_label.config(text='Min: 1  Max: ' + str(length))
	start_box.config(to=length)
	end_box.config(to=length)
	apply_button.config(state='normal')
	planets_info.delete(*planets_info.get_children())
	for index in multiplanets: # Display all Multiplanets actions
		planets_info.insert('', 'end', values=(index, multiplanets[index]['planets']))
	interval_info.delete(*interval_info.get_children())
open_button = Button(file_frame, command=openFile, text='Open File', width=10) # Open a file and read it as an ADOFAI level (if possable)
# Convert the whole level and dump it as a real json
def convertPlanets():
	new_main = deepcopy(main) # Deepcopy the main
	for i, action in enumerate(new_main['actions']): # Enumerate all the actions
		if action['eventType'] == 'SetSpeed' and planets[action['floor']] == -3: # All -3 planets should be 66.66666% speed
			new_main['actions'][i]['beatsPerMinute'] *= 2 / 3
	# Put SetSpeed and MultiPlanet actions
	def accelerate(position, planet_amount, new_planet_amount, force_muti_planets=False):
		if not accelerates.__contains__(position): # No SetSpeed action, then add one
			accelerates[position] = {
				'index': len(new_main['actions']),
				'speedType': 'Multiplier',
			}
			new_main['actions'].append({
				'beatsPerMinute': 100,
				'bpmMultiplier': planet_amount / new_planet_amount,
				"eventType": "SetSpeed",
				'floor': position,
				'speedType': 'Multiplier',
			})
		elif accelerates[position]['speedType'] == 'Multiplier':
			new_main['actions'][accelerates[position]['index']]['bpmMultiplier'] *= planet_amount / new_planet_amount
		if not multiplanets.__contains__(position): # No MultiPlanet action, then add one
			new_main['actions'].append({
				"eventType": "MultiPlanet",
				"floor": position,
				"planets": new_planet_amount,
			})
		elif force_muti_planets:
			new_main['actions'][multiplanets[position]['index']]['planets'] = new_planet_amount
	for child in interval_info.get_children(): # Enumerate all the children
		values = interval_info.item(child)['values'] # Children's values are the intervals
		if values[0] == 1: # I don't like to place a Block-1 SetSpeed, let's just change the whole level's BPM
			new_main['settings']['bpm'] *= 2 / 3
			new_main['actions'].append({
				"eventType": "MultiPlanet",
				"floor": values[0],
				"planets": 3,
			})
		else:
			accelerate(values[0], 2, 3, True)
		if values[1] != length: # The goal needn't have any speed change
			accelerate(values[1], 3, 2)
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
	for i, angle in enumerate(new_main['angleData']): # Enumerate all the blocks
		if twirls.__contains__(i): # Twirls make clockwise to counterclockwise, vice versa
			clockwise = not clockwise
		if angle != 999: # 999 means a midspin
			if i > 0: # No need to convert Block 0
				if new_main['angleData'][i - 1] != 999: # The angles of the blocks after midspin are not as same as after normal blocks
					old_angle += 180
				delta_degree = angle - old_angle # Assume the delta to two angles is degree
				if clockwise: # Clockwise and counterclockwise don't share the same angle
					delta_degree = old_angle - angle
				degree = setAngle(delta_degree, True) # 0 < degree <= 360
				if planets[i] == -3: # Convert -3
					degree *= 2 / 3
					if new_main['angleData'][i - 1] != 999: # The degrees of the blocks after midspin are not as same as after normal blocks
						degree += 60
					if holds.__contains__(i): # The degrees of the blocks before hold are not as same as after normal blocks
						hold_degree = degree + holds[i]['degree'] * 2 / 3 # One lap used to be a 360° now is 240°
						degree = hold_degree % 360
						if degree <= 60:
							hold_degree -= 360
						new_main['actions'][holds[i]['index']]['duration'] = (hold_degree - degree) / 360
				last_angle = new_main['angleData'][i - 2] # When midspins, angle count from i - 2 angle
				if new_main['angleData'][i - 1] != 999: # When not midspins, angle count from i - 1 angle
					last_angle = new_main['angleData'][i - 1] + 180
				delta_angle = degree + last_angle # Assume the delta to two angles is degree, but inverse operation
				if clockwise: # Clockwise and counterclockwise don't share the same angle
					delta_angle = last_angle - degree
				new_main['angleData'][i] = setAngle(delta_angle)
			old_angle = angle
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
		# When converting 3 planets to 3 planets, give out warnings
		def isConverting3planets():
			for i in range(start, end): # start <= range() < end
				if planets[i] != 2: # Not 2, then 3 or -3
					showwarning('Bad Converting Interval', 'Converting 3 planets to 3 planets is prohibited.')
					return True
		if start < 1: # NEVER CONVERT BLOCK 0 TO 3 PLANETS! Why? Try yourself
			showwarning('Bad Converting Interval', 'The start block number is too small(<1)')
		elif end > length:
			showwarning('Bad Converting Interval', 'The end block number is too large(>' + str(length) + ').')
		elif start >= end:
			showwarning('Bad Converting Interval', 'The start block number is larger than the end block number.')
		elif not isConverting3planets(): # Final test
			for i in range(start, end): # OK to convert
				planets[i] = -3
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
	for i in range(*interval_info.item(selected_interval)['values']): # All the -3 amount deleted are should be 2
		planets[i] = 2
	interval_info.delete(selected_interval)
delete_menu.add_cascade(command=removeInterval, label='Delete')
about_label = Label(gui, text='Repo: https://github.com/qwertycxz/ADOFAI-2PlanetsTo3Planets') # About the repo :)
about_label.bind('<Button-1>', lambda event: open_new_tab('https://github.com/qwertycxz/ADOFAI-2PlanetsTo3Planets'))
# Pack GUI
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
