xml-generator
=============

A xml generator pulling information from Google Spreadsheet for personal usage

Files
-----
├── LICENSE
├── README.md
├── XML_Prototype              => folder containing the prototype xml
│   ├── bases.xml
│   ├── costs.xml
│   ├── effects.xml
│   ├── events.xml
│   ├── prereq_conditions.xml
│   ├── probabilities.xml
│   ├── range_conditions.xml
│   ├── regions.xml
│   └── upgrades.xml
├── duplicates_checker.py     => executable script for xml duplicate checking
├── generator.py              => executable script for xml generation
├── utils                     => folder containing xml and google reader library
│   ├── Check_XML.py
│   ├── Check_XML.pyc
│   ├── Generate_XML.py
│   ├── Generate_XML.pyc
│   ├── GoogleReader.py
│   └── GoogleReader.pyc
└── xmls                      => destination folder for generated xml files
    ├── bases.xml
    ├── costs.xml
    ├── effects.xml
    ├── events.xml
    ├── prereq_conditions.xml
    ├── probabilities.xml
    ├── range_conditions.xml
    ├── regions.xml
    └── upgrades.xml

Usage
-----
1. python generator.py [gmail account name | OPTIONAL] to generate xmls
2. python duplicates_checker [gmail account name | OPTIONAL] to check duplicates
