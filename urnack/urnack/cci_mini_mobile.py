# cci_mini_mobile.py     william k. johnson 2016

import os
import argparse
import logging
import abc

log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'

# ------------------------------------------------------------------------
def init_logging( moniker = 'current_app' , fmt = log_format ) :

		"""
		initialize application logging
		:param logger:
		:param moniker:
		:param fmt:
		:return logger :
		"""

		logger = logging.getLogger( moniker )

		# setup logging

		# create logger
		logger.setLevel( logging.DEBUG )
		# create file handler strange file extension
		# tells python logging module to overwrite file
		fh = logging.FileHandler( moniker + '.log' + '-debug.log', mode = 'w')
		fh.setLevel( logging.DEBUG )

		# create console handler
		ch = logging.StreamHandler()
		ch.setLevel( logging.DEBUG )

		# create formatter and add it to the handlersuntitled
		formatter = logging.Formatter( fmt )
		fh.setFormatter( formatter )
		ch.setFormatter( formatter )

		# add the handlers to the self._logger
		logger.addHandler( fh )
		logger.addHandler( ch )

		return logger


# ------------------------------------------------------------------------
class cci_mobile( object )  :
			"""
			minimal utility class exposing
			"""

			__metaclass__ = abc.ABCMeta

			'''object model'''
			def __init__( self  ) :

				# logging
				self._logger = init_logging( self.__class__.__name__  )
				self._logger.info( self.__class__.__name__ + '...'  )

				# command line
				self._args_parser = argparse.ArgumentParser( description= self.__class__.__name__   + ' william k. johnson 2015 ' ,
										  epilog='...minimal utilities...')
				self._args_parser._optionals.title = 'flag arguments'



			'''attributes'''
			@property
			def args_parser( self ) :
				return self._args_parser
			@args_parser.setter
			def args_parser( self , args ) :
				self._args_parser = args



			'''services'''
			@abc.abstractmethod
			def connect( self ) :
				"""
				connect queue
				"""

				pass


