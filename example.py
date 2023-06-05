#! /usr/bin/env python
from planetamountconvert import Level


'''Example 1:
Change planet amount for every 100 block
Get the input and output path from command line
'''

from json import dump

level = Level()
path = input()
level.loadMainFromPath(path)
print(len(level)) # Use len() to get the length of the level

level.loadLevelFromMain()
print(level.length) # After loadLevelFromMain(), level.length stored the length of the level

end = level.length // 100 # Intermediate variable
for i in range(1, end):
	start = i * 100 # Intermediate variable
	level.setPlanets(start + 1, start + 100, i % 2 + 2)
level.setPlanets(end * 100, level.length, end % 2 + 2)
# Every 100 block, change the planet amount

level.convertByPlanets() # Let's go!

main = level.dumpMain() # If no arguments, dumpMain == getMain

with open(input(), 'w') as f:
	dump(main, f)


'''Example 2:
Change planet amount each time changing speed
Get the input and output path from tkinter
'''
from planetamountconvert import formatLevelString, Level
from tkinter.filedialog import askopenfilename, asksaveasfile

level_string = ''
with open(askopenfilename(), encoding = 'utf-8-sig') as f: # Watch out the encoding
	level_string = formatLevelString(f.read())
level = Level().loadMainFromString(level_string).loadLevelFromMain() # Chained calls support

last_set_speed = 0
accelerates = level.getActions('SetSpeed') # Get all actions that 'eventType': 'SetSpeed'

for i in sorted(accelerates): # Key of this dict is block number
	if last_set_speed != 0:
		level.setPlanets(last_set_speed, i - 1, 3) # Left closed right open
		last_set_speed = 0
	else:
		last_set_speed = i
if last_set_speed != 0:
	level.setPlanets(last_set_speed, level.length - 1, 3)

with asksaveasfile() as f:
	level.convertByPlanets().dumpMain(f)


'''Example 3:
Add a planet wherever speed up and remove a planet wherever speed down
Get the input and output path from pathlib.Path

Warning: the level converted by the example down below cannot be played
More than 3 planets are not available in game.
'''
from planetamountconvert import Level
from pathlib import Path

directory:Path
cycle:bool
crazy:bool

from anotherfile import directory, cycle, crazy

for i in directory.iterdir(): # For every directory in the given directory
	speeds = {}
	level = Level().loadMainFromPath(i / 'main.adofai').loadLevelFromMain() # i / 'main.adofai' is pathlib.Path

	accelerates = level.getActions('SetSpeed')
	bpm = level.main['settings']['bpm']

	for j in sorted(accelerates):
		if accelerates[j]['speedType'] == 'Bpm':
			if accelerates[j]['beatsPerMinute'] > bpm:
				speeds[j] = 1
			elif accelerates[j]['beatsPerMinute'] < bpm:
				speeds[j] = -1
			bpm = accelerates[j]['beatsPerMinute']
			continue

		if accelerates[j]['bpmMultiplier'] > 1:
			speeds[j] = 1
		elif accelerates[j]['bpmMultiplier'] < 1:
			speeds[j] = -1
		bpm *= accelerates[j]['bpmMultiplier']

	planet = 2
	last_set_speed = 0

	for j in speeds:
		if last_set_speed != 0:
			planet += speeds[last_set_speed]
			planet = 2 if planet < 2 or planet > 8 and cycle else planet
			planet = 8 if planet > 8 and not crazy or planet < 2 and cycle else planet
			level.setPlanets(last_set_speed, j - 1, planet)
		last_set_speed = j
	if last_set_speed != 0:
		planet += speeds[last_set_speed]
		planet = 2 if planet < 2 or planet > 8 and cycle else planet
		planet = 8 if planet > 8 and not crazy or planet < 2 and cycle else planet
		level.setPlanets(last_set_speed, level.length - 1, planet)

	with (i / 'main(StrangePlanets).adofai').open('w') as f:
		level.convertByPlanets().dumpMain(f)