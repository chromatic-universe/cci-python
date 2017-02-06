# cci-trinity.py  willian k. johnson p4a/python3 fork  chromatic universe 2016
# remove qpython bootstrap and dempendencies

import os
import copy
import logging
import importlib
from time import gmtime, strftime , sleep
import subprocess as proc
import threading
import socket
import datetime
from functools import partial
import requests
import signal
import kivy
from kivy.config import Config
from kivy.app import App 
from kivy.uix.widget import Widget
from kivy.uix.label import Label 
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock , mainthread
import tornado.websocket
from tornado import gen 

if platform == 'android' :
    from jnius import autoclass
    
kivy.require( '1.9.1' )

log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'
default_lib_path_2 = '/data/data/com.chromaticuniverse.cci_trinity/lib'
default_lib_2 = 'libpython2.7.so'
python_2 = 'python'
python_27 = 'python2.7'

t = 3


class ccitrinityApp( App ) :
            """
            trinity
            """

            
            
            def __init__( self ) :
                """

                :return:
                """

                super( ccitrinityApp , self ).__init__()


                # local logger
                self._logger = logging.getLogger( "cci trinity" )
                self._logger.setLevel( logging.DEBUG )
                fh = logging.FileHandler(  'trinity' + '-debug.log', mode = 'a' )
                fh.setLevel( logging.DEBUG )
                formatter = logging.Formatter( log_format )
                fh.setFormatter( formatter )
                self._logger.addHandler( fh ) 
                self._logger.info( self.__class__.__name__ + '...'  )

                self._py_link()


                self._pid = None
                self._pid_vulture = None
                self._clock_event = None
                self._init_clock_event = None

                self._retry_on_fail_reps = 0

                self._policy_thred = None
                self._trinity_socket_thred = None

                             


            def on_pause(self):
                # save data


                return True


            
            def on_resume( self ):
                # something


                pass
            


            @gen.coroutine
            def _manip_socket_stream( self ) :
                """
                :return:
                """

                socket_msg = { 'app_services' : self.root.ids.status_text ,
                               'async_services' : self.root.ids.vulture_status_text ,
                               'tunnel_services' : self.root.ids.manipulate_status_text }



                try :

                    client = yield tornado.websocket. \
                            websocket_connect( "ws://localhost:7082/trinity-stream" )
                    client.write_message("Testing from client")

                    while True :
                        msg = yield client.read_message()
                        service , payload = msg.split( ':' )                         
                        service = str( service.strip() )
                        self._update_status( socket_msg[service] , str( payload ) )

                except Exception as e :
                    self._logger.error( '..manip_socket_stream.. ' + e )




            def _trinity_update_thred( self ) :
                """

                :return:
                """

                try :
                    
                    tornado.ioloop.IOLoop.instance().run_sync( self._manip_socket_stream )

                except Exception as e :
                    self._logger.error( e )

                

            def _py_link( self ) :

                try :
                    os.symlink( '%s/%s' % ( default_lib_path_2 , default_lib_2 ) ,                    
                                './%s' % default_lib_2 )  
                    os.chmod( './%s' % python_2 , 0o755 )
                    os.chmod( './%s' % python27 , 0o755 )

                except :
                    pass
            
            

            def _pid_callback( self , dt ) :

                pid = str()
                pid_vulture = str()
                
                try :
                    with open( 'cci-trinity-pid' , 'r' ) as pidfile :
                        pid = pidfile.read().strip()
                    with open( 'cci-trinity-vulture-pid' , 'r' ) as vpidfile :
                        pid_vulture = vpidfile.read().strip()
                    self.root.ids.process_info.text = 'pid: %s   ~  port: 7080' % pid
                    self.root.ids.vulture_process_info.text = 'pid: %s   ~  port: 7081' % pid_vulture

                except :
                    pass




            def _init_callback( self , dt ) :
                 """
                 :param interval:
                 :return:
                 """
                 if not self._trinity_socket_thred :
                    self._trinity_socket_thred = threading.Thread( target = self._trinity_update_thred )
                    self._trinity_socket_thred.daemon = True
                    self._trinity_socket_thred.start()



            
            def _move_carousel( self  ) :
                """

                :return:
                """
                
                self.root.ids.trinity_carousel_id.load_next()
               

            def _on_sync_carousel( self  , args ) :
                """

                :return:
                """
                if args == 0 :
                    self.root.ids.trinity_item.title =  'cci-trinity~app services'
                elif args == 1	 :
                    self.root.ids.trinity_item.title  =  'cci-trinity~async services'
                elif args == 2 :
                    self.root.ids.trinity_item.title =  'cci-trinity~tunnel services'        



            def _running( self ) :
                """

                :return boolean:
                """
                
                running = False

                pid = None
                pid_vulture = None
                try :
                    with open( 'cci-trinity-pid' , 'r' ) as pidfile :
                        pid = pidfile.read().strip()
                    with open( 'cci-trinity-vulture-pid' , 'r' ) as v_pidfile :
                        pid_vulture = v_pidfile.read().strip()
                except :
                     pass

                # check if processes are running
                if pid and pid_vulture:
                     try :
                        running = os.path.exists( '/proc/%s' % pid )
                        self._pid = pid
                        running = os.path.exists( '/proc/%s' % pid_vulture )
                        self._pid_vulture = pid_vulture
                     except :
                        # pid not running
                        pass

                return running




            def on_start( self ) :
                """

                :return:
                """

                self._update_status( self.root.ids.status_text , '...initializing...' )
                self._update_status( self.root.ids.vulture_status_text , '...initializing...' )

                try :

                    os.chmod( './cci-bootstrap' , 0o755 )
                    os.chmod( './cci-bootstrap-v' , 0o755 )
                    
 
                    self._update_status( self.root.ids.vulture_status_text , ' ....trinity vulture/stream daemon....' )
                    with open( 'trinity_pid' , 'w' ) as f :
                        f.write( '%d' % os.getpid() )

                    if self._running() is False :

                            self.root.ids.bootstrap_switch.active = False
                            self._update_status( self.root.ids.status_text , ' ....trinity....' )
                            self._update_status( self.root.ids.vulture_status_text , ' ....trinity vulture/stream daemon....' )
                            self._update_status( self.root.ids.vulture_status_text , ' ....trinity vulture/stream daemon....' )

                    else :
                            self._update_status( self.root.ids.status_text , ' ....trinity running....' )
                            self._update_status( self.root.ids.vulture_status_text , ' ....trinity vulture/daemon running....' )
                            self.root.ids.manipulate_btn.background_color = [0,1,0,1]
                            self.root.ids.manipulate_tunnel_btn.background_color = [0,1,0,1]
                            self.root.ids.bootstrap_switch.active = True
                            self.root.ids.manipulate_btn.text = 'manipulate streams'
                            self.root.ids.manipulate_tunnel_btn.text = 'manipulate tunnels'
                            self.root.ids.process_info.text = 'pid: %s  port 7080' % self._pid
                            self.root.ids.vulture_process_info.text = 'pid: %s  port 7081' % self._pid_vulture
                            self._logger.info( '...server already running... pid %s....'  % self._pid )

                            if not self._trinity_socket_thred :
                                self._trinity_socket_thred = threading.Thread( target = self._trinity_update_thred )
                                self._trinity_socket_thred.daemon = True
                                self._trinity_socket_thred.start()
                                                                     
                       
                except Exception as e:
                       self._logger.error( '...error in  trinity server...' + e.message )
                       sys.exit( 1 )


            



            def _on_start_trinity( self , instance , value ) :
                """

                :return:
                """

                """
                if platform != 'android' :
                    self._on_start_trinity_linux()                
                else :
                """
                pid = str()
                pid_vulture = str()

                self._logger.info( '..._on_start_trinity...' )

                # start trinity
                if value == True :
                    if self._running() :
                        return

                    try :
                        self._update_status( self.root.ids.status_text , ' ....starting trinity....' )
                        b_ret = True
                        b_ret = self._bootstrap_trinity()

                        if not b_ret :
                            self._update_status( self.root.ids.status_text , ' ....trinity bootstrap failed....' )
                            return
                        else :
                            self._update_status( self.root.ids.status_text , ' ....trinity bootstrapped..running....' )
                            self.root.ids.manipulate_btn.background_color = [0,1,0,1]
                            self.root.ids.manipulate_tunnel_btn.background_color = [0,1,0,1]
                            self.root.ids.bootstrap_switch.active = True
                            self.root.ids.manipulate_btn.text = 'manipulate streams'
                            self.root.ids.manipulate_tunnel_btn.text = 'manipulate tunnels'
                            self._update_status( self.root.ids.status_text , ' ...trinity started...' )
                            self._update_status( self.root.ids.status_text , ' ...trinity vulture started...' )
                            self._update_status( self.root.ids.manipulate_status_text , ' ...no user defined tunnels...' )
                            
                            self._init_clock_event = Clock.schedule_once( self._init_callback, 15 )
                            self._clock_event = Clock.schedule_interval( self._pid_callback, 2 )

                    except Exception as e :
                            self._logger.error( '..._on_start_trinity...%s' % e.message )
                            self._update_status( self.root.ids.status_text , e.message )
                else :
                   
                    pid = str()
                    pid_vulture = str()

                    b_ret = False

                    try :
                        with open( 'cci-trinity-pid' , 'r' ) as pidfile :
                           pid = pidfile.read().strip()
                        self._pid = pid
                        with open( 'cci-trinity-vulture-pid' , 'r' ) as pidfile :
                           pid_vulture = pidfile.read().strip()
                    except :
                        return b_ret

                    try :
                         # kill trinity                                                                                 
                        os.kill( int( pid ) , signal.SIGTERM )                                                         
                        self._update_status( self.root.ids.status_text , ' ....trinity server stopped ....' )          
                        os.kill( int( pid_vulture ) , signal.SIGTERM )                   
                        self._update_status( self.root.ids.status_text , ' ....trinity vulture server stopped ....' )  
                        self.root.ids.manipulate_btn.background_color = [1,0,0,1]
                        self.root.ids.manipulate_tunnel_btn.background_color = [1,0,0,1]
                        self.root.ids.bootstrap_switch.active = False
                        self.root.ids.manipulate_btn.text = '~'
                        self.root.ids.manipulate_tunnel_btn.text = '~'
                        if self._clock_event :
                            self._clock_event.cancel()
                        self.root.ids.process_info.text = 'port: 7080'
                        self.root.ids.vulture_process_info.text = 'port: 7081'

                       
                        b_ret = True
                    
                    except OSError as e :    
                        
                        self._logger.error( 'kill server failed...%s' % e.strerror )
                        self._update_status( self.root.ids.status_text , ' ...kill server failed...' + e.message )

        




            def _kill_trinity( self ) :

                """

                :return:
                """

                pid = str()
                pid_vulture = str()

                b_ret = False

                try :
                    with open( 'cci-trinity-pid' , 'r' ) as pidfile :
                       pid = pidfile.read().strip()
                    self._pid = pid
                    with open( 'cci-trinity-vulture-pid' , 'r' ) as pidfile :
                       pid_vulture = pidfile.read().strip()
                except :
                    return b_ret

                try :
                    # kill trinity
                    os.kill( int( pid ) , signal.SIGTERM )
                    self._update_status( self.root.ids.status_text , ' ....trinity server stopped ....' )
                    os.kill( int( pid_vulture ) , signal.SIGTERM )
                    self._update_status( self.root.ids.status_text , ' ....trinity vulture server stopped ....' )


                    self.root.ids.bootstrap_btn.background_color = [0,1,0,1]
                    self.root.ids.manipulate_btn.background_color = [1,0,0,1]
                    self.root.ids.manipulate_tunnel_btn.background_color = [1,0,0,1]
                    self.root.ids.bootstrap_btn.text = 'start trinity'
                    self.root.ids.manipulate_btn.text = '~'
                    self.root.ids.manipulate_tunnel_btn.text = '~'
                    if self._clock_event :
                        self._clock_event.cancel()
                    self.root.ids.process_info.text = 'port: 7080'
                    self.root.ids.vulture_process_info.text = 'port: 7081'

                    b_ret = True
                
                except OSError as e :    
                    
                    self._logger.error( 'kill server failed...' + e.strerror )
                    self._update_status( self.root.ids.status_text , ' ...kill server failed...' + e.message )

    
                

            def _on_start_trinity_linux( self ) :
                """

                :return:
                """

                self._update_status( self.root.ids.status_text , '..platform is linux...' )




            
            def _bootstrap_trinity( self ) :
                """

                :return:
                """

                b_ret = False
                try :
                        if platform == 'android' :   
                            bootstrap_path = "/data/data/com.chromaticuniverse.cci_trinity/files/app"
                            trinity_cmd = "%s/%s" % ( bootstrap_path , "cci-bootstrap" )
                            async_cmd = "%s/%s" % ( bootstrap_path , "cci-bootstrap-v" )
                        else :
                            bootstrap_path = os.getcwd()
                            trinity_cmd = "/usr/bin/python %s/cci_trinity.py &" % bootstrap_path
                            async_cmd = "/usr/bin/python %s/cci_trinity_async.py &" % bootstrap_path
                        try :
                           
                            self._logger.info( '...bootstrap...' )
                            ret = os.system( trinity_cmd )
                            if ret != 0 :
                                raise OSError( "..fork system app server failed..." )
                            self._update_status( self.root.ids.status_text , '..cci_trinity_service started...' )
                            self._update_status( self.root.ids.vulture_status_text ,  '..cci_trinity_service started...' )
                            os.system( async_cmd )
                            if ret != 0 :
                                raise OSError( "..fork system call async server failed..." )
                            self._update_status( self.root.ids.status_text , '..cci_async_service started...' )
                            self._update_status( self.root.ids.vulture_status_text ,  '..cci_async_ervice started...' )

                           
                            b_ret = True
                        except proc.CalledProcessError as e:
                            self._logger.error( 'bootstrap failed...' + e.message ) 
                        except OSError as e :
                            self._logger.error( 'file does not exist?...' + e.message )
                        except ValueError as e :
                            self._logger.error( 'arguments foobar...' + e.message )
                        except Exception as e :
                            self._logger.error(  e.message )
                                              

                except Exception as e :
                    self._logger.error(  '...error in  trinity server...'  + e.message )    


                return b_ret

           



            @staticmethod
            @mainthread
            def _update_status( container , status ) :
                """

                :param status:
                :return:
                """
                timestamp = 'cci-trinity~ {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
                container.text = timestamp + status + '\n' + container.text






if __name__ == '__main__': 

            Config.set('graphics','resizable',0 )


            Config.set( 'graphics', 'width', '480' )
            Config.set( 'graphics', 'height', '800' )
            Config.set( 'input', 'mouse', 'mouse,disable_multitouch' )


            #from kivy.core.window import Window

            Window.size = ( 480 , 825 )
            ct = ccitrinityApp()
            ct.run()

