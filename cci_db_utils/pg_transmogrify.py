__author__ = 'William K. Johnson original version April 29 , 2015'

import threading, logging, time
import doctest
import unittest
import inspect
from datetime import datetime , timedelta
import subprocess as proc
import argparse
import os
import sys


# cci
import cci_utils.cci_constants as const
# postgres
import psycopg2
import psycopg2.extras


# constants
const.connect_prefix = '_dbs_'
const.log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'
# single row result
const.sql_static_dictionary = { 'sd_retrieve_version' : 'select version()',
                                'sd_retrieve_current_db' : 'select current_database()' ,
                                'sd_retrieve pg_id' : 'select pg_backend_pid()' ,
                                'sd_start_time_db' : 'select pg_postmaster_start_time()' ,
                                'sd_server_addr' : 'select inet_server_addr()'}
# multiple rows
const.sql_cursor_dictionary = { 'sd_enumerate_databases' : 'select datname from pg_database where datistemplate = false',
                                'sd_enumerate_tables' : "select table_name from information_schema.tables where table_schema='public' and table_name like 'peci%'" ,
                                'sd_enumerate_table_metadata' : 'select ordinal_position,' +
                                                                       'column_name,' +
                                                                       'data_type,' +
                                                                       'column_default,' +
                                                                       'is_nullable,' +
                                                                       'character_maximum_length,' +
                                                                       'numeric_precision ' +
                                                                       'from information_schema.columns ' +
                                                                       'where table_name = %s ' +
                                                                       'order by ordinal_position'
                               }
const.sql_dml_statement = { 'sd_truncate_tables'  : 'delete from %s' }
const.sql_default_cache_limit = 64
const.pg_dump_db_util = 'pg_dump'
const.pg_restore_db_util = 'pg_restore'
const.pg_cli_user = ''
const.pg_option_group = ['general' , 'output' , 'connection']

