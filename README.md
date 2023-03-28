# ADOFAI-2PlanetsTo3Planets

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

A single python file that could automatically turn a 2-planets ADOFAI level to a 3-planets ADOFAI level.

## Background

In the Steam Workshop, there're really a lot of levels that just turn two planets to three planets. That's not very creative and I think that these kinds of levels should be OK to convert automatically. And here we are!

The file's goal:

  Convert a 2-planets ADOFAI level to a 3-planets ADOFAI level.

## Usage

### GUI mode

2PlanetsTo3Planets.exe

or

python 2PlanetsTo3Planets.py

### CLI mode

python 2PlanetsTo3Planets.py [<input_path> [options]]

General Options:
  -f <number> Set the from-planet amount. Default 2
  -t <number> Set the to-planet amount. Default 3
  -s <number> Set the start of converting. Default the first block(-s 1).
  -e <number> Set the end of converting. Default the last block.
  -o <path>   Set the output path.
  -m          Multiple input mode. Ingore -s or -e options.

<./main.adofai> means a path to a .adofai file which should be an ADOFAI level.

## Changelog

2022/3/28: Fix a bug about float.

2022/9/7:  Combine 2planetsto3planets.py and GUI.py. Fix 1 bug: Hold converting is not correct. 1 New feature: Convert camera and track moves now!

2022/8/2:  Add a whole new panel that you can choose from-planet amount and to-planet amount.

2022/7/28: Fix that the degree isn't correct when a hold is less than 60°. 

2022/7/26: Add a GUI version. 

2022/7/18: Add several options and their help. Converting 3 planets to 3 planets now gives warning. 

2022/7/14: Add support for holds which more than 1 lap.

## Contributor

[@qwertycxz](https://github.com/qwertycxz)

## How could I contribute?

[Issue](https://github.com/qwertycxz/ADOFAI-2PlanetsTo3Planets/issues/new) and Pull-requests is both welcomed.

Please notice that [Contributor Covenant](http://contributor-covenant.org/version/1/3/0/) should be follow.

## License

[Apache 2.0](LICENSE) © qwertycxz
