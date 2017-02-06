__author__ = 'william k. johnson 2015'



import os
import sys
import subprocess
import argparse
import clang.cindex as clang
import unittest
import doctest
import copy
import pprint

from cci_mini_interface import cci_mini_clang_tool
import cci_utils.cci_io_tools as io
import cci_utils.cci_constants as const

const.cxx = '-std=c99'
const.cpp = '-std=c++11'
const.llvm_config = 'llvm-config'
const.config_prefix = '--'

# config flags
llvm_config_dict = {  'version' : None ,
                      'prefix' : None ,
                      'src-root' : None ,
                      'obj-root' : None ,
                      'bindir' : None ,
                      'includedir' : None ,
                      'libdir' : None ,
                      'cppflags' : None ,
                      'cflags' : None ,
                      'cxxflags' : None ,
                      'ldflags' : None ,
                      'system-libs' : None ,
                      'libs' : None ,
                      'libnames' : None ,
                      'libfiles' : None ,
                      'components' : None ,
                      'targets-built' : None ,
                      'host-target' : None ,
                      'build-mode' : None ,
                      'assertion-mode' : None
                 }

#-------------------------------------------------------------------------
class llvm_config_exception( Exception ) :
    """
    llvm config exception
    """
    def __init__( self ,*args ,**kwargs ):
        Exception.__init__( self ,*args ,**kwargs )

# ------------------------------------------------------------------------
class cci_mini_llvm_config( cci_mini_clang_tool ) :

        """
        small utility wrapper facade for llvm-config util
        """

        '''object model'''
        def __init__( self , fullpath = None , vargs_lst = None ) :

             # full path refers here to path to llvm-config
             super( cci_mini_llvm_config , self).__init__( fullpath , vargs_lst )

             if self.fullpath is None:
                    self.log.error(  'no path specified for llvm-config...' )
                    raise llvm_config_exception( 'no fullpath specified' )

             self._config_dict = copy.deepcopy( llvm_config_dict )
             self.log.info( self.__class__.__name__ + '...' + fullpath )

        def __repr__( self ) :
             """
             returns string representation and construction info
             :rtype : basestring
             :return:
             """
             return "{__class__.__name__}(fullpath={_fullpath!r},vargs_lst={_vargs!r})". \
                    format( __class__=self.__class__ , **self.__dict__ )

        def __str__( self ) :
              """
              returns pretty string
              :rtype: basestring
              :return: str
              """
              return 'cci_mini_llvm_config , 2015 , william k. johnson'

        def __bool__( self ) :
              """
              returns connected
              :rtype bool
              :return: self._db_connected
              """
              return True

        '''attributes'''
        @property
        def configs( self ) :
            return self._config_dict
        @configs.setter
        def configs( self , cf ) :
            self._config_dict = cf

        '''helpers'''
        def _atomic_config( self , config_moniker = 'version' ) :
            """
            return one config
            :param config_moniker:
            :return :config
            :rtype string
            """

            if not config_moniker in self._config_dict :
                raise llvm_config_exception( 'configuration specifier not found' )
            moniker_str = str()
            try:
                moniker_str += subprocess.check_output( [self.fullpath ,
                                                        const.config_prefix + config_moniker] )

            except subprocess.CalledProcessError as e :
                self.log.error( 'error in retrieving llvm-config atom....' )

            return moniker_str.strip( '\n' )


        def _atomic_cached_config( self , config_moniker = 'version' ) :
            """
            config from class map
            :param config_moniker:
            :return : config
            :rtype string
            """

            if not config_moniker in self._config_dict :
                raise llvm_config_exception( 'configuration specifier not found' )
            if self._config_dict[config_moniker] is None :
                raise llvm_config_exception( 'no cached config info found' )

            return self._config_dict[config_moniker]

        def _glom_configs( self ) :
            """
            all configs
            :return :
            """

            try :
                for key ,elem in self._config_dict.items() :
                    self._config_dict[key] = self._atomic_config( key )

            except llvm_config_exception as e :
                # reraise exception
                raise llvm_config_exception( e.message )


        '''services'''
        def perform( self ) :
            """
            llvm-config
            :return:
            """

            self._glom_configs()

        def cache_dump( self ) :
            """
            dump class map
            :return:
            """

            pp = pprint.PrettyPrinter( indent = 4 )
            pp.pprint( self._config_dict )

        def refresh( self ) :
            """
            remake class map
            :return:
            """
            self._config_dict = dict()
            self._config_dict = copy.deepcopy( llvm_config_dict )

            self._glom_configs()


# ------------------------------------------------------------------------
if __name__ == '__main__' :

        ostr = io.ostream_py()

        llvm_config = cci_mini_llvm_config( '/cci/dev_t/bin/llvm-config' )
        try :
            llvm_config.perform()
            llvm_config.cache_dump()
        except llvm_config_exception as e :
            llvm_config.log.error( e.message )
            ostr << e.message << const.endl



