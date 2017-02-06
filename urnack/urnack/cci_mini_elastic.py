# cci_mini_elastic.py william k. johnson 2016
# python 2 - py elasticsearch does not support python 3

#############
# python standard
import sys
import os
import json
import logging
import abc
from abc import ABCMeta , abstractmethod
import requests


import elasticsearch
import pymongo
from pymongo import MongoClient

#cci
import cci_mini_mobile


# ------------------------------------------------------------------------------
class cci_mini_elastic( cci_mini_mobile.cci_mobile ) :
			"""
			minimal elasticsearch implementation
			connect , add , query
			"""

			def __init__( self ,
						  target_servers=None ,
						  connect_on_construct=False ) :
				"""
				init

				:param target_server:
				:return:
				"""
				super( cci_mini_elastic , self ).__init__()


				# elasticsearch can connect to multiple hosts concurrently
				# this is a list of dictionaries
				self._target_servers = target_servers
				self._connect_on_construct = connect_on_construct
				self._elasticsearch = None
				self._server_info = None
				self._server_banner = str()


				if not self._target_servers :
					self._target_servers = [{'host': 'localhost'}]
				#if connect on construct , connect
				if self._connect_on_construct :
					self.connect()

			@property
			def target_servers( self ) :
				return self._target_servers
			@target_servers.setter
			def target_servers( self , server ) :
				self._target_servers = servers
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
			def server_info( self ) :
				return self._server_info
			@server_info.setter
			def server_info( self , info ) :
				self._server_info = info
			@property
			def server_banner( self ) :
				return self._server_banner
			@server_banner.setter
			def server_banner( self , banner ) :
				server_info._server_banner = banner
			@property
			def elastic( self ) :
				return self._elasticsearch


			def __repr__( self ) :
				 """
				 returns string representation and construction info
				 :rtype : basestring
				 :return:
				 """
				 return "{__class__.__name__}(target_servers={_target_servers!r}," \
						"gmail_test_account{_gmail_test_account!r},connect_on_construct{_connect_on_construct})". \
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
					# populate server info , we only support the first host for simplicity
					req = requests.get( 'http://' + self._target_servers[0]['host'] )
					self._server_info = req.json()

					# pretty print
					self._server_banner =  json.dumps( req.json(), sort_keys=True ,
									  indent=4, separators=(',', ': ') )

					# log some server info
					self._logger.info( 'elasticsearch version=' + self._server_info['version']['number'] + ';'
										+ 'lucene version=' + self._server_info['version']['lucene_version'])
					self._logger.info( self._target_servers[0]['host'])
					self._logger.info( self._server_banner )
					# instantiate the elasticsearch server
					# without specifying the connection class this
					# will throw an untyped connect exception(undocumented) . deduced from walking
					# into the urllib3 connect code which requires a thread pool
					# to exist

					self._elasticsearch = elasticsearch.Elasticsearch( self._target_servers ,
					                                                   connection_class=elasticsearch.connection.RequestsHttpConnection )
					self._logger.info( '...connected to elasticsearch server...' )

				 except elasticsearch.TransportError as e :
					self._logger.error( e.message + ' code:%d' % e.status_code  )
				 except elasticsearch.ConnectionTimeout as e :
					self._logger.error( e.message  )
				 except requests.RequestException as e :
					self._logger.error( e.message  )
				 except Exception as e :
					 self._logger.error( e )




			def index_payload( self , idx=None , dtype=None , sentinel=0 , payload=None ) :
				"""
				index_payload , json payload

				:param idx:
				:param dtype:
				:param payload:
				:param sentinel:
				:return:
				"""

				try :
					#  we assume json is valid :L we ask for forgiveness
					#  right now  elastisearch accepts invalid json
					#  the api is very permissive with this - we'll go along
					if payload :
						self._elasticsearch.index( index=idx ,
												   doc_type=dtype ,
												   id = sentinel ,
												   body=payload )

					self._logger.info( 'indexed json payload...'  )

				except ValueError as e :
					self._logger.error( e.message )