#-----------------------------------------------------------------------------------------------------------------------
class pg_transmogrify( object ) :

        """
        postgres database transmogrifier
        supplying a small subset of db functionality
        of the psycopg2 driver(i.e.,table and field enumeration ,
        table truncatiion , etc.) neccessary
        for peci fallback and commit
        """

        '''
        object model
        '''
        def __init__( self , name = 'cci_db' ,
                             user = 'postgres' ,
                             password = 'postgres' ,
                             host = 'localhost' ,
                             port = '5432' ,
                             connect_immediate = True ,
                             logging_on = True ,
                             kwargs = None ) :

             """
             creates postgres database transmogrifier from named parameters
             initializes configuration object , initializes self._logger
             :param name_:database name
             :param user: postgres user
             :param password: user password
             :param host : host machine
             :param port : database port
             :param connect_immediate : connect on initialization
             :param logging_on : logging
             :param kwargs: additonal named arguments
             :return:
             """

             self._dbs_dbname = name
             self._dbs_user = user
             self._dbs_password = password
             self._dbs_host = host
             self._dbs_port = port
             self._db_connect_str = None
             self._params_to_connect_str()
             self._db_connection = None
             self._db_version = None
             self._db_connected = False
             self._log_lvl = logging.DEBUG
             self._sql_history_cache = dict()
             self._sql_db_metadata = dict()
             self._sql_cache_limit = const.sql_default_cache_limit
             self._b_connect_immediate = connect_immediate
             self._transmogrify_facade = pg_transmogrify_facade( self )
             self._logger = None
             self._logger = logging.getLogger( 'peci_db' )

             if logging_on is True :
                 """create self._logger with 'peci_db'"""
                 self._logger.setLevel( logging.DEBUG )
                 """ create file handler"""
                 fh = logging.FileHandler( 'peci_db.log' + '-debug.log', mode='w')
                 fh.setLevel(logging.DEBUG )
                 """ create console handler """
                 ch = logging.StreamHandler()
                 ch.setLevel( logging.DEBUG )
                 """ create formatter and add it to the handlers """
                 formatter = logging.Formatter( const.log_format )
                 fh.setFormatter( formatter )
                 ch.setFormatter( formatter )
                 """ add the handlers to the self._logger """
                 self._logger.addHandler( fh )
                 self._logger.addHandler( ch )
                 self._logger.info( 'pg_transmogrify ,william k. johnson 2015' )

             if connect_immediate is True :
                self.connect()
                self._acquire_db_version()
                self._populate_db_session_info()

        def __del__( self ) :
            """
            close all database connections on destruction
            :return:
            """
            try:
                if self._db_connection is not None :
                    self._db_connection.close()
                    self._logger.info( 'closing all open database connections.' )
            except psycopg2.DatabaseError as err :
                self._logger.error( 'database error: %s' , err  )
                pass


        def __repr__( self ) :
             """
             returns string representation and construction info
             :rtype : basestring
             :return:
             """
             return "{__class__.__name__}(name={_dbs_dbname!r},user={_dbs_user!r}," \
                    "password={_dbs_password!r}," \
                    "host={_dbs_host!r}," \
                    "connect_str={_db_connect_str!r}," \
                    "config={_db_config!r}," \
                    "connect_immediate={_b_connect_immediate!r})".\
                    format( __class__=self.__class__ , **self.__dict__ )

        def __str__( self ) :
              """
              returns pretty string
              :rtype: basestring
              :return: str
              """
              return 'pg_transmogrify , 2015 ,william k. johnson'

        def __bool__( self ) :
              """
              returns connected
              :rtype bool
              :return: self._db_connected
              """
              return self._db_connected

        def __hash__( self ) :
              """
              :rtype: None
              :return None:
              """
              return None

        def __eq__( self, other) :
              """
              :rtype bool
              :param other:
              :return : bool
              """

              # TODO: implement this method
              return False

        def __reduce__( self ) :
              """
              persistence
              :return:
              """
              # TODO: implement this method


        """ helpers"""
        def _params_to_connect_str( self  ):
            """
            constructs connect string from db attributes
            :rtype: basestring
            :return connect_str:
            """
            connect_str =  str()
            for attr, value in self.__dict__.items():
               # attribute found
               if attr.find( const.connect_prefix , 0  ) is not -1 :
                    temp = attr[len( const.connect_prefix ):]
                    connect_str += temp
                    connect_str += '='
                    connect_str += value
                    connect_str += ' '
            connect_str = connect_str.rstrip( ' ' )
            self._db_connect_str = connect_str

        def _acquire_db_version( self ) :
            """
            get database version and additonal metadata.
            return version and optional additional metadata
            :return:
            """
            try:
                if self._db_connected is not True:
                    logging.error( 'operation not permitted.database not connected' )
                else:
                    cursor = self._db_connection.cursor()
                    self._execute_sql_statement( 'sd_retrieve_version' , cursor )
                    self._db_version = cursor.fetchone()
                    self._logger.info( self._db_version )
            except psycopg2.DatabaseError as err :
                self._logger.error( 'database error: %s' , err  )


        def _populate_db_session_info( self ) :
            """
            populate db session metadata
            :return:
            """
            try:
                if self._db_connected is True :
                    self._sql_db_metadata.clear()
                    cursor = self._db_connection.cursor()
                    for key , value  in const.sql_static_dictionary.items() :
                        self._execute_sql_statement( key , cursor )
                        self._sql_db_metadata[key] =  cursor.fetchone()
                        self._logger.info( self._sql_db_metadata[key]  )
            except psycopg2.DatabaseError as err :
                self._logger.error( 'database error: %s' , err  )
            finally :
                if cursor is not None :
                    cursor.close()


        def _execute_sql_statement( self , sql_key , db_cursor , fetchone = True  ) :
            """
            execute sql statement , single result
            :param sql_key: sql dictionary key
            :param db_cursor: active database cursor
            :return:

            caller is responsible for processing result set
            """
            if fetchone is True :
                self._logger.info( 'SQL:' + const.sql_static_dictionary[sql_key] )
                db_cursor.execute( const.sql_static_dictionary[sql_key] )
            else :
                self._logger.info( 'SQL:' + const.sql_cursor_dictionary[sql_key] )
                db_cursor.execute( const.sql_cursor_dictionary[sql_key] )

            self._update_sql_cache( sql_key )

        def _execute_sql_raw( self , statement  ) :
            """
            execute sql statement , no results
            :param statement:
            :return:
            """
            b_ret = False
            try:
                cursor = self._db_connection.cursor()
                self._logger.info( 'SQL:' + statement )
                cursor.execute( statement )
                b_ret = True
            except psycopg2.DatabaseError as err :
                self._logger.error( 'database error: %s' , err  )
            finally :
                if cursor is not None :
                    cursor.close()

            return b_ret


        def _update_sql_cache( self, sql_key ) :
            """
            insert sql statement into sql cache
            :param sql_key: sql dictionary key
            :return:
            """
            if len( self._sql_history_cache ) > self._sql_cache_limit :
                self._sql_history_cache.clear()
            st = datetime.fromtimestamp( time.time() ).strftime( '%Y-%m-%d %H:%M:%S' )
            self._sql_history_cache[st] = sql_key


        def stop_logging( self  , handler_type='file' ) :
            """
            swithc off all logging handlers
            :param handler_type :
            :return:
            """
            if handler_type == 'file' :
                self._logger.handlers = []
            # TODO complete this method


        """services"""
        def update_connection ( self ) :
            """
            redo connect string with session checking
            :return:
            """
            self._params_to_connect_str()
            self._logger.info( self._db_connect_str )

        def connect( self , connect_str = None ) :
            """
            connect to database

            :param connect_str : basestring
            :rtype : bool
            :return  : b_ret
            """
            if connect_str is None:
               connect_str = self._db_connect_str
            b_ret = False
            try:
                if self._db_connected is True :
                     self._logger.info( 'database connected...disconnecting...' )
                     self._db_connection.close()
                self._db_connection = psycopg2.connect( connect_str )
                self._logger.info( 'database connect string: %s' , connect_str  )
                b_ret = True
                self._logger.info( 'connected to database....ready.' )
                self._db_connected = True
            except psycopg2.DatabaseError as err :
                self._logger.error( 'database error: %s' , err  )

            return b_ret

        def share_connection( self , connection  ) :
            """
            use existing postgres connection
            :param connection : existing connection
            :return:
            """
            try:
                pass
            except psycopg2.DatabaseError as err :
                pass
            # TODO: implement this method
            pass

        def disconnect( self ) :
            """
            disconnect from database
            clear dictionaries
            :return:
            """
            try:
                if self._db_connection is not None :
                    self._db_connection.close()
                    self._db_connection = None
                    self._db_connected = False
                    self._sql_history_cache.clear()
                    self._sql_db_metadata.clear()
                    self._logger.info( 'disconnected from database....caches cleared...' )
                else:
                    self._logger.warning( 'database not connected...' )

            except psycopg2.DatabaseError as err :
                self._logger.error( 'database error: %s' , err  )

        def enum_databases( self ):
            """
            enumerate available databases
            :rtype : list
            :return : rows
            """
            rows = None
            try:
                if self._db_connected is True :
                    cursor = self._db_connection.cursor()
                    self._execute_sql_statement( 'sd_enumerate_databases' , cursor , False )
                    rows = cursor.fetchall()
            except psycopg2.DatabaseError as err :
                self._logger.error( 'database error: %s' , err  )
            finally :
                if cursor is not None :
                    cursor.close()

            return rows

        def enum_tables( self ) :
            """
            enumerate schema tables
            :rtype : list
            :return : rows
            """
            rows = None
            try:
                if self._db_connected is True :
                    cursor = self._db_connection.cursor()
                    self._execute_sql_statement( 'sd_enumerate_tables' , cursor , False )
                    rows = cursor.fetchall()
            except psycopg2.DatabaseError as err :
                self._logger.error( 'database error: %s' , err  )
            finally :
                if cursor is not None :
                    cursor.close()


            return rows

        def enum_table_metadata( self ) :
            """
            :rtype : tuple
            :return : rows
            """
            rows = None

            # TODO: implement this method

            return rows

        def purge_table_records( self , table_name , cascade = True ) :
            """
            purge postgres table of all rows

            :param table_name : name of table to purge
            :param cascade : cascade deletes
            :return:
            """
            sql = const.sql_dml_statement['sd_truncate_tables'] % table_name
            b_ret = self._execute_sql_raw( sql )
            self._update_sql_cache( 'sd_truncate_tables' )

            return b_ret


        """attributes"""
        @property
        def db_version( self ) :
            return self._db_version
        @property
        def db_name( self ) :
            return self._dbs_dbname
        @db_name.setter
        def db_name( self , name ) :
            self._dbs_dbname = name
        @property
        def db_password( self ) :
            return self._dbs_password
        @db_password.setter
        def db_password( self , password ) :
            self._dbs_password = password
        @property
        def db_host( self ) :
            return self._dbs_host
        @db_host.setter
        def db_host( self , host ) :
            self._dbs_host = host
        @property
        def db_port( self ) :
            return self._dbs_port
        @db_port.setter
        def db_port( self , port ) :
            self._dbs_port = port
        @property
        def db_user( self ) :
            return self._dbs_user
        @db_user.setter
        def db_user( self , user ) :
            self._dbs_user = user
        @property
        def db_connected( self ) :
            return self._db_connected
        @property
        def log_lvl(self ) :
            return self._log_lvl
        @log_lvl.setter
        def log_lvl( self , lvl ) :
            self._log_lvl = lvl
        @property
        def sql_cache( self ) :
            return self._sql_history_cache
        @property
        def sql_cache_limit( self ) :
            return self._sql_cache_limit
        @sql_cache_limit.setter
        def sql_cache_limit( self , limit ) :
            self._sql_cache_limit = limit
        @property
        def sql_db_metadata(self ) :
            return self._sql_db_metadata
        @property
        def facade( self ) :
            return self._transmogrify_facade


