from json import dump
from os.path import splitext
from sys import argv
clockwise = True
def setAngle(angle, hairpin = False):
	if angle < -360 or angle == -360 and hairpin:
		angle += 720
	elif angle < 0 or angle == 0 and hairpin:
		angle += 360
	elif angle > 360:
		angle -= 360
	return angle
with open(argv[1], encoding='utf-8-sig') as f:
	true = True
	false = False
	main = eval(f.read().replace(']\n', '],').replace('\n', '').replace(',,', ','))
if main.__contains__('pathData'):
	main['angleData'] = []
	pathData = main.pop('pathData')
	for c in pathData:
		if c == 'R':
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
main['settings']['bpm'] *= 2 / 3
old_angle = 999
twirls = {}
for i, action in enumerate(main['actions']):
	if action['eventType'] == 'Twirl':
		twirls[action['floor']] = True
	elif action.__contains__('beatsPerMinute'):
		main['actions'][i]['beatsPerMinute'] *= 2 / 3
main['actions'].append({
	"eventType": "MultiPlanet",
	"floor": 1,
	"planets": 3,
})
for i, angle in enumerate(main['angleData']):
	if twirls.__contains__(i):
		clockwise = not clockwise
	if angle != 999:
		if i > 0:
			if main['angleData'][i - 1] != 999:
				old_angle += 180
			delta_degree = angle - old_angle
			if clockwise:
				delta_degree = old_angle - angle
			degree = setAngle(delta_degree, True)
			old_degree = degree
			degree *= 2 / 3
			if main['angleData'][i - 1] != 999:
				degree += 60
			last_angle = main['angleData'][i - 2]
			if main['angleData'][i - 1] != 999:
				last_angle = main['angleData'][i - 1] + 180
			delta_angle = degree + last_angle
			if clockwise:
				delta_angle = last_angle - degree
			main['angleData'][i] = setAngle(delta_angle)
		old_angle = angle
output_direction = splitext(argv[1])
with open(output_direction[0] + '(3Planets)' + output_direction[1], 'w') as f:
	dump(main, f)