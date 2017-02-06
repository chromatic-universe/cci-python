# cci_mini_elastic.py william k. johnson 2016
# python 2 - py elasticsearch does not support python 3

#############
# python standard
import future
import sys
import os
from os.path import expanduser
import doctest
import unittest
import logging
import argparse
import json
import subprocess as proc
##############
# old school meta
from abc import ABCMeta , abstractmethod
##############
# our utility io
import cci_utils.cci_io_tools as io
# our constants
import cci_utils.cci_constants as const
##############
# url aux requests
import requests
# elasticsearch server interface
import elasticsearch
# gmail archive interface
import gmv

# our constants are typed from utils
# so they cannot be redefined at module scope
# mailbox-account and path to arhive
const.default_command_line = 'gmvault sync %s -d %s'

# ------------------------------------------------------------------------------
class cci_mini_gmail( object ) :
        """
        minimal wrapper for elasticsearch gmail
        """

        def __init__( self ,
                      gmail_account=None ,
                      archive_dest=None ) :
            """
            init

            :param gmail_account :
            :param archive_dest
            :return

            """

             # logging
            self._logger = io.init_logging( self.__class__.__name__  )
            self._logger.info( self.__class__.__name__ + '...'  )

            self._gmail_account = gmail_account
            self._archive = archive_dest

            # our vault directory
            if  self._gmail_account is None :
                self._gmail_account = 'foo@gmail.com'
            path = self._archive + '-' + self._gmail_account
            try:
                os.makedirs( path )
            except OSError as e:
                # path exists - if its not a directory raise
                if not os.path.isdir( path):
                    raise
            self._archive = path

        @property
        def gmail_account( self ) :
            return self._gmail_account
        @gmail_account.setter
        def gmail_account( self , account ) :
            self._gmail_account = account
        @property
        def archive( self ) :
            return self._archive
        @archive.setter
        def archive( self , arc ) :
            self._archive = arc
        @property
        def logger( self ) :
            return self._logger
        @logger.setter
        def logger( self , log ) :
            self._logger = log


        def __repr__( self ) :
             """
             returns string representation and construction info
             :rtype : basestring
             :return:
             """
             return "{__class__.__name__}(gmail_account{_gmail_account!r},archive{__archive})". \
                    format( __class__=self.__class__ , **self.__dict__ )


        def __str__( self ) :
              """
              returns pretty string
              :rtype: basestring
              :return: str
              """
              return self.__class__.__name__ +  ' 2016 , william k. johnson'


        def _default_output_handler( self , output ) :
            """
            default process stream handler for subprocess
            :param output : stream
            :return:
            """
            print output


        def _perform( self , command_line = None , out_func = None ) :
            """
            subprocess gvault

            :param command_line : command line list , parameters for execution
            :param out_func : function to process output
            :return b_ret : boolean
            """

            b_ret = False

            try:
                exec_command = str()
                if command_line is None :
                    #use default
                    exec_command = const.default_command_line
                else :
                    exec_command = command_line
                # util path
                exec_command = exec_command % ( self._gmail_account , self._archive )
                util_path = exec_command.split()
                # subprocess call , checks return value of process and returns output
                # output is returned as byte array and needs to be decoded to utf-8
                output = proc.check_output( util_path ).decode()
                # call the output stream handler
                # TODO this shold be a memory stream not a string
                if out_func is None :
                    self._default_output_handler( output )
                else :
                    out_func( output )
                b_ret = True
            except proc.CalledProcessError as e :
                # thrown if process call is something other than 0
                self._logger.error( e.message )

            return b_ret


        def mogrify_gmail( self ) :
            """
            mogrify gmail

            run gvault as subprocess
            """
            b_ret = self._perform()




# -----------------------------------------------------------------------------
class cci_elastic_skel( object) :
        """
        abstract base
        """
        _metaclass__ = ABCMeta

        '''object model'''
        def __init__( self ) :
            pass

        @property
        @abstractmethod
        def target_server( self ) :
            pass

# ------------------------------------------------------------------------------
class cci_mini_elastic( cci_elastic_skel ) :
        """
        minimal elasticsearch implementation
        connect , add , query
        """

        def __init__( self ,
                      target_servers=None ,
                      gmail_test_account=None ,
                      connect_on_construct=True ) :
            """
            init

            :param target_server:
            :return:
            """
            super( cci_elastic_skel , self ).__init__()

            # logging
            self._logger = io.init_logging( self.__class__.__name__  )
            self._logger.info( self.__class__.__name__ + '...'  )

            # elasticsearch can connect to multiple hosts concurrently
            # this is a list of dictionaries
            self._target_servers = target_servers
            # account for gmail testing
            self._gmail_test_account = gmail_test_account
            self._connect_on_construct = connect_on_construct
            self._elasticsearch = None
            self._server_info = None
            # cci mini gmail
            # get home directory fro archive
            home = expanduser( "~" )
            self_cci_gmail = cci_mini_gmail( gmail_account=self._gmail_test_account ,
                                             archive_dest=home + '/cci_vault' )

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
        def gmail_account( self ) :
            return self._gmail_test_account
        @gmail_account.setter
        def gmail_account( self , account ) :
            self._gmail_test_account = account
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

            try :
                # populate server info , we only support the first host for simplicity
                req = requests.get( 'http://' + self._target_servers[0]['host'] )
                self._server_info = req.json()
                # pretty print
                print json.dumps( req.json(), sort_keys=True ,
                                  indent=4, separators=(',', ': ') )
                # log some server info
                self._logger.info( 'elasticsearch version=' + self._server_info['version']['number'] + ';'
                                    + 'lucene version=' + self._server_info['version']['lucene_version'])
                # instantiate the elasticsearch server
                # without specifying the connection class this
                # will throw an untyped connect exception(undocumented) . deduced from walking
                # into the urllib3 connect code which requires a thread pool
                # to exist
                self._elasticsearch = elasticsearch.Elasticsearch( self._target_servers ,
                                                                   connection_class=elasticsearch.connection.RequestsHttpConnection )
            except elasticsearch.TransportError as e :
                self._logger.error( e.message + ' code:%d' % e.status_code  )
            except elasticsearch.ConnectionTimeout as e :
                self._logger.error( e.message  )


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
                    self._logger.error( e.message  )

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
                            help='send payload' )
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





