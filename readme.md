This is a small program to properly attribute portraits and sprites from the [PMD Sprite Repo](https://sprites.pmdcollab.org/#/), in accordance with the Rules and Bylaws of [Creative Commons Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/?ref=chooser-v1).

## Setup:

- Requires [Python >=3.12](https://www.python.org/downloads/)
  - You MUST check the option to "Add Python on PATH".
- Requires [Firefox](https://www.mozilla.org/en-US/firefox/)
- Requires [Gecko Driver](https://github.com/mozilla/geckodriver/releases) for Selenium, which should be placed in a folder along your PATH.
  - If you don't know what that means, put it in the same folder as your python installation, which for Windows, defaults to `%localappdata%\Programs\Python\Python312`.
- Then download these files on your computer and put them somewhere convenient.
- Either double-click `setup.bat`, or in a terminal window run the command `py -m pip install selenium`.

## Usage:
Create, in the same folder as the program, a text file called `input.txt`.  
In `input.txt`, add the National Dex numbers of each Pokémon you wish to have attributed from the [PMD Sprite Repo](https://sprites.pmdcollab.org/#/).  
If you want to have attributed a form for a Pokémon that is not "Normal", add the form's NAME on the same line as the Natdex number, after a comma.

Leading zeros do not matter in the Natdex number, nor does capitalization matter for the form name.

**Input Example 1:**  
I want the attributions for Beedrill, thus my `input.txt` would have:
```
15
```
**Input Example 2:**  
I want the attributions for Starter Shiny Machop, and Female Sneasel. My `input.txt` would have:
```
066,starter shiny
0215, Female
```

Double-click the file `main.py` to run it, or enter the command `py .\main.py` in a terminal window opened to the folder holding the program.  
Wait for it to complete and for the terminal window to close on its own. Do not close the terminal window yourself. Afterwards, fully-qualified attributions for each portrait and sprite of the Pokémon you listed will be in the file `output.txt` in the folder holding the program.

## Troubleshooting:
This hasn't been exhastively tested, and I wrote it over something like 8 hours while mildly sleep deprived. It might break.