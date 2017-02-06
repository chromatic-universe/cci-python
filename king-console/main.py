

import sqlite3

# kivy
import kivy
from kivy.utils import platform
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.carousel import Carousel
from kivy.config import Config
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix import image
from kivy.core.window import Window
from kivy.uix.actionbar import ActionButton , ActionBar
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
from kivy.utils import platform
from kivy.lang import Builder
from kivy.base import EventLoop
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.settings import SettingsWithSidebar , SettingsWithSpinner
from kivy.uix.screenmanager import ScreenManager, \
	                               Screen ,\
	                               RiseInTransition ,\
								   SwapTransition , \
								   FallOutTransition , \
								   SlideTransition
Window.softinput_mode = 'pan'

# python standard
import os
import copy
import logging
import importlib
from time import gmtime, strftime , sleep
import datetime
import subprocess as proc
import threading
import requests
import base64
import urllib2
from functools import partial
from kivy.utils import platform
import sqlite3
import Queue
import uuid
import json

if platform == 'android' :
	from jnius import autoclass

#cci
from king_console import resource_factory \
	                     as resources , \
						 screen , \
						 kc_ping
from king_console.kc_thread_manager \
				  				import kc_thread_manager
from king_console.kc_db_manager import kc_db_manager
from king_console.kc_stream 	import kc_mongo_config , \
								       kc_kafka_config
from king_console.kc_wireless import *





kivy.require(  '1.9.1'  )

#todo
dlabel = \
"""
Label:
	text_size: self.size
	valign: 'middle'
	halign: 'center'
"""

update_content = \
"""
GridLayout:
	orientation: 'horizontal'
	cols: 1
	Label:
		text: '...updating...'
	ProgressBar:
		max:1000
		value: 250
"""



# -----------------------------------------------------------------------------------
def local_mac_addr() :
		"""

		:return mac string:
		"""

		try :
			return base64.b64encode( proc.check_output( ['cat' ,
														 '/sys/class/net/wlan0/address'] ).strip().lower() )
		except :
			pass


lname = 'king-console-intf' + local_mac_addr()




# -------------------------------------------------------------------------------------------------
class stream_requests_handler( logging.Handler ) :
				"""

				"""
				def emit( self , record ) :

					log_entry = self.format(record)
					return requests.post('http://localhost:7081/trinity-vulture/post_stream_msg',
										 log_entry, headers={"Content-type": "application/json"}).content



# -------------------------------------------------------------------------------------------------
class stream_formatter( logging.Formatter ) :
				"""

				"""

				def __init__(self, task_name=None):



					super(  stream_formatter , self).__init__()



				def format( self , record ) :

					data = {'@message': record.msg,
							'@timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
							'@type':  lname }


					return json.dumps(data)



# dynamic
class dynamic_import :
		"""
		dynamic import
		"""

		def __init__( self , module_name , class_name ) :
			"""
			constructor
			:param module_name:
			:param class_name:
			:return:
			"""

			module = __import__( module_name )
			_class = getattr(module, class_name)
			self._instance = _class()

		@property
		def cls_instance( self ) :
			return self._instance
		@cls_instance.setter
		def cls_instance( self , cls ) :
			self._instance = cls


class ConsoleAccordion( Accordion ) :

		btn_text = StringProperty('')
		_orientation = StringProperty('vertical')
		_inner_orientation = StringProperty( 'horizontal' )
		orientation_handler = ObjectProperty(None)

		stop = threading.Event()

		def __init__( self, *args, **kwargs):
			super( ConsoleAccordion , self ).__init__( *args, **kwargs)

			# get the original orientation
			self._orientation = 'horizontal' if Window.width > Window.height else 'vertical'
			# inform user
			self.btn_text = self._orientation
			self.orientation = self._orientation
			self._inner_orientation =  'vertical' if self.orientation == 'horizontal' else 'horizontal'


		def check_orientation( self , width , height ) :
			"""

			:param width:
			:param height:
			:return:
			"""

			orientation = 'vertical' if height > width else 'horizontal'
			if orientation != self._orientation:
				self._orientation = orientation
				self.orientation_cb(orientation)



		def orientation_cb( self , orientation ) :
			"""

			:param orientation:
			:return:
			"""
			self.btn_text = orientation
			self.orientation = 'horizontal' if Window.width > Window.height else 'vertical'
			self._inner_orientation =  'vertical' if self._orientation == 'horizontal' else 'horizontal'


