#!/usr/bin/env python
""" mm.py - MarketMonitor polls the Yahoo Finance API for latest index data.

	Using the list of S&P 500 companies from http://data.okfn.org/data/core/s-and-p-500-companies,
    marketmonitor polls the Yahoo Finance API once a minute for the latest pricing information.
    Between 09:30AM and 16:00PM EST the program will run pulling this information. Before markets
    open it will pull the last price on closing.
"""
import logging
import mysql.connector
import sys
import multiprocessing as mp
import mysql.connector
from mysql import connector
from mysql.connector import errorcode
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

def insertSymbol(yh, symbol):
	try:
		conn = mysql.connector.connect(user='mm', password='ds87gfsjha9llnb', \
host='127.0.0.1', database='markets')
		cursor = conn.cursor()
		add_share_data = ("INSERT INTO sp500 "
						"(trade_date, symbol, close_price, open_price, current_price, price_change, volume, exchange) "
						"VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ")
		share_data = (yh.get_trade_datetime(), symbol, yh.get_prev_close(), yh.get_open(), yh.get_price(), yh.get_change(), yh.get_volume(), yh.get_stock_exchange())
		cursor.execute(add_share_data, share_data)
		conn.commit()
		cursor.close()
		conn.close()
		
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			print "Username or password incorrect!"
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			print "Database does not exist!"
		else:
			print err
	else:
		conn.close()
		logging.debug('Disconnected')
		return False

	return conn

def monitor(symbol):
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
			try:
				yh = Share(symbol)
				res = insertSymbol(yh, symbol)
				sleep(5)
			except ConnectionError as e:
				logging.debug(e)
				logging.debug('No response from Yahoo Finance API. Trying again...')

			yh.refresh
	except KeyboardInterrupt as e:
		logging.debug(e)
		return

def loadSymbols():
	'''
	Load S&P500 symbols from CSV file
	'''
	symbols = []
	try:
		f = open('/home/wmd/projects/marketmonitor/sp500.csv')
		for line in f:
			symbols.append(line.split(',')[0])
	finally:
		f.close()

	# Kick off parallel processing of symbols. For now we stick to
    # 10 jobs conccurrently. Also the signal catching needs to be revised
	# as it does not exit gracefully.
	try:
		p = mp.Pool(processes=10)
		p.map(monitor, symbols)
	except KeyboardInterrupt as e:
		print 'Quitting Market Monitor....'
		logging.debug(e)
		p.close()
		sys.exit()

if __name__ == '__main__':
	print 'Initializing Market Monitor...'
	loadSymbols()
