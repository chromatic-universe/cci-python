# tr_sqlite.py    william k. johnson 2016


import os
import sys
from StringIO import StringIO
import logging
from math import ceil

import subprocess as proc
import sqlite3
import time
import signal
import Queue
import requests
import datetime
import base64
import json


import flask
from flask import Flask , request , send_file , render_template , url_for
from flask import redirect , Response , current_app , jsonify , Blueprint
from flask_pymongo import PyMongo
from flask_restful import Resource, Api

try:  # python 2
    from urllib import urlencode
except ImportError:  # python 3
    from urllib.parse import urlencode


from application import app , _logger

default_db = None

# cci
import tr_utils


# -----------------------------------------------------------------------------
def query_session() :
			_logger.info( '...query_session...' )
			id=request.form['session_id']

			return redirect( url_for( 'session_call_history' ,
									  device = '"' + tr_utils.local_mac_addr() + '"' ,
									  session_id = '"' + id + '"' ) )

app.add_url_rule( '/query_session/' ,
				  'query_session' ,
				  view_func=query_session ,
				  methods=['GET' , 'POST'] )




# ----------------------------------------------------------------------------------------------------
def session_call_reprise(  session_id , max_id , total_count , record_ptr )  :
			"""

			:param session_id:
			:param record_ptr:
			:return:
			"""
			_logger.info( '...session_call_reprise...' )
			con = sqlite3.connect( "/data/media/com.chromaticuniverse.cci_trinity/king_console.sqlite" )
			con.row_factory = sqlite3.Row

			cur = con.cursor()
			cur.execute( "select * from session_call_history where session_name = %s" \
				         " and idx < %d " \
						 "order by timestamp DESC " \
						 "LIMIT %d" % ( session_id , int(max_id) - 15 , 15 ) )
			rows = cur.fetchall()

			return render_template( "list.html",
									rows = rows ,
									session_id = session_id ,
									total_count = total_count ,
									record_ptr = int( record_ptr ) + 15 ,
									max_id = int(max_id) - 15 )

app.add_url_rule( '/session_call_reprise/<session_id>/batch/<max_id>:<total_count>:<record_ptr>' ,
				  'session_call_reprise' ,
				  view_func=session_call_reprise ,
				  methods=['GET'] )





# ----------------------------------------------------------------------------------------------------
def session_call_history(  device , session_id )  :
			   """

			  :return:

			   """

			   _logger.info( '...aession_call_history...' )
			   con = sqlite3.connect( "/data/media/com.chromaticuniverse.cci_trinity/king_console.sqlite" )
			   con.row_factory = sqlite3.Row

			   cur = con.cursor()
			   if session_id is not None :
					cur.execute( 'select count(*) as count , max( session_call_history.idx ) as ' \
								 'max_idx  from sessions  session_call_history '
								 'inner join  sessions on session_call_history.session_name = sessions.session_name '
								 'where sessions.session_name = %s and sessions.device_id = %s'	 % ( session_id , device ) )
					rows = cur.fetchone()
					if rows is not None :
						count = rows[0]
						max_idx = rows[1]
						cur.execute( 'select * from session_call_history  ' \
									 'inner join  sessions on session_call_history.session_name = sessions.session_name '
									 'where sessions.session_name = %s and sessions.device_id = %s ' \
									 'order by session_call_history.timestamp DESC ' \
									 'LIMIT %d' % ( session_id , device , 15 ) )


						rows = cur.fetchall()
						return render_template( "list.html" ,
											rows = rows ,
											session_id = session_id ,
											total_count = count ,
											record_ptr = len( rows ) ,
											max_id = max_idx )

			   else :
					# grab newest session marked as active
					cur.execute( 	'select  max(session_call_history.idx)  as max_id  , session_call_history.session_name ' \
									'from session_call_history ' \
									'inner join  sessions on session_call_history.session_name = sessions.session_name ' \
									'where sessions.status = 1 and sessions.device_id = %s ' \
									'group by session_call_history.session_name ' \
									'order by session_call_history.timestamp desc ' \
									'limit 1'  % device )

					rows = cur.fetchone()
					if rows is not None :
						max_idx = rows[0]
						session_id = rows[1]

						cur.execute(   'select session_call_history.idx  , session_call_history.session_name ,' \
									   'session_call_history.call_segment , ' \
									   'session_call_history.call_moniker , session_call_history.call_params , ' \
									   'session_call_history.timestamp , sessions.device_id from session_call_history '\
									   'inner join  sessions on session_call_history.session_name = sessions.session_name ' \
									   'where session_call_history.session_name = "%s" '  \
									   'order by session_call_history.timestamp desc '  % session_id )

						rows = cur.fetchall()
						return render_template( "list.html" ,
												rows = rows ,
												session_id = '"' + session_id + '"' ,
												total_count = len( rows ) ,
												record_ptr = len( rows ) ,
												max_id = max_idx )

					return render_template( "index.html" ,
										message = 'no current sessions' )

app.add_url_rule( '/session_call_history/<device>' ,
				  'session_call_history' ,
				  defaults={'session_id': None} ,
				  view_func=session_call_history ,
				  methods=['GET'] )
app.add_url_rule( '/session_call_history/<device>/<session_id>' ,
				  'session_call_history' ,
				  view_func=session_call_history ,
				  methods=['GET'] )



# ----------------------------------------------------------------------------------------------------
def retrieve_policy( policy_moniker , provider_type ) :
					"""

					:param policy_moniker:
					:param provider_type:
					:return:
					"""

					json_row = None
					try :

						_logger.info( '...retrieve payload_policy ...' )
						con = sqlite3.connect( "/data/media/com.chromaticuniverse.cci_trinity/king_console.sqlite" )
						con.row_factory = tr_utils.dict_factory
						cur = con.cursor()

						s =  'select * from payload_policy ' \
							 'where moniker = "%s" '  \
							 'and provider_type = "%s" ' \
							 'and active = 1'  % ( policy_moniker , provider_type )
						cur.execute( s )

						json_row = cur.fetchone()
						if json_row is not None :
							_logger.info( '...retrieved default policy...%s' % json.dumps( json_row ) )
						else :
							_logger.error( '...could not retrieve default policy...' )
					except sqlite3.OperationalError as e :
						_logger.error( '...retrieve_policy statement failed...%s' , e.message )


					return json_row




# ----------------------------------------------------------------------------------------------------
def retrieve_default_db_path() :
					"""

					:return string db_path:
					"""
					db_path = None
					try :

						with open( 'bootstrap_db' , 'r' ) as f :
							db_path = f.read().strip().split( '=' )[1]

					except Exception as e :
						_logger.error( '...retrieve_default_db_path failed...%s' , e.message )


					return db_path



# ----------------------------------------------------------------------------------------------------
def retrieve_config_atom( atom ) :
					"""

					:param atom:
					:return:
					"""

					json_row = None
					try :

						_logger.info( '...retrieve_config_atom ...' )
						con = sqlite3.connect( "/data/media/com.chromaticuniverse.cci_trinity/king_console.sqlite" )
						con.row_factory = tr_utils.dict_factory
						cur = con.cursor()

						s =  'select map from metadata_config ' \
							 'where moniker = "%s" '  %  atom
						cur.execute( s )

						json_row = cur.fetchone()
						if json_row is not None :
							_logger.info( '...retrieved config map for ...%s' % atom )
						else :
							_logger.error( '...could not retrieve atom for %s...' % atom )
					except sqlite3.OperationalError as e :
						_logger.error( '...retrieve_policy statement failed...%s' , e.message )


					return json_row