#-----------------------------------------------------------------------------------------------------------------------
class pg_binary_util_dump( object ) :

    """
    wrapper facade for runtime binary pg_dump
    with some command line magic for clarity
    """

    # switch mapping , token : switch
    pg_cli_dump_map = {
                          'help' : '--help' ,
                          'version' : '--version',
                          'user' : '-U' ,
                          'filename' : '-f' ,
                          'verbosity' : '-v' ,
                          'host' : '-h' ,
                          'data_only' : '-a' ,
                          'output_format' : '-F' ,
                          'include_table' : '-t'
                      }

    '''object model'''
    def __init__( self , full_path = None ,
                  user = 'peci_user' ,
                  password = 'peci_user' ,
                  db_name = 'peci_db' ,
                  host = 'localhost' ,
                  port = '5432' ,
                  out_file = 'peci_db.out' ) :

              self._command_map = dict()
              self._identity = const.pg_dump_db_util
              self._user = user
              self._password = password
              self._db_name = db_name
              self._db_host = host
              self._db_port = port
              self._out_file = out_file
              self._full_path = full_path

              self._populate_command_map()
              self._default_command_line = self._default_command()


    def __repr__( self ) :
             """
             returns string representation and construction info
             :rtype : basestring
             :return:
             """
             return "{__class__.__name__}(fullpath={_full_path!r},user={_user!r},password={_password!r}," \
                    "db_name={_db_name!r},host={_db_host!r},port={_db_port!r},out_file={_out_file!r})".\
                    format( __class__=self.__class__ , **self.__dict__ )


    '''attributes'''
    @property
    def command_map( self ) :
        return self._command_map
    @command_map.setter
    def command_map( self , cmap ) :
        self._command_map = cmap
    @property
    def identity( self ) :
        return self._identity
    @property
    def full_path( self ) :
        return self._full_path

    '''helpers'''
    def _populate_command_map( self ) :
        """
        command switches and options
        parameter values are mapped to tokens here
        """
        self._command_map['user'] = self._user
        self._command_map['filename'] = self._out_file
        self._command_map['host'] = self._db_host
        self._command_map['database'] = self._db_name
        # custom output format
        self._command_map['output_format'] = 'c'


    def _default_command( self ) :
        """
        build command string , order of commands is preserved
        sequence of tokens should mirror the actual command line desired
        :return : command list
        """
        commands = list()
        tokens = ['verbosity' , 'data_only', 'user', 'host' ,
                  'output_format' , 'filename' , 'database' ]
        [self._atom( elem , commands ) for elem in tokens]

        return commands


    def _atom( self , atom , command_lst  ) :
        """
        add switch and value( if any ) to command list ,
        subprocess call takes a list as input so there
        is no need to worry about spaces
        :param atom : switch atom
        :param command_list : list of command atoms
        """
        # if not in switch map is a param by position , i.e. , the database name
        if atom in self.pg_cli_dump_map :
            command_lst.append( self.pg_cli_dump_map[atom] )
        # if not in command map , does not take parameters , only a switch
        if atom in self._command_map :
            command_lst.append( self._command_map[atom] )


    def _default_output_handler( self , output ) :
        """
        default process stream handler
        :param output : stream
        :return:
        """
        print( output )


    """
    services
    """
    def execute( self , command_line = None , out_func = None ) :
        """
        method to execute system binary as subprocess

        :param command_line : command line list , parameters for execution
        :param out_func : function to process output
        :return b_ret : boolean
        """
        b_ret = False

        try:
            util_path = list()
            if self._full_path is not None :
                util_path.append( self._full_path )
            else :
                util_path.append( self._identity )
            default_command = list()
            if command_line is None :
                default_command = self._default_command_line
            else :
                default_command = command_line
            # concatenate binary moniker and command list
            util_path += default_command
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
            print ( e )

        return b_ret


