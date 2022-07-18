from getopt import getopt, GetoptError
from json import dump
from os.path import splitext
from sys import argv, exit
# Error happened. Print some messages to tell user
def exitWithMessage(*error_message):
	print(*error_message)
	exit()
# Help
def exitWithHelp(*error_message):
	exitWithMessage(*error_message, '\n\nUsage:\n\tpython 2PlanetsTo3Planets.py <input_path> [options]\n\nGeneral Options:\n\t-s <number>\tSet the start of converting. Default the first block(-s 1).\n\t-e <number>\tSet the end of converting. Default the last block.\n\t-o <path>\tSet the output path.\n\t-m\tMultiple input mode. Ingore -s or -e options.')
# 0 <= angle < 360, 0 < degree <= 360
def setAngle(angle, is_degree=False):
	if angle < -360 or angle == -360 and is_degree: # Only elevator dance will take -360 degree, I suppose
		angle += 720
	elif angle < 0 or angle == 0 and is_degree:
		angle += 360
	elif angle > 360:
		angle -= 360
	return angle
main = {} # main.adofai content
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
	exitWithHelp('Error: File not found.')
except IndexError:
	exitWithHelp('Error: No <input_path>.')
except PermissionError:
	exitWithHelp('Error: Input file permission error.')
if main.__contains__('pathData'): # In the old version adofai levels, instead of angldData, there's pathData which is un-read-able. So convert pathData to angleData first
	main['angleData'] = []
	pathData = main.pop('pathData') # We don't need pathData anymore
	for c in pathData: # pathData is a string
		if c == 'R': # Ugly, but my python is too old(3.8) to do matching
			main['angleData'].append(0)
		elif c == 'J':
			main['angleData'].append(30)
		elif c == 'E':
			main['angleData'].append(45)
		elif c == 'T':
			main['angleData'].append(60)
		elif c == 'U':
			main['angleData'].append(90)
		elif c == 'G':
			main['angleData'].append(120)
		elif c == 'Q':
			main['angleData'].append(135)
		elif c == 'H':
			main['angleData'].append(150)
		elif c == 'L':
			main['angleData'].append(180)
		elif c == 'N':
			main['angleData'].append(210)
		elif c == 'Z':
			main['angleData'].append(225)
		elif c == 'F':
			main['angleData'].append(240)
		elif c == 'D':
			main['angleData'].append(270)
		elif c == 'B':
			main['angleData'].append(300)
		elif c == 'C':
			main['angleData'].append(315)
		elif c == 'M':
			main['angleData'].append(330)
		elif c == '!':
			main['angleData'].append(999)
input_path, input_extension = splitext(argv[1]) # If no -o, output new file as input_path + '(3Planets)' + input_extension
length = len(main['angleData']) # How many blocks do we have?
convert_interval, multiple_input_mode, output_path = [[1, length]], False, input_path + '(3Planets)' + input_extension # Default options
try: # Options operation
	options, arguments = getopt(argv[2:],'-m-s:-e:-o:') # See help!
	for i, option in options: # More ugly if and else
		try: # Foolproof
			if i == '-m': # See Line 157
				multiple_input_mode = True
			elif i == '-s':
				convert_interval[0][0] = int(option)
			elif i == '-e':
				convert_interval[0][1] = int(option)
			elif i == '-o':
				output_path = option
		except ValueError:
			exitWithHelp('Error: A non-integer option inputed.')
except GetoptError:
	exitWithHelp('Error: Option is incorrect.')
