# kc_thread_manager.py   willian l. johnson 2016


# python standard
import os
import copy
import logging
import importlib
from time import gmtime, strftime , sleep
import subprocess as proc
import threading



# -----------------------------------------------------------------------------------
class kc_thread_manager( object ) :

			"""
			kc_thread_manager
			"""

			def __init__( self ,
						  logger = None  ,
						  thread_pool = False ,
						  workers = 0 ) :

				"""

				:param logger :
				:return:
				"""

				if logger is None :
					raise Exception( 'no logging instance specified...' )
				self._logger = logger
				self._logger.info( '...thread manager initialized...' )

				# thread dictionary
				self._thread_dict = dict()
				#log serializer - re-entrant lock
				self._log_lock = threading.RLock()


			def __del__( self ) :
				"""
				thread barrier

				:return:
				"""
				pass


			@property
			def log( self ) :
				return self._logger
			@log.setter
			def log( self , lg ) :
				self._logger = lg
			@property
			def thrds( self ) :
				return self._thread_dict
			@thrds.setter
			def thrds( self  , t ) :
				self._thread_dict = t
			@property
			def rlk( self ) :
				return self._log_lock
			@rlk.setter
			def rlk( self , lk  ) :
				self._log_lock = lk





