# cci_aws_meta_bot.py willliam k. johnson 2016


import os
import sys
#############
import doctest
import unittest
from sets import Set
from abc import abstractmethod , ABCMeta
import copy
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
##############
import requests
import logging
import argparse
import subprocess as proc
##############

##############
import cci_utils.cci_io_tools as io
from cci_stream_inf import cci_stream_intf
import cci_utils.cci_constants as const

##############
import boto3


const.ec2 = 'ec2'
const.instances = 'instances'
const.security_groups = 'security_groups'
const.net_interfaces = 'net_interfaces'
const.volumes = 'volumes'
const.aws_cli_dump = ['aws' , 'ec2' , 'describe-instances' , '--profile']
aws_output_t = Set( ['text', 'table' ,'json'] )



# cli callback----------------------------------------------------------------------------------
def stream_version( ctx , param , value ) :
    if not value or ctx.resilient_parsing :
        return
    click.echo( click.style( 'cci_aws_meta_bot version 0.8  william k. johnson 2016' ,
                             fg='green') )
    ctx.exit()


# ------------------------------------------------------------------------------
class cci_mini_aws_bot( cci_stream_intf ) :
        """
        minimal wrapper for boto3 and aws cli
        """


        def __init__( self ,
                      domain_accounts=None ,
                      use_default = True ,
                      out_format = 'table' ) :


            super( cci_mini_aws_bot , self ).__init__()

            self._logger = io.init_logging( self.__class__.__name__  )
            self._logger.info( self.__class__.__name__ + '...'  )
            self._current_profile = str()
            self._out_format = out_format

            if domain_accounts :
                if use_default :
                    if 'default' in domain_accounts :
                        self._boto_session = boto3.Session( profile_name = domain_accounts['default'] )
                else :
                        self._boto_session = domain_accounts[0]
                self._current_profile = self._boto_session.profile_name
                self._ec2 = self._boto_session.resource( const.ec2 )
            self._domain_accounts = domain_accounts
            self._lines = []
            self._buffer = str()


        # -----------------------------------------------------------------------
        def call_and_listen( self , command_line ) :
                """
                execute subprocess and listen for
                return buffer

                :param command_line:
                :return:
                """

                output = StringIO()
                output.write( proc.check_output( command_line ).decode() )

                return output

        # ------------------------------------------------------------------------
        def enum_profile_metadata( self , ec2 = None) :
                """
                enumerate profile metadata

                :param: ec2 instance
                :return:
                """

                instance_dict = {}

                if ec2 :
                        instance_dict[const.instances]  = ec2.instances.all()
                        instance_dict[const.security_groups]  = ec2.security_groups.all()
                        instance_dict[const.net_interfaces]  = ec2.network_interfaces.all()
                        instance_dict[const.volumes]  = ec2.volumes.all()

                return instance_dict


        # -------------------------------------------------------------------------
        def _default_output_handler( self , output ) :
                """
                default process stream handler
                :param output : stream
                :return:
                """
                print( output )


        # -------------------------------------------------------------------------
        def output_to_list_handler( self , output ) :
                """
                html out

                :param output:
                :return:
                """
                self._lines = output.split( '\n' )


        # -------------------------------------------------------------------------
        def output_to_buffer_handler( self , output ) :
                """
                html out

                :param output:
                :return:
                """
                self._buffer = output


        # -------------------------------------------------------------------------
        def enum_all_profiles( self ) :
                """
                enumerate all profiles

                :return:
                """

                profile_metadata_dictionary = {}

                for profile in self._domain_accounts :
                    session = boto3.Session( profile_name = self._domain_accounts[profile] )
                    profile_metadata_dictionary[profile] = self.enum_profile_metadata( session.resource( const.ec2 ) )

                return profile_metadata_dictionary

        # -------------------------------------------------------------------------
        def enum_instance_info( self , instance_id = None ) :
                """
                enumerate instance info

                :param instance_id:
                :return:
                """

                instance_metadata_dictionary = {}

                return instance_metadata_dictionary


        # -------------------------------------------------------------------------
        def aws_cli_display_dump( self ,
                                  profile = 'default' ,
                                  out_func = None) :
                """
                use subprocess of aws cli to describe
                instance for display. assumes profile accounts have
                been configured on local host. boto3 is
                too byzantine for something this straightforward.

                :param profiles: list
                :param:out_format : string
                :return:
                """

                output = None

                if not self._out_format in aws_output_t :
                    raise ValueError( 'unrecognized output format' )

                command_line = copy.deepcopy( const.aws_cli_dump )
                command_line.append( profile )
                command_line.append( '--output' )
                command_line.append( self._out_format )

                try :

                    # subprocess call , checks return value of process and returns output
                    # output is returned as byte array and needs to be decoded to utf-8
                    output = StringIO()
                    output.write( proc.check_output( command_line ).decode() )
                    if out_func is None :
                        self._default_output_handler( output.getvalue() )
                    else :
                        out_func( output.getvalue() )

                except proc.CalledProcessError as e :
                    self._logger.error( e.message )
                finally :
                    output.close()

        @property
        def ec2( self ) :
            return self._ec2
        @ec2.setter
        def ec2( self , service ) :
            self._ec2 = service
        @property
        def logger( self ) :
            return self._logger
        @logger.setter
        def logger( self , log ) :
            self._logger= log
        @property
        def lines( self ) :
            return self._lines
        @lines.setter
        def lines( self , li ) :
            self._lines = li
        @property
        def buffer( self ) :
            return self._buffer
        @buffer.setter
        def buffer( self ,buf ) :
            self._buffer = buf



# ------------------------------------------------------------------------
if __name__ == '__main__' :


        ostr = io.ostream_py()
        accounts = {'default' : 'default' , 'cci-aws-2' : 'aws2' }

        try :

            aws = cci_mini_aws_bot()
            # profile_metadata = aws.enum_all_profiles()
            aws.aws_cli_display_dump( out_func=aws.output_to_buffer_handler )
            print aws.buffer
            # print profile_metadata
            #context = click.get_current_context()

        except IOError as e :
            ostr << 'IO error ' << e.message << const.endl
        except Exception as e:
            ostr << 'error:' + e.message << const.endl
