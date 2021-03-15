# VNSTATGUI
A GUI interface for vnstat written in python 3 that exports data from vnstat as json and display's it in the GUI.


# Table of Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)


# Introduction


The idea to create this came to mind when I wanted to monitor network usage on my hotspot that has limited bandwith and I couldn't find a current working GUI for vnstat.

# Requirements

* vnstat
* python 3
* matplotlib
* pandas
* PyQt5

# Installation

Start off by cloning:
```
$ git clone https://github.com/heydok/vnstatgui.git
$ cd vnstatgui
$ pip3 install -r requirements.txt
```

# Usage

Run vnstatgui:

```
$ ./vnstatgui.py

or

$ python3 vnstatgui.py
```

This opens a new gui where you can select the data you want to view per interface and date range.


# License

vnstatgui is licensed under the GNU GENERAL PUBLIC LICENSE.

Copyright (c) Heydok.
