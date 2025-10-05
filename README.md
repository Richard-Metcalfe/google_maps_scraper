# Web Scraper for Google Maps

## Requirements
* Python installation 3.10 or greater
* Pip version equivalent to the your python version = package installation.

## Python packages used
* **argparse**: this module provides a way to handle command-line arguments, making it easier to write scripts that can accept user input directly from the command line. 
* **playwright**: a tool for automating web browsers. Developed by Microsoft, it is designed to be reliable, fast, and capable of handling modern web applications that use dynamic webpages.
* **dataclasses**: this module provides a decorator and functions for automatically adding special methods to user-defined classes. 
* **pandas**: open-source library in Python for data manipulation and analysis. Provides data structures and functions needed to work on structured data. Well-suited for handling tabular data, such as data stored in spreadsheets or databases.
* **alive-progress**: Progress Bar updates for long running operations
* **scrapy**: package for scraping static webpages. Enable crwaling of web domains to search for data. Does not handle dynamic pages well. 

## Usage 
After installing Python it's easiest to create a virtual environment. E.g. for python version 3.13, or whichever version you are using.

**N.B.** This program is currently hardcoded to scape  [www.google.com/maps](https://www.google.com/maps) - other websites will require further work. It is necessary to manually accept cookies after the browser opens. 

## Steps ##
**N.B.** After initial setup you only need to perform steps 3 and 7 to run the run the scraper.

### 1. Open a terminal change directory to the project root

> cd {_your-projects-dir_}/google_maps_scraper

### 2. Create a virtual environment

> python -m venv venv_3-13

### 3. Start the virtual Environment

**Windows:**

> .\venv_3-13\Scripts\Activate.ps1

***nix** (Including MacOS Darwin) 

> source venv_3-13/bin/activate

### 4. Install the requirements
The packages required to run the program are recorded in the file **_requirements.txt_**. This allows easy creation of a virtual execution environment for the program.

To install the required packages to the virtual environment run

> pip install -r requirements.txt

### 5. Install the playwright drivers

> playwright install

### 6. Run the help function to see details of the command line arguments

**Windows**

>  python .\main.py --help

***nix**

> python main.py --help

### 7. Run the program with your category and location

**Windows**

>  python .\main.py --category "Roofers" --location "Manchester" --number 10

***nix**

> python main.py --category "Roofers" --location "Manchester" --number 10

## Searching for email addresses by domain
The google maps webscraper retrieves the company domain that hosts the company website. The email scraper attempts to retrieve email addresses from pages within that domain using a web spider and parsing the static content of the webpages. This won't find email addresses in dymamically created webpages that retrieve data from another source. 

The standalone email scraper with read data from a CSV file specified on the command line - one that was created from a previous google maps scrape. It will then iterate over rows and if a web-domain is present for that entry it will attempt to crawl the web-domain for email addresses, if found it will store then in another file with the suffix _**_with_emails**_. 
For large data set or web-domains with a lot of pages, this will take a while and might not find anything. 

    The command

> python .\email_scraper.py --file "Roofers_in_Manchester_google_maps.csv"

    will create a new CSV file with the name Roofers_in_Manchester_google_maps_with_emails.csv