#-----------------------------------------------------------------------------------------------------------------------
class pg_binary_util_restore( object ) :

    """
    wrapper facade for runtime binary pg_restore
    """

    # switch mapping , token : switch
    pg_cli_restore_map = {
                          'help' : '--help' ,
                          'version' : '--version',
                          'user' : '-U' ,
                          'filename' : '-f' ,
                          'verbosity' : '-v' ,
                          'host' : '-h' ,
                          'data_only' : '-a'
                         }

    '''object model'''
    def __init__( self , full_path = None ,
                  user = 'peci_user' ,
                  password = 'peci_user' ,
                  db_name = 'peci_db' ,
                  host = 'localhost' ,
                  port = '5432' ,
                  out_file = 'peci_db.out' ) :


       self._command_map = dict()
       self._identity = const.pg_restore_db_util
       self._full_path = full_path

    '''attributes'''
    @property
    def command_map( self ) :
        return self._command_map
    @command_map.setter
    def command_map( self , cmap ) :
        self._command_map = cmap
    @property
    def identity( self ) :
        return self._identity
    @property
    def full_path( self ) :
        return self._full_path

    '''helpers'''
    def _populate_command_map( self ) :
        pass

    """
    services
    """
    def execute( self , command_line ) :
        pass



#-----------------------------------------------------------------------------------------------------------------------
class pg_transmogrify_facade( object ) :
       """
       wrapper facade for postgres db command line utils
       exposing fincionality of the fallback and commit
       peci procedures
       """

       '''object model'''
       def __init__( self , mogrifier = None  ) :

            self._valid = True

            self._binaries = dict()
            self._binaries[const.pg_dump_db_util] = pg_binary_util_dump()
            self._binaries[const.pg_restore_db_util] = pg_binary_util_restore()
            self._requires_superuser = True
            self._versions = list()
            self._interactive = False
            self._mogrifier = mogrifier

            """create self._logger with'"""
            """create self._logger with'"""
            self._logger = logging.getLogger( 'peci_transmogrify_facade' )
            self._logger.setLevel( logging.DEBUG )
            """ create file handler"""
            fh = logging.FileHandler( 'peci_transmogrify_facade.log'  + '-debug.log', mode='w' )
            fh.setLevel(logging.DEBUG )
            """ create console handler """
            ch = logging.StreamHandler()
            ch.setLevel( logging.DEBUG )
            """ create formatter and add it to the handlers """
            formatter = logging.Formatter( const.log_format )
            fh.setFormatter( formatter )
            ch.setFormatter( formatter )
            """ add the handlers to the self._logger """
            self._logger.addHandler( fh )
            self._logger.addHandler( ch )


       def __bool__( self ) :
            """
            is object valid
            :return : boolean
            """
            return self._valid


       '''attributes'''
       @property
       def versions( self ) :
            return self._versions
       @property
       def requires_superuser( self ) :
            return self.requires_superuser
       @property
       def interactive( self ) :
            return self._interactive

       '''services'''
       def stat_names( self ) :
            """
            :rtype : boolean
            :return:
            """
            # check if our utils actually exist
            b_ret = False
            try:
                # for each utility
                for key , value in self._binaries.items() :
                    os.path.exists( value.identity )
                b_ret = True
            # io exception will be raised on not found
            # by design we do not try to find the binary ,
            # which would add anothe layer of complexity
            except IOError as e :
                self._logger.error( e )
                self._valid = False

            return b_ret

       def _purge_tables( self , table_list ) :
           """
           procedure to purge tables before calling
           pg_restore. We use delete instead of truncate
           because of foreign key dependencies
           from django
           :param table_list : list
           :return:
           """
           b_ret = False
           try :
               # for each table in domain list
               for elem in table_list  :
                    # purge
                    self._logger.warn( 'purging table ' + elem[0]  + '....' )
                    b_ret = self._mogrifier.purge_table_records( elem[0] )
                    if b_ret is False :
                        break

           except IOError as e :
               self._logger.error( e )

           return b_ret

       def generate_commit( self , gen_file_out = None ) :
            """
            state machine to implement the generate/commit procedure

            :param gen_file_out : generated output file
            :return : boolean
            """
            # TODO: implement this method

            b_ret = False
            try:
                self._logger.warn( 'initiating commit generation....' )
                self._logger.warn( 'rotating fielded configuration to fallback configuration....' )
                self._logger.warn( 'exporting data configuration to fielded configuration....' )

            except:
                self._logger.error( 'commit generation failed....' )
                return False

            self._logger.info( 'commit generation succeeded....' )

            return True

       def fallback( self , fallback_file = None , fielded_file = None ) :
            """
            state machine to execute the fallback procedure

            :param fallback_file:
            :param fielded_file:
            :return : boolean
            """
            b_ret = False
            try:
                self._logger.warn( 'initiating fallback....' )
                # state machine
                processing = True
                state = 'purge'
                while processing is True :
                    if self._mogrifier.db_connected is not True :
                         self._logger.error( 'mogrifier not connected....' )
                         break;
                    if state == 'purge' :
                        # truncate tables
                        self._logger.warn( 'purging peci tables in working database....' )
                        b_ret = self._purge_tables( self._mogrifier.enum_tables() )
                        if b_ret is True :
                            state = 'load'
                            continue
                        else :
                           self._logger.error( 'purging tables failed....' )
                           break
                    elif state == 'load' :
                            # load current database from fallback stash
                            self._logger.warn( 'loading working database from fallback resource ....' )
                            state = 'copy'
                            continue
                    elif state  == 'copy' :
                            # copy fallback resource to fielded resource
                            self._logger.warn( 'copying fallback resource to fielded resource....' )
                            processing = False
                            b_ret = True

            except :
                self._logger.error( 'exception in fallback....' )
            finally:
                if b_ret is True :
                    self._logger.info( 'fallback succeeded....' )
                else :
                    self._logger.error( 'fallback failed....' )

            return b_ret

