__author__ = 'william k. johnson 2015'

# cci_mini_diag.py

import os
import subprocess
import argparse
import clang.cindex as clang


from cci_mini_interface import *
import cci_utils.cci_io_tools as io
import cci_utils.cci_constants as const

const.cxx = '-std=c99'
const.cpp = '-std=c++11'

# ------------------------------------------------------------------------
"""
when passing args to the libclang library , be aware that this is an extern "C"
interface. libclang has no knowledge of c++ headers. you may or may not have to
pass them in the vargs list. Also be aware of mishegas and goofosity with standard
C headers due to the fact that clang has its own eccentric method for locating them.
if you get errors about limits.h or stdarg.h not found you'll have to explicitly
pass the clang include directory with the args. we set the libclang path explicitly.
"""

class cci_mini_diag( cci_mini_clang_tool ) :

        """
        small utility class to expose libclang diagnostics
        """

        '''object model'''
        def __init__( self ,
                      fullpath = None ,
                      vargs_lst = None ,
                      raise_bool = True ,
                      clang_lib_path = '/usr/lib' ) :

           super( cci_mini_diag , self).__init__( fullpath , vargs_lst , raise_bool , clang_lib_path )
           self._config = clang.Config()
           self._config.set_library_file( clang_lib_path + '/libclang.so')
           self.log.info( 'using clang library at ' + self._clang_lib_path  )

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
              return 'cci_mini_diag , 2015 , william k. johnson'

        def __bool__( self ) :
              """
              returns connected
              :rtype bool
              :return: self._db_connected
              """
              return True

        '''services'''
        def prepare( self ) :
            """
            prepare
            :return:
            """
            if self._connection is not None :
                self.connect()

        def perform( self ) :
            """
            retrieve diagnostics for full_path
            :return:
            """
            try :

                if self.fullpath is None:
                    self.log.error(  'no file specified for diagnosis...' )
                    return

                # create clang index
                clang_index = clang.Index.create()
                if clang_index is not None :
                    self.log.info( 'created clang index......' + self.fullpath + '...' )
                    # create translation unit
                    trans_unit = clang.TranslationUnit.from_source(
                                                                    self.fullpath ,
                                                                    self._vargs ,
                                                                    None ,
                                                                    0
                                                                  )
                    if trans_unit is not None :
                        # retrieve diagnostic count
                        self.log.info( 'created translation unit....' )
                        # get diag info
                        ostr = io.ostream_py()
                        for diagnostic in trans_unit.diagnostics :
                            ostr << '\tseverity : ' << diagnostic.severity << const.endl
                            ostr << '\tline : ' << diagnostic.location << const.endl
                            ostr << '\tmessage : ' << diagnostic.spelling << const.endl
                            ostr.output.flush()

            except clang.TranslationUnitLoadError as e:
                self.log.error( 'error in creating translation unit ' + e.message )
            except Exception as e:
                self.log.error( 'error in creating translation unit ' + e.message )
            finally :
                pass

# ------------------------------------------------------------------------
class cci_clang_tools_daemon( Daemon ) :

        """
        utility wrapper for daemon facility
        """
        def __init__( self , pidfile , class_name , **kwargs ) :

            # daemon upcall
            super( cci_clang_tools_daemon , self ).__init__( pidfile )
            # transmogrify our runtime class
            self._cname = globals() [class_name]
            # unpack the runtime class args
            self._arg_str  = str()
            for key, value in kwargs.iteritems() :
                temp = "%s=%s" % ( key , value )
                self._arg_str += temp
                self._arg_str += ' '
            self._arg_str.strip()

        def run( self ) :
            """
            daemon loop
            :return:
            """
            # instantiate runtime class
            runtime_class = self._cname( self._arg_str )
            # call any abstract methods
            runtime_class.prepare()
            runtime_class.perform()

# ------------------------------------------------------------------------
if __name__ == '__main__' :

        ostr = io.ostream_py()
        # include source root , repo include , pseudo compile objects and assembly
        # only , c++ semantics , c++11 standard lib
        v_args = ['-I./' ,
                  '-I../../include' ,
                  '-I/usr/lib/3.4/clang' ,
                  '-c',
                  '-x' ,
                  'c++' ,
                  '-std=c++11'
                 ]

        try :
            cci = cci_mini_diag(
                                 # file from wherever
                                 fullpath = '/cci/cci_src/master/git_repo_1/python/cci_llvm_clang/foo.cpp' ,
                                 vargs_lst = v_args ,
                                 clang_lib_path = '/cci/dev_t/lib'
                               )
            cci.prepare()
            cci.perform()
            cci.log.info( 'completed diagnosis...' )
        except IOError as e :
            ostr << 'IO error ' << e.message << const.endl
        except Exception as e:
            ostr << e.message << const.endl







