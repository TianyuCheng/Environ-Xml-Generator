xml-generator
=============

A xml generator pulling information from Google Spreadsheet for Project Environ

Usage
-----
  python generator.py --username=<username> [--verbose]

  python generator.py --help

Files
-----
	+ generator.py              => executable script for xml generation
	+ utils
	  - GoogleReader.py         => utility class to fetch google spreadsheet data

Dependencies
------------
	gdata==2.0.18
 
	keyring==3.8

You can use pip install to install these packages

	sudo pip install gdata

	sudo pip install keyring

Author
------
Tianyu Cheng (tianyu.cheng@utexas.edu)