#-----------------------------------------------------------------------------------------------------------------------
def output_handler( output ) :

    print( output )

#-----------------------------------------------------------------------------------------------------------------------
def transmogrify_main()  :

    # command line
    parser = argparse.ArgumentParser( description='pg_transmogrify , william k. johnson 2015' ,
                                      epilog='...postgres processing utlities...')

    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='verbose flag' )
    parser.add_argument('--fallback', '-fbk',
                        action='store_true',
                        help='peci fallback procedure' )
    parser.add_argument('--commit', '-cmt',
                        action='store_true',
                        help='peci commit procedure' )
    parser.add_argument('--synchronize', '-sync',
                        action='store_true',
                        help='peci db sync procedure' )
    parser.add_argument('--enumerate', '-enum',
                        action='store_true',
                        help='enumerate peci tables' )
    parser.add_argument('--domain', '-dm',
                        choices=['aoa', 'atn', 'europe','all'] ,
                        default='all' ,
                        required=True ,
                        help='peci domain' )
    args = parser.parse_args()

    walk_args = True
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    executed = False


    if len( sys.argv ) == 1 :
        print( args.help )
    if args.verbose is True :
        info = True
    else :
        info = False
    postgres = pg_transmogrify( connect_immediate = False , logging_on = info )
    if bool( postgres.facade ) is True :
        # postgres.facade.generate_commit()
        if args.fallback is True :
            sys.stdout.write( "\033[91mFallback is not reversible , proceed?" )
            choice = input().lower()
            if choice in yes:
              postgres.connect()
              if postgres.db_connected is True :
                  postgres.facade.fallback()
                  executed = True
            elif choice in no :
                pass
            else:
                sys.stdout.write("please respond with 'yes' or 'no'")
        elif args.commit is True :
            if executed is True :
                print( 'can only execute one process atomically...' )
        elif executed is False :
            print( 'please specify an operation...')
    sys.stdout.write( "\033[0m" )
    #dump_out = pg_binary_util_dump( full_path = '/usr/bin/pg_dump')
    #dump_out.execute( out_func = output_handler )

if __name__ == "__main__":

    # do a test connect and retrieve
    try :
        postgres = pg_transmogrify( connect_immediate = True , logging_on = True )
    except psycopg2.DatabaseError , exception:
        print exception
        sys.exit( 1 )
    finally:
        pass
    #doctest.testmod()
    #transmogrify_main()


