# william k. johnson 2015

import unittest
import peci_db_utils.pg_transmogrify as pt
import peci_db_utils.constants as const
import logging
import time
from datetime import datetime , timedelta



# constants
const.test_log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'
const.init_string = 'connection should %s be initialized'

# TODO: set logging to error for mogrify instances

class test_pg_transmogrify( unittest.TestCase ) :

    @classmethod
    def setUp( cls ) :

        cls._remote_server = '10.0.2.5'

    @property
    def remote_server( self ) :
        return cls._remote_server
    @remote_server.setter
    def remote_server( self , server ) :
        cls._remote_server = server

    def test_pg_transmogrify_construction_empty_params( self ) :

        self.assertIsNotNone( pt.pg_transmogrify() , msg  = 'construction failed for pg_transmogrify' )

    def test_pg_transmogrify_construction_connect_immediate_no( self ) :

        pgmog = pt.pg_transmogrify( connect_immediate=False )
        self.assertFalse( pgmog.db_connected , msg = const.init_string % 'not' )

    def test_pg_transmogrify_connect_localhost( self ) :

        pgmog = pt.pg_transmogrify( host='localhost' )
        self.assertTrue( pgmog.db_connected , msg = const.init_string )

    def test_pg_transmogrify_connect_remote( self ) :

        pgmog = pt.pg_transmogrify( host=self._remote_server )
        self.assertTrue( pgmog.db_connected , msg = const.init_string )

    def test_pg_transmogrify_disconnect( self ) :

        pgmog = pt.pg_transmogrify()
        pgmog.disconnect()
        self.assertFalse( pgmog.db_connected , msg = const.init_string % 'not ' )

    def test_pg_transmogrify_restart( self ) :
        """
        calling connect on an already connected db willl disconnect and reconnect - a de facto restart
        """
        pgmog = pt.pg_transmogrify()
        pgmog.connect()
        self.assertTrue( pgmog.db_connected , msg = const.init_string )

    def test_pg_transmogrify_connect_default_user( self ) :

        pgmog = pt.pg_transmogrify( user= 'peci_admin' )
        self.assertTrue( pgmog.db_connected , msg = const.init_string )

    def test_pg_transmogrify_connect_default_database( self ) :
        """
        connect default db
        """
        pgmog = pt.pg_transmogrify( name = 'peci_admin' )
        self.assertTrue( pgmog.db_connected , msg = const.init_string )

    def test_pg_transmogrify_key_error_in_cache( self ) :
         """
         exercise sql cache dictionary
         """
         pgmog = pt.pg_transmogrify( connect_immediate = False )
         self.assertRaises( KeyError , pgmog._execute_sql_statement , sql_key='@xyz' , db_cursor=None )

    def test_pg_transmogrify_sql_cache_clears_upon_limit( self ) :
         """
         sql_cache recognizes cache limit
         """
         pgmog = pt.pg_transmogrify( connect_immediate = False )
         limit = 10
         sql = 'select version()'
         pgmog.sql_cache_limit = limit

         for idx in range( limit + 1 ) :
             pgmog._update_sql_cache( sql )

         self.assertEqual( len( pgmog.sql_cache ) , 1 , msg = 'cache limit failed' )

    @classmethod
    def tearDown( cls ) :
        pass

if __name__ == '__main__':


    unittest.main( verbosity=9 )
