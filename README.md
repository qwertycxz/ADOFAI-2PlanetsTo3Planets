# ADOFAI-2PlanetsTo3Planets

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

A single python file that could automatically turn a 2-planets ADOFAI level to a 3-planets ADOFAI level (and more).

## Background

In the Steam Workshop, there're really a lot of levels that just turn two planets to three planets. That's not very creative and I think that these kinds of levels should be OK to convert automatically. And here we are!

### The file's goal:

Convert a 2-planets ADOFAI level to a 3-planets ADOFAI level.

## Usage

### GUI

```sh
planetamountconvert.exe
```

or

```sh
planetamountconvert.py
```

### CLI

```sh
planetamountconvert.py [-h] [<input_path> [<options>]]
```

options:

    `-h`, `--help`          show this help message and exit
    `-l`, `--length`        get the length of a lavel and exit
    `-o <path>`, `--output <path>`
                            set the output path (default: input_folder\input_file_name(3planets).adofai)
    -s [start_end_to_list], --setting [start_end_to_list]
                            the converting setting (default: '::')
    [start_end_to_list] -> [start_block]:[end_block]:[to_planets] [[start_block]:[end_block]:[to_planets] ...]
                            0 < start_block ≤ end_block ≤ length
                            to_planets > 1

example:

```sh
PlanetAmountConvert.py ./main.adofai 50:: :60:2
                        # Convert main.adofai
                        #   between Block 61 and the last block to 3 planets and
                        #   between the first block and Block 60 to 2 planets.
                        # The second option will override the first option.
```

### Python Module

```py
from planetamountconvert import Level
...
# See more hint on the note and in example.py
```

## Changelog

2023/4/17: Rewrite all scripts with OOP. Use json and argparse instead of eval and getopt. Add type hint. Optimize GUI and CLI experince.

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
