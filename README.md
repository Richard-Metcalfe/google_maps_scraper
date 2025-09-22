# Web Scraper for Google Maps

## Requirements
* Python installation 3.10 or greater
* Pip - to install packages.

## Python packages used
* argparse: The argparse module provides a way to handle command-line arguments, making it easier to write scripts that can accept user input directly from the command line. 
* playwright:Playwright is a tool for automating web browsers. Developed by Microsoft, it is designed to be reliable, fast, and capable of handling modern web applications.
* dataclasses: This module provides a decorator and functions for automatically adding special methods to user-defined classes. 
* pandas: Widely-used open-source library in Python for data manipulation and analysis. It provides data structures and functions needed to work on structured data seamlessly. Pandas is well-suited for handling tabular data, such as data stored in spreadsheets or databases.
* alive-progress: Progress Bar updates for long running operations

## Usage 
After installing Python it's easiest to create a virtual environment. E.g. for python version 3.13.

**N.B.** This program is currently hardcoded to scape [https://www.google.com/maps] - other websites will require further work. It is necessary to manually accept cookies after the browser opens. 

### Steps ###

1. Create a virtual environment

> python -m venv venv_3-13

The packages required to run the program are recorded in the file **_requirements.txt_**. This allows easy creation of a virtual execution environment for the program.

2. Install the requirements

To install the required packages to the virtual environment run
> pip install -r requirements.txt

3. Start the virtual Environment open a terminal and run

**Windows:**
> .\venv_3-13\Scripts\Activate.ps1

***nix**
> .\venv_3-13\Scripts\activate

4. Install the playwright drivers

> playwright install

5. Run the help function to see details of the command line arguments

>  python .\main.py --help

6. Run the program with your category and location

>  python .\main.py --category "Roofers" --location "Manchester" --number 10