class CustomDropDown( DropDown ):
    pass



class kingconsoleApp( App ) :
		"""
		maelstrom
		"""


		def __init__( self ) :
			"""

			:return:
			"""

			super( kingconsoleApp , self ).__init__()

			self.settings_cls =  SettingsWithSpinner


			# logger
			self._logger = logging.getLogger( "king console" )
			self._logger.setLevel( logging.DEBUG )
			fh = logging.FileHandler(  'king-console.log' + '-debug.log', mode = 'a' )
			fh.setLevel( logging.DEBUG )
			formatter = logging.Formatter( resources.log_format )
			fh.setFormatter( formatter )
			self._logger.addHandler( fh )
			self._logger.info( self.__class__.__name__ + '...'  )
			self._ret_text = str()
			#view manager
			self._view_manager = None
			self._full_screen = None
			self._full_screen_lst = list()
			self._full_item = None

			if self._check_connectivity() :
				self._console_local , \
				self._console_real , \
				self._console_ifconfig , \
				self._console_iwlist =  self._Local_net_info()
			else :
				self._console_local = 'None'
				self._console_real = 'None'
				self._console_ifconfig = 'None'
				self._console_iwlist  = 'None'
				self._logger.error( '...no connectivity...' )

			self._session_id = None

			self._current_ip = self._console_ifconfig
			self._console_count = 1
			self._console_constructed = list()
			self._cur_console_buffer = str()
			self._thrd = kc_thread_manager( self._logger )


			self.stop_event = threading.Event()
			self._db_call_queue = Queue.Queue()
			self._db_payload_queue = Queue.Queue()
			self._db_payload_lk = threading.RLock()
			self._is_full_screen = False
			self._is_dirty_payload = False
			self._dlg_param = None
			self._diaspora = True
			self._default_document_policy = None
			self._default_stream_policy = None
			self._rube_widget = None



			Window.on_rotate = self._on_rotate



		def _init_stream_logging( self ) :
				"""

				:return:

				"""

				handler = stream_requests_handler()
				formatter = stream_formatter( "king-console-intf" )
				handler.setFormatter( formatter )
				self._logger.addHandler( handler )





		def build( self ) :
			"""

			:return:
			"""

			return self.root




		# helpers
		@staticmethod
		def _retr_resource( resource_id ) :
			"""

			:param resource_id:
			:return ui resource:
			"""

			return resources.const_resource_ids[resource_id]


		# settings
		def build_settings( self , settings ) :
			"""

			:param settings:
			:return:
			"""
			settings.add_json_panel( 'king-console contexts',
									  self.config ,
									  data=resources.settings_json )
			settings.add_json_panel( 'king-console environment',
									  self.config ,
									  data=resources.settings_env_json )
			settings.add_json_panel( 'king-console streams',
									 self.config ,
									 data=resources.settings_stream_json )
			self.use_kivy_settings = False


		def build_config( self , config ) :
			"""

			:param config:
			:return:
			"""
			config.setdefaults( 'stream',  {
											'packet_timeout': 3 ,
											'show_stream': 1 ,
											} )
			config.setdefaults( 'network-icmp', {
											'packet_timeout': 1 ,
											'show_stream': 1 ,
											'default_address' : 'www.chromaticuniverse.xyz'
											} )




		def _real_ip_callback( self , ip = None ) :
			"""

			:param ip:
			:return real ip:
			"""

			# if using nat will differ
			try :
				rip = urllib2.urlopen( 'https://enabledns.com/ip' , timeout=3 )
				self._console_real = rip.read()
				self.root.current_screen.ids.console_real_id.text = self._console_real

			except Exception as e :
				pass




		def _create_session( self ) :
			"""

			:return:
			"""

			# we don't use db queue in main thread


			uid = str( uuid.uuid4() )
			package = ( ( 'insert_session'  ,
						[uid ,
						 'wiljoh' ,
						 'level1' ,
						 'king console' ,
						  local_mac_addr()] ) )
			self.dbq.put( package )
			id = '(session_id=%s)' % uid
			package = ( ( 'insert_session_call'  ,
						[uid ,
						 'application' ,
						 'init' ,
						 id ,
						 self._console_ifconfig] ) )
			self.dbq.put( package )
			self._session_id = uid


			if self._check_connectivity() :
				# document repository
				try :
					mac =  local_mac_addr()
					data = {
							 "active" : "true" ,
							 "device_id" : mac ,
							 "last_known_ip" : self._console_local ,
							 "last_known_remote_ip" : self._console_real
							}
					s = 'http://localhost:7081/trinity-vulture/session_update'
					requests.post( s ,
									   data = json.dumps( data ) , timeout = 2 )

					self._init_stream_logging()

					Clock.schedule_once( self._real_ip_callback , 15  )
					self._logger.info( '..updated session info remote...open %s' % local_mac_addr() )
				except Exception as e :
					self._logger.error( e.message )




			else :
				self._logger.error( '...could not update session remote info...no connectivity...' )





		def _save_session_notes( self ) :
			"""

			:return:
			"""
			try :
				for slide in self.root.current_screen.ids.maelstrom_carousel_id.slides :
					try :
						if slide.children[2].text.find( 'notes #' ) != -1 :
							tx = slide.children[1].children[0]
							# non empty only
							if len( tx.text ) == 0 :
								return

							# pst note
							package = ( ( 'insert_session_note'  ,
							[ self._session_id ,
							  tx.text ,
							  '(none)'] ) )
							self.dbq.put( package )
							# post stack call , no payload
							#todo filter these out of payload processing
							id = '(session_id=%s)' % self._session_id
							package = ( ( 'insert_session_call'  ,
										[ self._session_id ,
										 'application' ,
										 'notes' ,
										 '(none)' ,
										 tx.text] ) )
							self.dbq.put( package )

					except :
						continue

			except :
				# ignore everything , the app is exiting
				pass



		def _close_session( self ) :
			"""

			:return:
			"""

			mac =  local_mac_addr()
			self._save_session_notes()

			# we don't use db queue in main thread
			package = ( ( 'update_session_status'  ,
						[0 , self._session_id] ) )
			self.dbq.put( package )
			# document repository
			if self._check_connectivity() :
				try :
					mac =  local_mac_addr()
					data = {
							 "active" : "false" ,
							 "device_id" : mac ,
							 "last_known_ip" : self._console_local ,
							 "last_known_remote_ip" : self._console_real
							}
					s = 'http://localhost:7081/trinity-vulture/session_update'
					requests.post( s ,
									   data = json.dumps( data ) , timeout = 2 )
				except Exception as e :
					self._logger.error( e.message )


				self._logger.info( '..updated session info remote...closed %s' % mac )
			else :
				self._logger.error( '...could not update session remote info...no connectivity...' )




		def _retr_proc_atom( self , proc_str = None ) :
			"""

			:return proc atom:
			"""

			pass



		def _Local_net_info( self ) :
			"""

			:return:
			"""
			out = str()
			out2 = str()
			ifconfig = str()
			iw = str()

			try :

				   if platform == 'android' :
						cmd = ["su" ,
							   "-c" ,
							   "/data/data/com.hipipal.qpyplus/files/bin/qpython.sh"  ,
							   "./king_console/kc_ping.pyo" ,
							   "-x"
							  ]
						try :
							out = proc.check_output( cmd  )
							if out :
								pos = out.find( '<ip_info>' )
								if pos :
									out = out[:pos]
								out , out2 = out.split( ':' )
								cmd = ['busybox' , 'ifconfig']
								ifconfig = proc.check_output( cmd  )
								self.logger.info( ifconfig )
								iw =  essid_scan()


						except proc.CalledProcessError as e :
							self._logger.error( e.message )
							b_ret = False
				   else :
						return self._local_net_linux_info()

			except Exception as e :
				b_ret = False
				self._logger.error( e.message )

			return out , out2 , ifconfig , iw





		def  _local_net_linux_info( self ) :
			"""

			:return:
			"""
			out = str()
			out2 = str()
			try :

				try :
					out , out2 = kc_ping.retr_local_ip_info()
				except :
					out  = '~ '
					out2 = '~'
					pass


				cmd = ['ifconfig']
				ifconfig = proc.check_output( cmd  )
				self.logger.info( ifconfig )
				iw =  '~'

				return out , out2 , ifconfig , iw

			except proc.CalledProcessError as e :
				self._logger.error( e.message )
				b_ret = False




		def _on_rotate( self , rotation ) :
			"""

			:param rotation:
			:return:
			"""

			pass



		def on_config_change(self, config, section, key, value):
			"""

			:param config:
			:param section:
			:param key:
			:param value:
			:return:
			"""
			self._logger.info("main.py: app.on_config_change: {0}, {1}, {2}, {3}".format(
				config, section, key, value))

			"""
			if section == "section1":
				if key == "key1":
					self.root.ids.label. = value
				elif key == 'font_size':
					self.root.ids.label.font_size = float(value)
				elif key == 'default_user':
					self.root.ids.label.default_user = value
			"""


		# android mishegas
		def on_pause(self):
			# save data


			return True



		def on_resume( self ):
			# something


			pass



		@mainthread
		def _show_exit( self ) :
			"""

			:return:
			"""
			layout = Label( text = '...closing streams...standby...' )
			pop = Popup( title='break down' ,
						           content=layout , size=( 400 , 300 ) )
			pop.open()



		def on_stop( self ) :
			"""

			:return:
			"""

			layout = Label( text = '...closing streams...standby...' )
			pop = Popup( title='break down' ,
						           content=layout , size=( 400 , 300 ) )
			pop.open()

			# mark session as closed
			self._close_session()

			#stop threads
			for moniker,atom in self._thrd.thrds.iteritems() :
				atom['stop_alert'].set()
				if atom['instance'] :
					atom['instance'].join()
			#wait for all threads to exit.





		def _db_queue_thred( self ) :
			"""

			:return:
			"""

			db = kc_db_manager( '/data/media/com.chromaticuniverse.cci_trinity/king_console.sqlite' , self._logger )

			while not self._thrd.thrds['db_queue_thred']['stop_alert'].isSet() :

				while not self.dbq.empty() :
					db.db_lk.acquire()
					package  = self.dbq.get()
					# call
					try :
						db._call_map[package[0]] ( package[1] )
					except Exception as e :
						# a query?
						try :
							db._query_call_map[package[0]] ( package[1] )
						except Exception as e:
							self._logger.error( '..in db function call...' + e.message )
					finally :
						db.db_lk.release()


				sleep( 0.25 )




		def _check_connectivity( self ) :
					"""

					:return:
					"""


					if platform == 'android':
						try:
							Activity = autoclass( 'android.app.Activity' )
							PythonActivity = autoclass( 'org.renpy.android.PythonActivity' )
							activity = PythonActivity.mActivity
							ConnectivityManager = autoclass( 'android.net.ConnectivityManager')

							con_mgr = activity.getSystemService( Activity.CONNECTIVITY_SERVICE )

							conn = con_mgr.getNetworkInfo( ConnectivityManager.TYPE_WIFI ).isConnectedOrConnecting()
							if conn :
								return True
							else:
								conn = con_mgr.getNetworkInfo( ConnectivityManager.TYPE_MOBILE ).isConnectedOrConnecting()
								if conn:
									return True
								else:
									return False
						except Exception as e :
							self._logger.error( 'check connectivity failed....' +  e.message )
							return False
					else :

							return True





		def _handle_payload_update( self , touch  ) :
			"""

			:return:
			"""

			self._dlg_param.dismiss()




		def run_default_document_policy( self  , run ) :
			"""

			:param run:
			:return:
			"""

			self._toggle_policy( 'default' ,
								'document' ,
								self._default_document_policy[0][2] ,
								'/data/media/com.chromaticuniverse.cci_trinity/king_console.sqlite' ,
								run )



		def on_start( self ) :
			"""

			:return:
			"""

			self._logger.info( '...on_start...' )


			layout = GridLayout( cols = 1 , orientation = 'horizontal' )
			layout.add_widget( Image( source = 'king-console32bw.png' , size_hint_y = .50 ))
			lbl = Builder.load_string( dlabel )
			lbl.text = 'initializing services...standby....'
			layout.add_widget( lbl )
			btns = BoxLayout( orientation = 'horizontal' )
			yes_btn = Button(text='ok', background_color = [0,0,0,0]  )
			btns.add_widget( yes_btn )
			layout.add_widget( btns  )
			content = layout
			self._dlg_param = Popup( title='init async...' ,
						           content=content, auto_dismiss=True , size_hint=(None, None), size=( 400 , 300 ))

			# bind the on_press event of the button to the dismiss function
			yes_btn.bind(on_press=self._handle_payload_update )



			self._dlg_param.open()
			self._create_session()

			# db queue thread
			thred = threading.Thread( target = self._db_queue_thred )
			moniker = 'db_queue_thred'
			if thred :
					thread_atom = { 'thread_id' : str( thred.ident ) ,
									'stop_alert'  : threading.Event() ,
									'instance' : thred
								  }
					App.get_running_app()._thrd.thrds[moniker] = thread_atom
			thred.start()

			self.root.current_screen._retrieve_policy( 'default' , 'document' )
			self.root.current_screen._retrieve_policy( 'default' , 'stream' )


			self.root.current_screen.ids.console_local_id.text = self._console_local
			self.root.current_screen.ids.console_real_id.text = self._console_real
			self.root.current_screen.ids.console_interfaces.text = self._console_ifconfig + '\n\n' + self._console_iwlist
			self._cur_console_buffer = self.root.current_screen.ids.console_interfaces.text

			EventLoop.window.bind( on_keyboard = self._hook_keyboard )




		def _hook_keyboard( self , window, key , *largs ) :
				"""

				:param window:
				:param key:
				:param largs:
				:return:
				"""

				if key ==   27  :
					if self.root.current == 'screen_cci' :
						self.stop()
					else :
						self.root.current = 'screen_cci'
						return True

				return False




		def _toggle_policy( self , moniker , provider_type , interval , db  , toggle ) :
				"""

				:param moniker:
				:param provider_type:
				:param interval:
				:param db:
				:return:
				"""

				try :

					data = { 'moniker' : moniker ,
							 'provider_type' : provider_type ,
							 'interval' : str( interval ) ,
							 'db_bootstrap' : db
						   }

					if toggle :
						ps = 'start'
					else :
						ps = 'stop'
					s = 'http://localhost:7081/trinity-vulture/%s' % ps
					r = requests.post( s ,
									   data = json.dumps( data ) )
					if r.status_code != 200 :
						raise( '...post policy %s %s start failed...' % ( moniker , provider_type ) )
					self._logger.info( '...post policy succeeded for %s %s...' % ( moniker , provider_type ) )
				except Exception as e :
					self._logger.error( e.message )





		def _screen_exists( self , scr = None ) :
			"""

			:return:
			"""
			for screen in self.root.screens :
				if screen.name == scr :
					return True , screen
			return False , None




		def _selected_accordion_item( self ) :
			"""

			:return accordion item selected:
			"""
			acc = self.root.current_screen.ids.cci_accordion
			for item in acc.children :
				try:
					if not item.collapse :
						return item
				except :
					pass




		def accordion_touch_up( self ) :
			"""
			:return:
			"""
			for item in self.root.current_screen.children :
				try:
					if not item.collapse :
						self._logger.info( self.__class__.__name__ + '...' +
										   item.title + '...accordion_item_touch_down' )
				except :
					pass





		def move_to_accordion_item( self , acc , tag = None ) :
			"""
			workaround for android nesting bug
			:param acc:
			:return:
			"""

			for child in acc.children :
				if child.title == 'cci-maelstrom' :
					child.collapse = False
					child.canvas.ask_update()

			self.root.current_screen.ids.ping_btn.text = "execute"





		def _open_extended_window( self ) :
			"""

			:return:
			"""

			item = self._selected_accordion_item()
			self.root.current = 'screen_' + item.title




		def _manip_extended_window( self , widg = None  , no_keep_alive = True ) :
			"""

			:return:
			"""

			self.root.current = 'screen_cci'
			if widg is not None :
				self.root.remove_widget( widg )






		def _on_full_screen( self ) :
			"""

			:return:
			"""

			# rube goldberg for no full screen for notes ; poorly implemented
			# keyboard goofosity on android
			try :
				if self.root.current_screen.ids.maelstrom_carousel_id.current_slide. \
													   children[2].text.find( 'notes #' ) != -1 :
					return
			except :
				pass


			acc = self.root.current_screen.ids.cci_accordion
			cci = None
			if not self._is_full_screen :
				self._full_screen_lst = list()
				for item in acc.children :
					self._full_screen_lst.append( item )
					if item.title == 'cci-maelstrom' :
						cci = item
				self._full_screen_lst.remove( cci )
				for item in self._full_screen_lst :
					acc.remove_widget( item )
				self._is_full_screen = True
			else :
				cci = acc.children[0]
				acc.remove_widget( cci )
				self._full_screen_lst.reverse()
				for item in self._full_screen_lst :
					acc.add_widget( item )
				acc.add_widget( cci )
				self._is_full_screen = False




		def _on_document_context( self  , context ) :
				"""

				:return:
				"""

				if context == 'mongo' :
					mongo = kc_mongo_config( bootstrap ='cci-server' ,
											 port = 8001 ,
											 log = self._logger ,
											 device_id = local_mac_addr() )
					mongo.show_config()
				elif context == 'kafka-publisher' :

					kafka = kc_kafka_config( bootstrap = 'cci-server' ,
											 log = self._logger )
					kafka.show_config()




		def _toggle_tree_view_manager_nodes( self , btn ) :
			"""

			:param modes:
			:return:
			"""

			tree = self._rube_widget

			if btn.text == 'expand' :
				for node in tree.iterate_open_nodes():
					if not node.is_open:
						tree.toggle_node( node )
				btn.text = 'close'
			else :
				for node in tree.iterate_open_nodes():
					if node.is_open:
						tree.toggle_node( node )
				btn.text = 'expand'




		def _on_view_manager( self ) :
			"""

			:return:
			"""

			if not self._view_manager :
				self._view_manager = screen.ViewManagerScreen()
				self._view_manager.name = 'screen_view_manager'
				self._view_manager.id = 'view_manager_screen'
				tv = TreeView( root_options=dict( text = 'king console' , font_size = 18 ) )
				self._rube_widget = tv

				layout = GridLayout( orientation='horizontal' , size_hint_y = None  , cols=1 , size = (480 , 900 ))
				# action bar
				ab = Builder.load_string( self._retr_resource( 'action_bar_plus' ) )


				layout.add_widget( ab )

				# scroll
				sv = ScrollView()

				# tree view
				n1 = tv.add_node(screen.TreeManagerLabel(text='main context') )
				n2 = tv.add_node(screen.TreeManagerLabel(text='transport'), n1)
				tv.add_node(screen.TreeManagerLabel(text='syn ack'), n2)
				n3 = tv.add_node(screen.TreeManagerLabel(text='mini mport scan'), n2)
				tv.add_node(screen.TreeManagerLabel(text='discovery & port manip'), n3)
				tv.add_node(screen.TreeManagerLabel(text='nmap firewalk'), n3)
				tv.add_node(screen.TreeManagerLabel(text='atomic firewalk'), n3)


				n4 = tv.add_node(screen.TreeManagerLabel(text='network'), n1)
				tv.add_node(screen.TreeManagerLabel(text='ping'), n4)
				n5 = tv.add_node(screen.TreeManagerLabel(text='ping subnet'), n4)
				tv.add_node(screen.TreeManagerLabel(text='beaucoup ping' ) , n5),
				n6 = tv.add_node(screen.TreeManagerLabel(text='application & discovery'), n1)
				n7 = tv.add_node(screen.TreeManagerLabel(text='quick fingerprint'), n6)
				tv.add_node(screen.TreeManagerLabel(text='fat ingerprint'), n6)
				tv.add_node(screen.TreeManagerLabel(text='baby snmp'), n7)
				tv.add_node(screen.TreeManagerLabel(text='upnp'), n7)
				tv.add_node(screen.TreeManagerLabel(text='ip geography'), n7)
				n8 = tv.add_node(screen.TreeManagerLabel(text='datalink'), n1)
				tv.add_node(screen.TreeManagerLabel(text='arp'), n8)
				n9 = tv.add_node(screen.TreeManagerLabel(text='arp scan'), n8)
				tv.add_node(screen.TreeManagerLabel(text='arp monitor'), n9)
				n10 = tv.add_node(screen.TreeManagerLabel(text='streams'), n1)
				tv.add_node(screen.TreeManagerLabel(text='payload policy'), n10)
				tv.add_node(screen.TreeManagerLabel(text='traceroute context' ) )
				tv.add_node(screen.TreeManagerLabel(text='packet stream context' ) )

				layout.add_widget( tv )
				sv.add_widget( layout )


				self._view_manager.add_widget( sv )
				self.root.add_widget( self._view_manager )

			self.root.current = self._view_manager.name


		# attributes
		@property
		def logger( self ) :
			return self._logger
		@logger.setter
		def logger( self , log ) :
			self._logger = log
		@property
		def dbq( self ) :
			return self._db_call_queue
		@dbq.setter
		def dbq( self , q ) :
			self._db_call_queue = q
		@property
		def dbpq( self ) :
			return self._db_payload_queue
		@dbpq.setter
		def dbpq( self , q ) :
			self._db_payload_queue = q
		@property
		def dbpq_lk( self ) :
			return self._db_payload_lk
		@dbpq_lk.setter
		def dbpq_lk( self , lk ) :
			self._db_payload_lk = lk
		@property
		def session( self ) :
			return self._session_id
		@session.setter
		def session( self , sess ) :
			self._session_id = sess


        

      

if __name__ == '__main__':

		Config.set( 'graphics', 'width', '480' )
		Config.set( 'graphics', 'height', '800' )
		Config.set( 'input', 'mouse', 'mouse,disable_multitouch' )


		#from kivy.core.window import Window

		Window.size = ( 480 , 800 )

		kc = kingconsoleApp()
		kc.run()
		kc.logger.info( "main...app running....." )
            