'''
# ------------------------------------------------------------------------------
def payload_main( payload=None , account=None ) :
        """
        send a json payload to elasticsearch

        :return:
        """

        # we use our own out stream for module level exceptions
        # in case logger has not been constructed
        ostr = io.ostream_py()
        # target hosts - by trial and error , this is the correct connect
        # string for aws elasticsearch( i.e. 'host' not 'hosts' and no url prefix
        # if you're talking to the REST interface. coyld not get direct connect
        # over 9200 to work in any configuration
        server_param =  [{ 'host' :'search-chromatic-search-p647s4rdqjcgub7tt7neealjn4.us-west-2.es.amazonaws.com' ,
                           'port' : 80}]

        try :
            # instantiate our gmvault wrapper
            cci = cci_mini_elastic( target_servers=server_param ,
                                    gmail_test_account=account )

            # send a payload
            if payload :
                cci.index_payload( idx=payload['idx'] ,
                                   dtype=payload['dtype'] ,
                                   sentinel=payload['sentinel'] ,
                                   payload=payload['body'] )

            cci.logger.info( 'ok ...' )
            # object representation
            ostr << repr( cci )\
                 << const.endl

        except IOError as e :
            ostr << 'IO error ' << e.message << const.endl
        except elasticsearch.ElasticsearchException as e :
            # this exception does not supply a proper message , dump the repr
            ostr << e << const.endl
        except Exception as e:
            ostr << e.__class__.__name__ + ':' + e.message << const.endl


# ------------------------------------------------------------------------------
def gvault_main( account=None ) :
        """
        run gvault to archive gmail to json

        :return:
        """

        # execute default command line
        # we use our own out stream for module level exceptions
        # in case logger has not been constructed
        ostr = io.ostream_py()

        try :
            # instantiate our elastic facade
            home = expanduser( "~" )
            cci = cci_mini_gmail( gmail_account=account ,
                                  archive_dest=home + '/cci_vault' )

            #execute subprocess
            cci.mogrify_gmail()

            cci.logger.info( 'ok ...' )
            # object representation
            ostr << repr( cci )\
                 << const.endl

        except IOError as e :
            ostr << 'IO error ' << e.message << const.endl
        except Exception as e:
            ostr << e.__class__.__name__ + ':' + e.message << const.endl



 # ------------------------------------------------------------------------


if __name__ == '__main__' :

        # command line

        parser = argparse.ArgumentParser( description='\033[92mcci_mini_elastic , william k. johnson 2015, all rights reserved\033[0m' ,
                                          epilog='\033[92m...elasticsearch processing utils...\033[0m' )

        parser.add_argument('--verbose', '-v',
                            action='store_true',
                            help='verbose flag' )
        parser.add_argument('--payload', '-p',
                            action='store_true',
                          :param idx:
					:param dtype:
					:param payload:
					:param sentinel:
					:return:
					"""

					try :
						#  we assume json is valid :L we ask for forgiveness
						# :param idx:
					:param dtype:
					:param payload:
					:param sentinel:
					:return:
					"""

					try :
						#  we assume json is valid :L we ask for forgiveness
						#  right now  elastisearch accepts invalid json
						#  the api is very permissive with this - we'll go along
						if payload :
							self._elasticsearch.index( index=idx ,
													   doc_type=dtype ,
													   id = sentinel ,
													   body=payload )

						self._logger.info( 'indexed json payload...'  )

					except ValueError as e :
						self._logger.error( e.message  )
			 right now  elastisearch accepts invalid json
						#  the api is very permissive with this - we'll go along
						if payload :
							self._elasticsearch.index( index=idx ,
													   doc_type=dtype ,
													   id = sentinel ,
							:param idx:
					:param dtype:
					:param payload:
					:param sentinel:
					:return:
					"""

					try :
						#  we assume json is valid :L we ask for forgiveness
						#  right now  elastisearch accepts invalid json
						#  the api is very permissive with this - we'll go along
						if payload :
							self._elasticsearch.index( index=idx ,
													   doc_type=dtype ,
													   id = sentinel ,
													   body=payload )

						self._logger.info( 'indexed json payload...'  )

					except ValueError as e :
						self._logger.error( e.message  )
									   body=payload )

						self._logger.info( 'indexed json payload...'  )

					except ValueError as e :
						self._logger.error( e.message  )
			  help='send p:param idx:
					:param dtype:
					:param payload:
					:param sentinel:
					:return:
					"""

					try :
						#  we assume json is valid :L we ask for forgiveness
						#  right now  elastisearch accepts invalid json
						#  the api is very permissive with this - we'll go along
						if payload :
							self._elasticsearch.index( index=idx ,
													   doc_type=dtype ,
													   id = sentinel ,
													   body=payload )

						self._logger.info( 'indexed json payload...'  )

					except ValueError as e :
						self._logger.error( e.message  )
			ayload' )
        parser.add_argument('--gmail', '-g',
                            action='store_true',
                            help='archive mail' )
        parser.add_argument('--account', '-a',
                            required=True ,
                            help='gmail account(required)' )
        args = parser.parse_args()

        if len( sys.argv ) == 1 :
            print args.help
            sys.exit( 1 )
        if ( args.payload and args.gmail ) or ( not args.payload and not args.gmail ) :
            print '\033[91mplease specify either payload or gmail....\033[0m'
            sys.exit( 1 )
        elif args.payload :
            load = { 'idx' : 'posts' ,
                     'dtype' : 'blogs' ,
                     'sentinel' : 21,
                     'body' : { 'author': 'claude balls',
                                'blog': 'fop',
                                'title': 'How to Write Clickbait Titles About Git Being Awful Compared to Mercurial',
                                'topics': ['mercurial', 'git', 'flamewars', 'hidden messages'],
                                'awesomeness': 0.95
                              }
                   }
            payload_main( payload=load , account=args.account )
        elif args.gmail :
            gvault_main( account=args.account )
        else :
            print args.help

		server_param =  [{ 'host' :'search-chromatic-search-p647s4rdqjcgub7tt7neealjn4.us-west-2.es.amazonaws.com' ,
                           'port' : 80}]

		cci = cci_mini_elastic( server_param  )
'''



