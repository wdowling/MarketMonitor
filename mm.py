#!/usr/bin/env python
""" mm.py - MarketMonitor polls the Yahoo Finance API for latest index data.

	Using the list of S&P 500 companies from http://data.okfn.org/data/core/s-and-p-500-companies,
    marketmonitor polls the Yahoo Finance API once a minute for the latest pricing information.
    Between 09:30AM and 16:00PM EST the program will run pulling this information. Before markets
    open it will pull the last price on closing.
"""
import logging
import sys
from time import sleep
from yahoo_finance import Share
from requests.exceptions import ConnectionError

__author__ = "William Dowling"
__copyright__ = "Copyright 2015 William Dowling (wmdowling@gmail.com)"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "William Dowling"
__email__ = "wmdowling@gmail.com"

# Initialize logging
logging.basicConfig(filename='/var/log/marketmonitor.log', level=logging.DEBUG)

def monitor(symbols):
	'''
	Pull the following information from each symbol:
		get_price()
		get_open()
		get_prev_close()
		get_change()
	'''
	logging.debug('Symbol | Datetime | Close Price | Open | Current | Change | Volume | Exchange')
	try:
		while(True):
			for symbol in symbols:
				try:
					yh = Share(symbol)
					logging.debug(symbol + ' | ' + str(yh.get_trade_datetime()) + ' | ' + str(yh.get_prev_close()) + ' | ' + str(yh.get_open()) + ' | ' + str(yh.get_price()) + ' | ' + str(yh.get_change()) + ' | ' + str(yh.get_volume()) + ' | ' + str(yh.get_stock_exchange()))
					sleep(5)
				except ConnectionError as e:
					logging.debug(e)
					logging.debug('No response from Yahoo Finance API. Trying again...')

			yh.refresh
	except KeyboardInterrupt:
		print 'Quitting Market Monitor....'
		sys.exit()

def loadSymbols():
	'''
	Load S&P500 symbols from CSV file
	'''
	symbols = []
	try:
		f = open('constituents.csv')
		for line in f:
			symbols.append(line.split(',')[0])
	finally:
		f.close()

	monitor(symbols)

if __name__ == '__main__':
	print 'Initializing Market Monitor...'
	loadSymbols()
