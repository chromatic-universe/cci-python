# cci-trinity.py  willian k. johnson p4a/python3 fork  chromatic universe 2016
# remove qpython bootstrap and dependencies



import sys
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
import json
import sqlite3
import paramiko

import kivy
from kivy.config import Config
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix import image
from kivy.core.window import Window
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.treeview import TreeView , TreeViewLabel , TreeViewNode
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.config import ConfigParser
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock , mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.settings import SettingsWithSidebar , SettingsWithSpinner
from kivy.utils import platform


# cci
from streams import tr_utils , \
	                sshtunnel


kivy.require( '1.9.1' )

log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'

t = 3


# -------------------------------------------------------------------------------------------------
class ConsolePopup( Popup  ) :
				"""

				"""
				def on_press_dismiss( self , *args) :

					self.dismiss()

					return False


				def on_press_context( self , *args) :

					self.dismiss()

					return False


				def on_dismiss( self ) :
					pass





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
				# params
				self._db_path = self._retrieve_default_db_path()
				self._stream_bootstrap = None
				try :
					j = json.loads( self._retrieve_config_atom( 'trinity-stream-toggle' )['map'] )
				except :
					self._logger.error( '..could not load trinity-stream-toggle' )
				logger = None
				lname = 'cci_trinity-' + tr_utils.local_mac_addr()

				self._pid = None
				self._pid_vulture = None
				self._clock_event = None
				self._retry_on_fail_reps = 0

				self._policy_thred = None




			@mainthread
			def _enum_policy_record( self , jsn , moniker ) :
				"""

				:param jsn json:
				:return:
				"""
				if jsn is None :
					return

				s = '\n\n' + 24 * '*'
				header = 'default %s policy' % moniker
				s += '\n' + header + '\n'
				s += 24 * '*'
				s += '\n'
				for key , value in jsn.iteritems() :
					s += '%s = %s\n' % ( key , value )
				self._update_status( self.root.ids.vulture_status_text ,
									 '...default %s policy initialized....%s' % ( moniker , s ) )




			def _start_policy_thred( self ) :
				"""

				:param sself:
				:return:
				"""
				# start default document policy
				try :
					j = self._default_policy( True , 'document')
					self._enum_policy_record( j , 'document' )
					j = self._default_policy( True , 'stream')
					self._enum_policy_record( j , 'stream' )
					self._update_status( self.root.ids.status_text ,
									 '..policies initialized..check streams for details.' )

				except Exception as e :
					self._update_status( self.root.ids.status_text ,
										 '...policy initialization failed..check aysnc services for details' )




			def _start_policy_callback( self , dt ) :
						"""

						give vulture server time to initialize

						:return:
						"""

						# start default document policy
						self._policy_thred = threading.Thread( target = self._start_policy_thred ).start()





			def on_stop( self ) :
						"""

						:return:
						"""


						if self._policy_thred :
							self._policy_thred.join( timeout = 2 )




			def on_start(self) :
						"""

						:return:
						"""


						self._update_status( self.root.ids.status_text , '...initializing...' )
						self._update_status( self.root.ids.vulture_status_text , '...initializing...' )


						is_running = False
						try :

                             with open( 'trinity_pid' , 'w' ) as f :
                                 f.write( os.getpid() )
							 pid = None
							 pid_vulture = None
							 try :
								 with open( 'pid' , 'r' ) as pidfile :
									pid = pidfile.read().strip()
								 with open( 'pid_vulture' , 'r' ) as v_pidfile :
									pid_vulture = v_pidfile.read().strip()
							 except :
								 pass

							 # check if processes are running
							 if pid and pid_vulture:
								 try :
									# throws exception if process doesn't exist
									is_running = os.path.exists( '/proc/%s' % pid )
									self._pid = pid
									is_running = os.path.exists( '/proc/%s' % pid_vulture )
									self._pid_vulture = pid_vulture
								 except :
									# pid not running
									pass

							 if is_running is False :


								self.root.ids.bootstrap_btn.background_color = [0,1,0,1]
								self.root.ids.bootstrap_btn.text = 'start trinity'
								self._update_status( self.root.ids.status_text , ' ....trinity....' )
								self._update_status( self.root.ids.vulture_status_text , ' ....trinity vulture/stream daemon....' )

								"""
								 # wrqputite pid
								 with open( 'pid' , 'w' ) as pidfile :
									 pidfile.write( str( os.getpid() ) + '\n'  )
								 # start server
								 IOLoop.instance().start()
								"""

							 else :
									self._update_status( self.root.ids.status_text , ' ....trinity running....' )
									self._update_status( self.root.ids.vulture_status_text , ' ....trinity vulture/daemon running....' )
									self.root.ids.bootstrap_btn.background_color = [1,0,0,1]
									self.root.ids.manipulate_btn.background_color = [0,1,0,1]
									self.root.ids.bootstrap_btn.text = 'stop trinity'
									self.root.ids.manipulate_btn.text = 'manipulate streams'
									self.root.ids.process_info.text = 'pid: %s  port 7080' % self._pid
									self._logger.info( '...server already running... pid %s....'  % self._pid )





						except Exception as e:
							_logger.error( '...error in  trinity server...' + e.message )
							sys.exit( 1 )




			# android mishegas
			def on_pause(self):
				# save data


				return True



			def on_resume( self ):
				# something


				pass



			def _debug_log_snippet( self ) :
				"""

				:return:
				"""

				try :

					cmd = [ 'tail' ,
							'-n' ,
							'10' ,
							'cci-trinity-server.log-debug.log'
						   ]
					return proc.check_output( cmd )
				except proc.CalledProcessError as e:
					self._logger.error( '..._debug_log_snippet...' + e.message )



			@staticmethod
			@mainthread
			def _update_status( container , status ) :
				"""

				:param status:
				:return:
				"""
				timestamp = 'cci-trinity~ {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
				container.text = timestamp + status + '\n' + container.text



			# ----------------------------------------------------------------------------------------------------
			def _retrieve_config_atom( self , atom ) :
					"""

					:param atom:
					:return:
					"""

					json_row = None
					try :

						self._logger.info( '...retrieve_config_atom ...' )
						con = sqlite3.connect( self._db_path )
						con.row_factory = tr_utils.dict_factory
						cur = con.cursor()

						s =  'select map from metadata_config ' \
							 'where moniker = "%s" '  %  atom
						cur.execute( s )

						json_row = cur.fetchone()
						if json_row is not None :
							self._logger.info( '...retrieved config map for ...%s' % atom )
						else :
							self._logger.error( '...could not retrieve atom for %s...' % atom )
					except sqlite3.OperationalError as e :
						self._logger.error( '...retrieve_policy statement failed...%s' , e.message )


					return json_row




			def _retrieve_default_db_path( self ) :
					"""

					:return string db_path:
					"""
					db_path = None
					try :

						with open( 'bootstrap_db' , 'r' ) as f :
							db_path = f.read().strip().split( '=' )[1]
							db_path.lstrip()

					except Exception as e :
						self._logger.error( '...retrieve_default_db_path failed...%s' , e.message )


					return db_path




			def _retrieve_policy(  self , policy_moniker , provider_type ) :
					"""

					:param policy_moniker:
					:param provider_type:
					:return:
					"""

					json_row = None
					try :

						self._logger.info( '...retrieve payload_policy ...' )
						s =  '/data/media/com.chromaticuniverse.cci_trinity/king_console.sqlite'
						con = sqlite3.connect( self._db_path )
						con.row_factory = tr_utils.dict_factory
						cur = con.cursor()

						s =  'select * from payload_policy ' \
							 'where moniker = "%s" '  \
							 'and provider_type = "%s" ' \
							 'and active = 1'  % ( policy_moniker , provider_type )
						cur.execute( s )

						json_row = cur.fetchone()
						if json_row is not None :
							self._logger.info( '...retrieved default policy...%s' % json.dumps( json_row ) )
						else :
							self._logger.error( '...could not retrieve default policy...' )
					except sqlite3.OperationalError as e :
						self._logger.error( '...retrieve_policy statement failed...%s' , e.message )


					return json_row




			def _default_policy( self  , toggle , policy_type = None ) :
				"""

				:return:
				"""

				jsn = None
				try :
					jsn = self._retrieve_policy(  'default' , policy_type )
					if int( jsn['active'] ) :
						# start default policy
						self._toggle_policy( jsn , toggle )
				except Exception as e :
					self._logger.info( '..exception..'  % e.message )
					return None


				return jsn
			
			
			




			def _retry_toggle_policy_callback( self , jsn , toggle , * largs ) :
				"""

				:param json:
				:param toggle:
				:param largs:
				:return:
				"""

				try :
					self._toggle_policy( jsn , toggle )
					s = '..toggle policy retry succeeded..default policy initialized'
					self._update_status( self.root.ids.vulture_status_text , s )
					self._update_status( self.root.ids.status_text , s )

					jsn = self._retrieve_policy(  'default' , 'document' )
					self._enum_policy_record( jsn , 'document' )
					jsn = self._retrieve_policy(  'default' , 'stream' )
					self._enum_policy_record( jsn , 'stream' )



				except Exception as e :
					s = '..toggle policy failed...no more retries  %s..' % e.message
					self._logger.error( s )
					self._update_status( self.root.ids.vulture_status_text , s )
					self._update_status( self.root.ids.status_text , s )
					raise Exception( '..failure...' )



			def _toggle_policy( self , jsn , toggle ) :
				"""

				:param json dictionary:
				:toggle boolean:
				:return:
				"""

				try :

					data = { 'moniker' : jsn['moniker'] ,
							 'provider_type' : jsn['provider_type'] ,
							 'interval' : str( jsn['run_interval'] ) ,
							 'db_bootstrap' : '/data/media/com.chromaticuniverse.cci_trinity/king_console.sqlite'
						   }

					if toggle :
						ps = 'start'
					else :
						ps = 'stop'
					s = 'http://localhost:7081/trinity-vulture/%s' % ps
					r = requests.post( s ,
									   data = json.dumps( data ) )
					if r.status_code != 200 :
						raise( '...post policy %s %s start failed...' % ( jsn['moniker'] , jsn['provider_type'] ) )
					self._logger.info( '...post policy succeeded for %s %s...' % ( jsn['provider_type'] , jsn['provider_type'] ) )

				except Exception as e :
					if self._retry_on_fail_reps :
						return
					s = '..toggle policy failed....retrying in 8 seconds %s..' % e.message
					self._logger.error( s )
					self._update_status( self.root.ids.vulture_status_text , s )
					self._retry_on_fail_reps += 1

					Clock.schedule_once( partial( self._retry_toggle_policy_callback , jsn , toggle ) , 5 )
					raise Exception( '..failure...' )



			def _on_start_trinity( self ) :
				"""

				:return:
				"""

				pid = str()
				pid_vulture = str()

				self._logger.info( '..._on_start_trinity...' )

				# start trinity
				if self.root.ids.bootstrap_btn.text == 'start trinity' :
					try :
						self._update_status( self.root.ids.status_text , ' ....starting trinity....' )

						b_ret = self._bootstrap_trinity()

						if not b_ret :
							self._update_status( self.root.ids.status_text , ' ....trinity bootstrap failed....' )
							return
						else :
							self._update_status( self.root.ids.status_text , ' ....trinity bootstrapped..running....' )
							self.root.ids.bootstrap_btn.background_color = [1,0,0,1]
							self.root.ids.manipulate_btn.background_color = [0,1,0,1]
							self.root.ids.manipulate_tunnel_btn.background_color = [0,1,0,1]
							self.root.ids.bootstrap_btn.text = 'stop trinity'
							self.root.ids.manipulate_btn.text = 'manipulate streams'
							self.root.ids.manipulate_tunnel_btn.text = 'manipulate tunnels'
							self._update_status( self.root.ids.status_text , ' ...trinity started...' )
							self._clock_event = Clock.schedule_interval( self._pid_callback, 2 )
					except Exception as e :
						self._logger.error( '..._on_start_trinity...' + e.message )
						self._update_status( self.root.ids.status_text , e.message )

					# start trinity vulture
					try :
						self._update_status( self.root.ids.status_text , ' ....starting trinity vulture....' )
						self._update_status( self.root.ids.vulture_status_text , ' ....starting trinity vulture....' )
						b_ret = self._bootstrap_trinity_vulture()

						if not b_ret :
							self._update_status( self.root.ids.status_text , ' ....trinity vulture bootstrap failed....' )
						else :

							self._update_status( self.root.ids.status_text , ' ....trinity vulture bootstrapped..running....' )
							self.root.ids.bootstrap_btn.background_color = [1,0,0,1]
							self.root.ids.manipulate_btn.background_color = [0,1,0,1]
							self.root.ids.manipulate_tunnel_btn.background_color = [0,1,0,1]
							self.root.ids.bootstrap_btn.text = 'stop trinity'
							self.root.ids.manipulate_btn.text = 'manipulate streams'
							self.root.ids.manipulate_tunnel_btn.text = 'manipulate tunnels'
							self._update_status( self.root.ids.status_text , ' ...trinity vulture started...' )
							self._update_status( self.root.ids.vulture_status_text , ' ...trinity vulture started...' )
							self._update_status( self.root.ids.vulture_tunnel_text , ' ...no user defined tunnels...' )

							# schedule default policies to start in 8 seconds
							self._update_status( self.root.ids.status_text ,
												 '..waiting for async server to initialize polocies...standby..' )
							Clock.schedule_once( self._start_policy_callback , 5 )

					except Exception as e :
						self._logger.error( '..._on_start_trinity...vulture' + e.message )
						self._update_status( self.root.ids.status_text , e.message )


				else :
					try :
						try :
							 with open( 'pid' , 'r' ) as pidfile :
								pid = pidfile.read().strip()
							 self._pid = pid
							 with open( 'pid_vulture' , 'r' ) as pidfile :
								pid_vulture = pidfile.read().strip()
						except :
							 pass

						try :
							pos = sys.platform.find( 'linux4' )
							cmd = list()
							if pos == -1 :
								andr = False
							else :
								andr = True

							# kill trinity
							if platform == 'android':
								cmd = ['su' ,
									   '-c' ,
									   'kill' ,
									   '-9' ,
									   pid]
							else :
								cmd = ['kill' ,
									   '-9' ,
									   pid]

							proc.check_output( cmd )
							self._update_status( self.root.ids.status_text , ' ....trinity server stopped ....' )
							# kill trinity-vulture
							if platform == 'android':
								cmd = ['su' ,
									   '-c' ,
									   'kill' ,
									   '-9' ,
									   pid_vulture]
							else :
								cmd = ['kill' ,
									   '-9' ,
									   pid_vulture]
							proc.check_output( cmd )
							self._update_status( self.root.ids.status_text , ' ....trinity vulture stopped ....' )
							self._update_status( self.root.ids.vulture_status_text , ' ....trinity vulture stopped ....' )
							self.root.ids.bootstrap_btn.background_color = [0,1,0,1]
							self.root.ids.manipulate_btn.background_color = [1,0,0,1]
							self.root.ids.manipulate_tunnel_btn.background_color = [1,0,0,1]
							self.root.ids.bootstrap_btn.text = 'start trinity'
							self.root.ids.manipulate_btn.text = '~'
							if self._clock_event :
								self._clock_event.cancel()
							self.root.ids.process_info.text = 'port: 7080'
							self.root.ids.vulture_process_info.text = 'port: 7081'
						except proc.CalledProcessError as e:
							self._logger.error( 'kill server failed...' + e.message )
							self._update_status( self.root.ids.status_text , ' ...kill server failed...' + e.message )

					except Exception as e :
						self._logger.error( '..._on_stop_trinity...' + e.message )
						self._update_status( self.root.ids.status_text , e.message )





			def _pid_callback( self , dt ) :
					pid = str()

					with open( 'pid' , 'r' ) as pidfile :
						pid = pidfile.read().strip()
					with open( 'pid_vulture' , 'r' ) as vpidfile :
						pid_vulture = vpidfile.read().strip()
					self.root.ids.process_info.text = 'pid: %s   ~  port: 7080' % pid
					self.root.ids.vulture_process_info.text = 'pid: %s   ~  port: 7081' % pid_vulture






			def _bootstrap_trinity( self ) :
						"""

						:return:
						"""

						# another process ont that port?
						#

						b_ret = False

						try:
							s = socket.socket()
							s.setsockopt( socket.SOL_SOCKET , socket.SO_REUSEADDR , 1 )
							s.bind( ( socket.gethostname()  , 7080 ) )
						except socket.error as e:
							self._logger.error(  '..bootstrap failed...errno:%d...%s' % ( e[0] , e[1] ) )
							return


						pid = str()
						try :

								self._logger.info( "...bootstrapping cci_trinity....." )
								cmd = list()

								if platform == 'android':
									cmd = [
									  "su" ,
									  "-c" ,
									  "/data/data/com.hipipal.qpyplus/files/bin/qpython.sh" ,
									  "./cci_trinity.pyo" ,
									  "&"
									  ]
								else :
									cmd = [
									  "python" ,
									  "./cci_trinity.py" ,
									  "&"
									  ]


								proc.Popen( cmd )
								self._logger.info( "...made proc call....." )


								try:
									s = socket.socket()
									s.setsockopt( socket.SOL_SOCKET , socket.SO_REUSEADDR , 1 )
									s.bind( ( socket.gethostname()  , 7080 ) )
									b_ret = True
									self._logger.info( "bootstrapped cci_trinity....." )
								except socket.error as e:
									self._logger.info( "failed tp bootstrap cci_trinity....." )
									b_ret = False




						except proc.CalledProcessError as e:
							self._logger.error( 'bootstrap failed...' + e.message )
						except OSError as e :
							self._logger.error( 'file does not exist?...' + e.message )
							#sys.exit( 1 )
						except ValueError as e :
							self._logger.error( 'arguments foobar...' + e.message )
							#sys.exit( 1 )
						except Exception as e :
							self._logger.error(  e.message )
							#sys.exit( 1 )

						return b_ret




			def _bootstrap_trinity_vulture( self ) :
						"""

						:return:
						"""
						b_ret = False

						try :

								self._logger.info( "...bootstrapping cci_trinity_vulture....." )
								pos = sys.platform.find( 'linux4' )
								if pos == -1 :
									andr = False
								else :
									andr = True
								cmd = list()


								if platform == 'android':
									cmd = [
									  "su" ,
									  "-c" ,
									  "/data/data/com.hipipal.qpyplus/files/bin/qpython.sh" ,
									  "./cci_trinity_async.pyo" ,
									  "&"
									  ]
								else :
									cmd = [
									  "python" ,
									  "./cci_trinity_async.py" ,
									  "&"
									  ]



								proc.Popen( cmd )

								try:
									s = socket.socket()
									s.setsockopt( socket.SOL_SOCKET , socket.SO_REUSEADDR , 1 )
									s.bind( ( socket.gethostname()  , 7081 ) )
									b_ret = True
									self._logger.info( "bootstrapped cci_trinity_vulture....." )
								except socket.error as e:
									self._logger.info( "failed tp bootstrap cci_vulture_async....." + e.message  )
									b_ret = False



						except proc.CalledProcessError as e:
							self._logger.error( 'bootstrap failed.async..' + e.message )
						except OSError as e :
							self._logger.error( 'async file does not exist?...' + e.message )
							#sys.exit( 1 )
						except ValueError as e :
							self._logger.error( 'arguments foobar in async ...' + e.message )
							#sys.exit( 1 )
						except Exception as e :
							self._logger.error(  e.message )
							#sys.exit( 1 )

						return b_ret



			def _move_carousel( self  ) :
						"""

						:return:
						"""

						if self.root.ids.packet_stream_btn.text ==  'aysnc services' :
							self.root.ids.trinity_carousel_id.load_next()
							self.root.ids.packet_stream_btn.text = 'tunnel services'
						elif self.root.ids.packet_stream_btn.text ==  'tunnel services'  :
							self.root.ids.trinity_carousel_id.load_next()
							self.root.ids.packet_stream_btn.text = 'app server'
						else :
							self.root.ids.packet_stream_btn.text = 'aysnc services'
							self.root.ids.trinity_carousel_id.index = 0



			def _on_sync_carousel( self  , args ) :
						"""

						:return:
						"""


						if args == 0 :
							self.root.ids.packet_stream_btn.text =  'aysnc services'
						elif args == 1	 :
							self.root.ids.packet_stream_btn.text =  'tunnel services'
						elif args == 2 :
							self.root.ids.packet_stream_btn.text =  'app server'

						pass





			# attributes
			@property
			def logger( self ) :
				return self._logger
			@logger.setter
			def logger( self , log ) :
				self._logger = log




if __name__ == '__main__':

			Config.set('graphics','resizable',0 )


			Config.set( 'graphics', 'width', '480' )
			Config.set( 'graphics', 'height', '800' )
			Config.set( 'input', 'mouse', 'mouse,disable_multitouch' )


			#from kivy.core.window import Window

			Window.size = ( 480 , 800 )
			ct = ccitrinityApp()
			ct.run()




