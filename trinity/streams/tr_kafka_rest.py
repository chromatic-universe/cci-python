# tr_kafka.py    william k. johnson 2016


import os
import sys
from StringIO import StringIO
import logging
from math import ceil
from flask import Flask , request , send_file , render_template , url_for
from flask import redirect , Response , jsonify
from flask_restful import Resource, Api , reqparse, abort
import subprocess as proc
import sqlite3
import time
import signal
import Queue
import requests
import json

#from pykafka import KafkaClient

#cci
from application import app , \
	                    _logger , \
					    kafka_no_resource_exception
import tr_sqlite
import tr_utils

api = Api( app )

supported_kafka_version = { "version" : "0.10" }
trinity_kafka_consumer = None
trinity_default_db_path = None


# ----------------------------------------------------------------------------------
def init_kafka_consumer( param_dictionary = None ) :
				"""

				:param param_dictionary:
				:return:
				"""

				try :

					trinity_default_db_path = tr_sqlite.retrieve_default_db_path()
					consumer_moniker = tr_utils.local_mac_addr()


				except Exception as e :
					_logger.error( 'error in init consumer...%s' % e.message )





# -----------------------------------------------------------------------------------
def abort_no_exist_version( version  ) :
				"""

				:param version:
				:return:
				"""

				if todo_id not in TODOS:

					abort( 404 ,
						   message="version {} doesn't exist".format( version ) )




# -----------------------------------------------------------------------------------
class tr_kafka_stream( object ) :

				"""
				tr_kafka_stream
				"""

				def __init__( self ,
							  default_bootstrep ,
							  logger = None )  :

						"""

						:param default_db:
						:param logger:
						:return:
						"""


						if logger is None :
							raise Exception( 'no logging instance specified...' )
						self.logger = logger

						self.logger.info( '...kf_kafka_stream initialized...' )



				def __del__(self) :
						"""

						:return:
						"""

						pass




# -----------------------------------------------------------------------------------
class cci_kafka_version( Resource ) :
				"""
				metadata
				"""

				def get ( self ) :
						"""
						GET return running kafka software version , also test connect
						:param supported_version:
						:return:
						"""


						return jsonify( supported_kafka_version )

api.add_resource( cci_kafka_version , '/kafka/version' )




# -----------------------------------------------------------------------------------
class cci_kafka_bootstrap( Resource ) :
				"""
				metadata
				"""

				def get ( self ) :
						"""
						GET return kafka bootsrap server , only supporting single broker for now
						:param supported_version:
						:return:
						"""

						j = json.loads( tr_sqlite.retrieve_config_atom( 'trinity-kafka-bootstrap' )['map'] )

						return j

api.add_resource( cci_kafka_bootstrap , '/kafka/bootstrap' )





# -----------------------------------------------------------------------------------
class cci_kafka_topics( Resource ) :
				"""
				metadata
				"""

				def get ( self ) :
						"""
						GET return kafka topicsr
						:param supported_version:
						:return:
						"""
						try :
							boot = json.loads( tr_sqlite.retrieve_config_atom( 'trinity-kafka-bootstrap' )['map'] )
							strap = boot['bootstrap_servers']

							#kc = KafkaClient( hosts = strap )
							topics = kc.topics

							
						except Exception as e :

							topics =  { "error" : e.message }

						return topics

api.add_resource( cci_kafka_topics , '/kafka/topics' )

