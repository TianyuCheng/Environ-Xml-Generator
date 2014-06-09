xml-generator
=============

A xml generator pulling information from Google Spreadsheet for internal usage

Usage
-----
1. python generator.py [gmail account name | OPTIONAL] to generate xmls
2. python duplicates_checker [gmail account name | OPTIONAL] to check duplicates
<hr>

Files
-----
+ duplicates_checker.py     => executable script for xml duplicate checking
+ generator.py              => executable script for xml generation
+ utils                     => folder containing xml and google reader library
	- Check_XML.py
	- Generate_XML.py
	- GoogleReader.py
<hr>

Dependencies
------------
gdata==2.0.18

keyring==3.8

You can use pip install to install these packages

sudo pip install gdata

sudo pip install keyring
<hr>

Author
------
Tianyu Cheng (tianyu.cheng@utexas.edu)