accelerates, holds, mutiplanets, twirls = {}, {}, {}, {} # Record these 4 actions
for i, action in enumerate(main['actions']): # Enumerate all the actions
	if action['eventType'] == 'Hold' and action['duration'] > 0: # Only record holds more than 1 lap
		holds[action['floor']] = {
			'degree': action['duration'] * 360,
			'index': i,
		}
	elif action['eventType'] == 'MultiPlanet':
		mutiplanets[action['floor']] = {
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
planet, planets = 2, [] # Record planets amount of all blocks
for i, angle in enumerate(main['angleData']): # Enumerate all the blocks
	if mutiplanets.__contains__(i): # Each time acting MutiPlanets, change the former planet amount
		planet = mutiplanets[i]['planets']
	planets.append(planet)
# Giving out MutiPlanets information letting user don't convert 3 planets to 3 planets
def printMutiPlanetsInformation():
	if len(mutiplanets) > 0: # Only print if there're MutiPlanets actions
		print('MutiPlanets information:')
		for index in mutiplanets: # Print all actions
			print('Block', index, '\t', mutiplanets[index]['planets'], 'planets')
# When converting 3 planets to 3 planets, give out warnings
def isConverting3planets(start, end, treat_warning_as_error):
	for i in range(start, end): # start <= range() < end
		if planets[i] != 2: # Not 2, then 3 or -3
			if treat_warning_as_error: # Treat warning as error if not using -m option
				print('Error: Converting 3 planets to 3 planets in banned.')
				printMutiPlanetsInformation()
				exit()
			print('Warning: Converting 3 planets to 3 planets in banned. Ingored.')
			printMutiPlanetsInformation()
			return True
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
	if not isConverting3planets(start, end, treat_warning_as_error): # Final test
		for i in range(start, end): # OK to convert
			planets[i] = -3
		return True
if multiple_input_mode: # Do multiple input
	print('Multiple input mode is on. You are supposed to input even number of integers which means the start and the end of one converting.\nMinimum: 1  Maximum:', length)
	printMutiPlanetsInformation()
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
for i, action in enumerate(main['actions']): # All -3 planets should be 66.66666%
	if action['eventType'] == 'SetSpeed' and planets[action['floor']] == -3:
		main['actions'][i]['beatsPerMinute'] *= 2 / 3
# Put SetSpeed action and MultiPlanet
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
	elif accelerates[position]['speedType'] == 'Multiplier': # BPM-type actions are converted at Line 176, so only convert Multiplier-type actions
		main['actions'][accelerates[position]['index']]['bpmMultiplier'] *= planet_amount / new_planet_amount
	if not mutiplanets.__contains__(position): # No MultiPlanet action, then add one
		main['actions'].append({
			"eventType": "MultiPlanet",
			"floor": position,
			"planets": new_planet_amount,
		})
	elif force_muti_planets: # Start block must be 3 planets, but end block needn't
		main['actions'][mutiplanets[position]['index']]['planets'] = new_planet_amount
for start, end in convert_interval: # Enumerate all the intervals
	if start == 1: # I don't like to place a Block-1 SetSpeed, let's just change the whole level's BPM
		main['settings']['bpm'] *= 2 / 3
		main['actions'].append({
			"eventType": "MultiPlanet",
			"floor": start,
			"planets": 3,
		})
	else:
		accelerate(start, 2, 3, True)
	if end != length: # The goal needn't have any speed change
		accelerate(end, 3, 2)
clockwise, old_angle = True, 999 # And the real mathematics begin!
for i, angle in enumerate(main['angleData']): # Enumerate all the blocks
	if twirls.__contains__(i): # Twirls make clockwise to counterclockwise, vice versa
		clockwise = not clockwise
	if angle != 999: # 999 means a midspin
		if i > 0: # No need to convert Block 0
			if main['angleData'][i - 1] != 999: # The angles of the blocks after midspin are not as same as after normal blocks
				old_angle += 180
			delta_degree = angle - old_angle
			if clockwise: # Clockwise and counterclockwise don't share the same angle
				delta_degree = old_angle - angle
			degree = setAngle(delta_degree, True)
			old_degree = degree
			if planets[i] == -3: # Convert -3
				degree *= 2 / 3
				if main['angleData'][i - 1] != 999: # The degrees of the blocks after midspin are not as same as after normal blocks
					degree += 60
				if holds.__contains__(i): # The degrees of the blocks before hold are not as same as after normal blocks
					hold_degree = degree + holds[i]['degree'] * 2 / 3
					degree = hold_degree % 360
					main['actions'][holds[i]['index']]['duration'] = (hold_degree - degree) / 360
			last_angle = main['angleData'][i - 2]
			if main['angleData'][i - 1] != 999: # The angles of the blocks after midspin are not as same as after normal blocks
				last_angle = main['angleData'][i - 1] + 180
			delta_angle = degree + last_angle
			if clockwise: # Clockwise and counterclockwise don't share the same angle
				delta_angle = last_angle - degree
			main['angleData'][i] = setAngle(delta_angle)
		old_angle = angle
useless_actions = []
for action in main['actions']: # Delate useless MutiPlanets and SetSpeed actions
	if action['eventType'] == 'MultiPlanet' and abs(planets[action['floor']]) == abs(planets[action['floor'] - 1]) or action['eventType'] == 'SetSpeed' and action['bpmMultiplier'] == 1 and action['speedType'] == 'Multiplier': # If a MutiPlanets don't change the number of planets or a SetSpeed don't change the speed, then it‘s useless
		useless_actions.append(action)
for action in useless_actions: # Delate useless actions
	main['actions'].remove(action)
try: # File operations always have to do a LOT of error catching
	with open(output_path, 'w') as f: # Finally I could dump a JSON
		dump(main, f)
except PermissionError:
	exitWithHelp('Error: Output file permission error')
print('Converting Complete!')
