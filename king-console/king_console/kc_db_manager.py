# kc_dbmanager.py william k. johnson 2016


import os
import sys
#############
import copy
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
##############
import logging
import argparse
import socket
import fcntl
import struct
import subprocess as proc
import urllib2
import requests
import sqlite3
import uuid
import threading

from kivy.app import App



log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'

sql_cursor_dictionary = {  'sd_insert_session' : 'insert into sessions  (session_name ,'
												 'session_user ,'
												 'context ,'
												 'session_moniker ,'
												 'device_id) '
												 'values ( %s , %s , %s , %s , %s )' ,
							'sd_insert_session_call' :   'insert into session_call_history'
														 '  (session_name ,'
														 'call_segment ,'
														 'call_moniker ,'
														 'call_params , '
														 'payload) '
														 'values ( %s , %s , %s , %s , %s )' ,
							'sd_insert_payload' : 		 'insert into session_payload_atoms ( payload ,'
														 'size , '
														 'cache_pending) '
							                             'values ( %s , %d , %d )' ,
							'sd_insert_session_note' : 	 'insert into session_notes ( session_name ,'
														 'snippet , '
														 'metatag) '
							                             'values ( %s , %s , %s )' ,
							'sd_update_session_status_closed' : 'update sessions set status = 0 '
														 		'where session_name = %s' ,
							'sd_update_session_status_open' :   'update sessions set status = 1 '
														 		'where session_name = %s'  ,
							'sql_retrieve_call_history' : 	'select * from session_call_history '
															'where session_name = %s '
															'order by timestamp DESC '
													        'LIMIT 15' ,
							'sql_retrieve_document_policy' : 'select * from payload_policy '
														    'where moniker = %s '
															'and provider_type = %s '
															'and active = 1',
							'sql_retrieve_one_config_atom' : 'select map from metadata_config '
															 'where moniker = %s '
						}
# -----------------------------------------------------------------------------------
def dict_factory( cursor, row)  :
    d = {}
    for idx , col in enumerate( cursor . description ) :
        d[col[0]] = row[idx]
    return d



# -----------------------------------------------------------------------------------
def quoted( s ) :
	return '"' +  s  + '"'



# -----------------------------------------------------------------------------------
def quoted_list_to_tuple( lst ) :
	return tuple( [quoted( x ) for x in lst] )




