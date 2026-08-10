#encoding:utf-8
#name:mod_config.py

import configparser
import os

def getConfig(section, key):
	config = configparser.ConfigParser()
	path = 'config\\config.conf'
	config.read(path)
	return config.get(section,key)


