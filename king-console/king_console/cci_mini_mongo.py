# cci_mini_mongo.py     william k. johnson


#############
# python standard
import sys
import os
import json
import logging
import requests
import pprint
import StringIO
import pymongo
import json
from pymongo import MongoClient

#cci
import cci_mini_mobile


# ---------------r---------------------------------------------------------------
class cci_mini_mongo( cci_mini_mobile.cci_mobile ) :
			"""
			minimal elasticsearch implementation
			connect , add , query
			"""

			def __init__( self ,
						  bootstrap=None ,
						  port=27017 ,
						  device_id=None ,
						  connect_on_construct=True ) :
				"""
				init

				:param target_server:
				:return:
				"""
				super( cci_mini_mongo , self ).__init__()


				# elasticsearch can connect to multiple hosts concurrently
				# this is a list of dictionaries
				self._bootstrap = bootstrap
				self._connect_on_construct = connect_on_construct
				self._mongo = None
				self._mongo_dbs = None
				self._mongo_port = port
				self._device_id = device_id
				self._device_info = dict()
				self._connected = False


				if not self._bootstrap :
					self._bootstrap = 'localhost'
				#if connect on construct , connect
				if self._connect_on_construct :
					self.connect()

			@property
			def bootstrap( self ) :
				return self._bootstrap
			@bootstrap.setter
			def bootstrap( self , server ) :
				self._bootstrap = servers
			@property
			def connected( self ) :
				return self._connected
			@connected.setter
			def connected( self , conn ) :
				self._connected = conn
			@property
			def device_id( self ) :
				return self._device_id
			@device_id.setter
			def device_id( self , id  ) :
				self._device_id = id
			@property
			def device_info( self ) :
				return self._device_info
			@device_info.setter
			def device_info( self , info  ) :
				self._device_info = info
			@property
			def logger( self ) :
				return self._logger
			@logger.setter
			def logger( self , log ) :
				self._logger = log
			@property
			def connect_on_construct( self ) :
				return self._connect_on_construct
			@connect_on_construct.setter
			def connect_on_construct( self , val ) :
				self._connect_on_construct = val
			@property
			def mongo( self ) :
				return self._mongo


			def __repr__( self ) :
				 """
				 returns string representation and construction info
				 :rtype : basestring
				 :return:
				 """
				 return "{__class__.__name__}(bootstraps={_bootstrap!r}," \
						"connect_on_construct={_connect_on_construct})". \
						format( __class__=self.__class__ , **self.__dict__ )


			def __str__( self ) :
				  """
				  returns pretty string
				  :rtype: basestring
				  :return: str
				  """
				  return self.__class__.__name__ +  ' 2016 , william k. johnson'


			def connect( self  ) :

				 """
				 connect to elastic host direct
				 we take no kargs

				 :return:
				 """

				 self._logger.info( '....connect...' )

				 try :
					 	connect_str = 'mongodb://' + self._bootstrap + \
									  ':'  + \
									 str( self._mongo_port )


						self._mongo = MongoClient( connect_str ,
												   tz_aware = True ,
												   socketTimeoutMS = 5000 ,
												   connectTimeoutMS = 5000 )
						self._mongo_dbs = self._mongo.database_names()
						db = self._mongo['cci_maelstrom']
						cursor = db['auth_devices'].find({'device_id' : self._device_id})
						for document in cursor :
							self._device_info = document
						self._logger.info( '....mongo ok....' )

				 except Exception as e :
						self._logger.error( e.message )
						self._connected = False
				 self._connected = True