# -----------------------------------------------------------------------------------
class kc_db_manager( object ) :

				"""
				kc_db_manager
				"""

				def __init__( self ,
							  default_db ,
							  logger = None )  :

					"""

					:param default_db:
					:param logger:
					:return:
					"""


					if logger is None :
						raise Exception( 'no logging instance specified...' )
					self.logger = logger
					self.logger.info( '...db manager initialized...' )

					# default db
					try :
						self._current_db = sqlite3.connect( default_db  )
					except sqlite3.DatabaseError as e :
						self.logger.error( e.message )
				    # cursor
					self._db_cursor = self._current_db.cursor()
					self.uid = None
					self._db_rlk = threading.RLock()

					self._call_map = {
									   'insert_session' : self.insert_session ,
									   'insert_session_call' : self.insert_session_call ,
									   'insert_payload' : self.insert_payload ,
									   'insert_session_note' : self.insert_session_note ,
									   'update_session_status' : self.update_session_status
									 }
					self._query_call_map =  {
											   'query_call_history' :  self.query_call_history ,
											   'query_document_policy' : self.query_document_policy ,
											   'retrieve_config_atom' : self.retrieve_config_atom
									 		}


				def __del__( self ) :
					"""

					:return:
					"""

					if self._current_db :
						self.logger.info( '...db manager uninitialized...' )
						self._current_db.close()




				def _execute_sql_update( self , sql_key , params  , raw = False ) :
					"""

					:param sql_key:
					:param args:
					:param kargs:
					:return:
					"""

					try :

							s = sql_cursor_dictionary[sql_key]
							if not raw :
								# params is a string list
								s = s % quoted_list_to_tuple( params )
							else :
								# params is a tuple
								s = s % params

							self._db_cursor.execute( s )
							self.db.commit()

							self.logger.info( '...' +  sql_key  + ' executed...' )

					except sqlite3.IntegrityError as e :
						self.logger.error( 'integrity error in update statement '
							+ e.message )
					except sqlite3.OperationalError as e :
						self.logger.error( 'statement failed: '
							+ e.message )
					except TypeError as e :
						self.logger.error( e.message )
						



				def _execute_sql_result_set( self , sql_key , params , event , queue_id ) :
					"""

					:param sql_key:
					:param params:
					:param event:
					:return:
					"""

					q = App.get_running_app().dbpq
					rf = self._current_db.row_factory

					if not event.isSet() :
						try :

							s = sql_cursor_dictionary[sql_key]
							s = s % quoted_list_to_tuple( params )

							rs = ( None , None )
							payload = list()
							self._db_cursor.execute( s )
							while True :
								rs = self._db_cursor.fetchone()
								if rs is None :
									break
								payload.append( rs )

							App.get_running_app().dbpq_lk.acquire()
							q.put( payload )
							self.logger.info( '...' +  sql_key  + ' executed...'  + str( params ) )
							event.set()

						except sqlite3.OperationalError as e :
							self.logger.error( 'statement failed: '
								+ e.message )
						except TypeError as e :
							self.logger.error( '...not enough aruments for db query...' )
						finally :
							App.get_running_app().dbpq_lk.release()





				def execute_naked_sql_result_set( self ,
												   sql_statement ,
												   params ) :
					"""

					:param sql_statement:
					:param params:
					:return:
					"""

					payload = list()
					try :

						s = sql_statement
						s = s % quoted_list_to_tuple( params )

						rs = ( None , None )

						self._current_db.row_factory = dict_factory
						cursor = self._current_db.cursor()
						cursor.execute( s )
						while True :
							rs = cursor.fetchone()
							if rs is None :
								break
							payload.append( rs )

						self.logger.info( '...' +  sql_statement  + ' executed...'  + str( params ) )

					except sqlite3.OperationalError as e :
						self.logger.error( 'statement failed: '
							+ e.message )
					except TypeError as e :
						self.logger.error( '...not enough aruments for db query...' )

					return payload




				def insert_session( self ,	params ) :
					"""

					:param uid:
					:param user
					:param level:
					:param moniker:
					:param device:
					:return session uid:
					"""

					self._execute_sql_update( 'sd_insert_session' , params )

					self.uid = params[0]




				def insert_session_call( self , call_params ) :
					"""

					:param session_id:
					:param segment:
					:param function:
					:param params:
					:payload( to be stubbed on insert )
					:return:
					"""


					self._execute_sql_update( 'sd_insert_session_call' , call_params )





				def insert_payload( self , call_params ) :
					"""

					:param payload:
					:param size:
					:param cache_pending:
					:return:None
					"""

					params = ( '"' + call_params[0] + '"'  ,
							   int( call_params[1] ) ,
							   int( call_params[2] ) )
					self._execute_sql_update( 'sd_insert_payload' , params , raw = True  )




				def insert_session_note( self , call_params ) :
					"""

					:param session_id:
					:param snippet:
					:param comment:

					:return:
					"""


					self._execute_sql_update( 'sd_insert_session_note' , call_params   )




				def update_session_status( self , call_params ) :
					"""

					:param call_params:
					:return:
					"""

					if call_params[0] == 0 :
						call_params.remove( 0 )
						self._execute_sql_update( 'sd_update_session_status_closed' , call_params )
					else :
						call_params.remove( 1 )
						self._execute_sql_update( 'sd_update_session_status_open' , call_params )




				def query_call_history( self , call_params ) :
						"""

						:param call_params:
						:return:
						"""

						# wait trigger
						event = call_params[0]
						id = call_params[1]
						call_params.remove( event )
						call_params.remove( id )


						self._execute_sql_result_set( 'sql_retrieve_call_history' ,
													  call_params ,
													  event ,
													  id )




				def query_document_policy( self , call_params ) :
						"""

						:param call_params:
						:return:
						"""

						# wait trigger
						event = call_params[0]
						id = call_params[1]
						call_params.remove( event )
						call_params.remove( id )


						self._execute_sql_result_set( 'sql_retrieve_document_policy' ,
													  call_params ,
													  event ,
													  id  )




				# ----------------------------------------------------------------------------------------------------
				def retrieve_config_atom( self , call_params ) :
						"""

						:param params:
						:return:
						"""

						# wait trigger
						event = call_params[0]
						id = call_params[1]
						call_params.remove( event )
						call_params.remove( id )


						self._execute_sql_result_set( 'sql_retrieve_one_config_atom' ,
													  call_params ,
													  event ,
													  id )





				@property
				def log( self ) :
					return self.logger
				@log.setter
				def log( self , lg ) :
					self.logger = lg
				@property
				def db( self ) :
					return self._current_db
				@db.setter
				def db( self  , daba ) :
					self._current_db = data
				@property
				def cursor(  self ) :
					return self._db_cursor
				@cursor.setter
				def cursor( self  , cur ) :
					self._db_cursor = cur
				@property
				def db_lk( self ) :
					return self._db_rlk
				@db_lk.setter
				def db_lk( self , lk ) :
					self._db_rlk = lk





# --------------------------------------------------------------------------------------------------------------
if __name__ == '__main__' :

				# logger
				logger = logging.getLogger( "kc_db_manager" )
				logger.setLevel( logging.DEBUG )
				ch = logging.StreamHandler()
				ch.setLevel( logging.DEBUG )
				formatter = logging.Formatter( log_format )
				ch.setFormatter(formatter)
				logger.addHandler(ch)
				logger.info( '...kc_db..manager...' )


				kcdb = kc_db_manager( '../king_console.sqlite'  , logger )
				params = [str( uuid.uuid4() )  , 'wiljoh' , 'level1' , 'latenight review' ,  local_mac_addr() ]

