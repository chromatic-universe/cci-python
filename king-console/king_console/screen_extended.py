import threading
from kivy.app import App
from kivy.clock import Clock , mainthread
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.bubble import Bubble
from kivy.uix.actionbar import ActionBar , ActionButton
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.accordion import Accordion ,AccordionItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.screenmanager import ScreenManager, \
	                               Screen ,\
	                               RiseInTransition ,\
								   SwapTransition , \
								   FallOutTransition , \
								   SlideTransition
from kivy.graphics import Color
from kivy.core.window import Window


#cci
import screen
from king_console import resource_factory \
	                     as resources
from resource import transport_extended as transport_resources ,\
					 app_discovery_extended as app_discovery_resources
from king_console import kc_ping , \
						 kc_arp , \
						 kc_tcp , \
						 kc_nmap , \
						 kc_wireless
import random
import datetime
from time import gmtime, strftime , sleep
import subprocess as proc
import Queue
import json
from requests import put, get
from kivy.core.window import Window
from kivy.clock import Clock , mainthread


screen_map = {  'nmap firewalk' : False ,
				'ip_geography_view'  : False ,
				'zombie' : False ,
				'discovery and port manip' : False
	         }

class console_grid( GridLayout ) :

		ip_input_metric = ObjectProperty()



# -------------------------------------------------------------------------------------------------
class DatalinkScreen( Screen ) :
					"""


					"""
					stop = threading.Event()

					accordion_id = ObjectProperty()
					console_arp_monitor_txt = ObjectProperty()
					start_monitor_btn = ObjectProperty()
					console_params = ObjectProperty()




					@staticmethod
					def _retr_resource( resource_id ) :
						"""

						:param resource_id:
						:return ui resource:
						"""

						return resources.const_resource_ids[resource_id]





					def _post_function_call( self , func , params ) :
						"""

						:param func:
						:param params:
						:return:
						"""

						package = ( func , params )
						App.get_running_app().dbq.put( package )




					def _post_payload( self , func , params ) :
						"""

						:param func:
						:param params:
						:return:
						"""

						if not App.get_running_app()._call_stack_debug :
							package = ( func , params )
							App.get_running_app().dbq.put( package )





					def _on_arp_monitor_start( self ) :
						"""

						:return:
						"""

						self.ids.console_arp_monitor_txt.text += '...standby....\n\n'
						if self.ids.start_monitor_btn.text == 'start' :

							thred = threading.Thread( target = self._on_arp_monitor ,
													  kwargs=dict( console=self.console_arp_monitor_txt ,
																   items = 15 ) )
							if thred :
								moniker = 'arp monitor console'
								thread_atom = { 'thread_id' : str( thred.ident ) ,
												'stop_alert'  : threading.Event() ,
												'instance' : thred
											  }
								App.get_running_app()._thrd.thrds[moniker] = thread_atom


							thred.start()

							self.ids.console_arp_monitor_txt.text += '...working.....'
							self.ids.start_monitor_btn.text = 'stop'
							self.ids.start_monitor_btn.color = [1,0,0.1]
						else :
							thr = App.get_running_app()._thrd.thrds['arp monitor console']
							thr['stop_alert'].set()
							self.ids.start_monitor_btn.text = 'start'
							self.ids.start_monitor_btn.color = [0,1,0.1]
							self.ids.console_arp_monitor_txt.text = ''




					@mainthread
					def _update_console_payload( self , content , params = '(no params)' ) :
						"""

						:param console slide:

						:return:
						"""


						self.ids.console_arp_monitor_txt.text = content + self.ids.console_arp_monitor_txt.text
						self.ids.console_params.text = params


						self.canvas.ask_update()




					def _on_arp_monitor( self , console = None , items = 15 ) :
						"""
						:param console:
						:param items:
						:return
						"""


						thr = App.get_running_app()._thrd.thrds['arp monitor console']
						alarm = thr['stop_alert']

						App.get_running_app()._logger.info( self.__class__.__name__ + '...on_arp_monitor'  )

						boiler = str()

						try :

							if alarm.isSet() :
									return
						except :
							pass


						try :

							cmd = ["su" ,
								   "-c" ,
								   "/data/data/com.hipipal.qpyplus/files/bin/qpython.sh" ,
								   "./king_console/kc_arp.pyo" ,
								   '-x' ,
								    '12'
								  ]
							"""
							cmd = [ "python" ,
								   "./king_console/kc_arp.py" ,
								   '-x' ,
								   '8'
								  ]
							"""
							try :
								while not alarm.isSet() :
									boiler = proc.check_output( cmd  )

									pos = boiler.find( '[]' )
									if pos != -1 :
										boiler = boiler[:pos]

									self._update_console_payload( boiler  )
									self._post_function_call( 'insert_session_call' , [ App.get_running_app()._session_id ,
																			'datalink' ,
																			'arp_monitor' ,
							  												'(no_params)' ,
																			boiler ] )
									sleep( 1 )
							except proc.CalledProcessError as e :
								b_ret = False
						except Exception as e :
							b_ret = False
							App.get_running_app()._logger.error( e.message )











# -------------------------------------------------------------------------------------------------
class NetworkScreen( Screen ) :
					"""


					"""
					stop = threading.Event()

					action_bar = ObjectProperty()
					accordion_id = ObjectProperty()
					_console_text = ObjectProperty()
					view_btn_a = ObjectProperty()
					action_view = ObjectProperty()



					@staticmethod
					def _retr_resource( resource_id ) :
						"""

						:param resource_id:
						:return ui resource:
						"""

						return resources.const_resource_ids[resource_id]





					def _post_function_call( self , func , params ) :
						"""

						:param func:
						:param params:
						:return:
						"""

						package = ( func , params )
						App.get_running_app().dbq.put( package )




					def _post_payload( self , func , params ) :
						"""

						:param func:
						:param params:
						:return:
						"""

						if not App.get_running_app()._call_stack_debug :
							package = ( func , params )
							App.get_running_app().dbq.put( package )




					def add_console(  self ,
								   content ,
								   tag  ) :
							"""
							:param parent:
							:param content:
							:param: console_count:
							:param tag:

							:return:
							"""

							layout = GridLayout( cols = 1 ,
												 orientation = 'horizontal'
												  )
							bar = Builder.load_string( self._retr_resource( 'dlg_action_bar_3' ) )
							bar.ids.view_btn_a.text = 'back'
							bar.ids.view_btn_a.bind( on_press =
								lambda a:App.get_running_app()._manip_extended_window() )
							layout.add_widget( bar )
							layout.add_widget( Label( text = tag  ,
													  color = [ 1, 0 , 0 , 1] ,
													  font_size = 16 ,
													  size_hint_y = 0.1 ) )

							scrolly = Builder.load_string( self._retr_resource( 'text_scroller' ) )
							tx = scrolly.children[0]
							tx.text = ''

							layout.add_widget( scrolly )
							layout.add_widget( Label( text =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S" )  ,
													font_size = 16  ,
													size_hint_y = 0.2 ,
													color = [ 1, 0 , 0 , 1] ) )

							return layout




# -------------------------------------------------------------------------------------------------
class AppDiscoveryScreen( Screen ) :
					"""


					"""
					stop = threading.Event()

					action_bar = ObjectProperty()
					accordion_id = ObjectProperty()
					_console_text = ObjectProperty()
					console_timestamp = ObjectProperty()
					_is_full_screen = ObjectProperty()
					ip_geo_key = ObjectProperty()
					ip_geo_metric = ObjectProperty()
					console_count = ObjectProperty()


					def __init__( self , **kwargs ) :
						"""

						:param kwargs:
						:return:
						"""


						super( AppDiscoveryScreen , self ).__init__( **kwargs )

						self._console_count = 0
						self._full_screen_lst = None





					@staticmethod
					def _retr_resource( resource_id ) :
						"""

						:param resource_id:
						:return ui resource:
						"""

						return app_discovery_resources.const_app_discovery_ids[resource_id]






					def _post_function_call( self , func , params ) :
						"""

						:param func:
						:param params:
						:return:
						"""

						package = ( func , params )
						App.get_running_app().dbq.put( package )




					def _post_payload( self , func , params ) :
						"""

						:param func:
						:param params:
						:return:
						"""

						if not App.get_running_app()._call_stack_debug :
							package = ( func , params )
							App.get_running_app().dbq.put( package )






					def _move_to_accordion_item( self , acc , tag = None ) :
							"""

							:param acc:
							:return:
							"""

							for child in acc.children :
								if child.title == tag :
									child.collapse = False
									child.canvas.ask_update()





					def _on_full_screen(self):
						"""

						:return:
						"""

						acc = self.ids.appdiscovery_accordion
						cci = None
						if not self._is_full_screen:
							self._full_screen_lst = list()
							for item in acc.children:
								self._full_screen_lst.append(item)
								if item.title == 'cci-maelstrom':
									cci = item
							self._full_screen_lst.remove(cci)
							for item in self._full_screen_lst:
								acc.remove_widget(item)
							self._is_full_screen = True
						else:
							cci = acc.children[0]
							acc.remove_widget(cci)
							self._full_screen_lst.reverse()
							for item in self._full_screen_lst:
								acc.add_widget(item)
							acc.add_widget(cci)
							self._is_full_screen = False




					def on_touch_up( self , touch ) :
							self._selected_accordion_item()





					def _selected_accordion_item( self  ) :
						"""

						:return accordion item selected:
						"""
						acc = self.ids.appdiscovery_accordion
						for item in acc.children :
							try:
								if not item.collapse :
									if item.title == 'ip geography' :
										App.get_running_app()._logger.info( item.title )
										if not screen_map['ip_geography_view'] :
											view = Builder.load_string( self._retr_resource('ip_geography_view'  ) )
											self.ip_geo_metric = view.ids.ip_geo_metric
											self.ip_geo_key = view.ids.ip_geo_key
											view.ids.do_geo_btn.bind( on_press = lambda a: self._on_geography_start()  )
											self.ids.view_ip_geo.add_widget( view )
											screen_map['ip_geography_view'] = True
										return item

							except Exception as e :
								App.get_running_app()._logger.error( e.message )






					@mainthread
					def _update_console_payload( self , content , console , params = None ) :
						"""

						:param console slide:

						:return:
						"""


						console.children[1].children[0].text = content
						console.children[0].text = params + '\n' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
						console.children[0].halign = 'center'
						self.canvas.ask_update()





					def _on_geography_start( self ) :
							"""

							:return:
							"""




							self._console_count += 1
							carousel = self.ids.appdiscovery_carousel_id
							console = self.add_console(  content = 'cci-maelstrom~app_discovery-> :...working...this could be lenghty...no time updates' ,
																	tag = 'ip geo console #%d' % self._console_count )

							carousel.add_widget( console  )
							carousel.index += 1
							self._move_to_accordion_item( self.ids.appdiscovery_accordion , 'cci-maelstrom' )


							thred = threading.Thread( target = self._on_ip_geography ,
													  kwargs=dict( ip = self.ip_geo_metric.text ,
																   console=console ,
																   key_file = self.ip_geo_key.text
																	) )
							if thred :
								moniker = 'ip geo console #' + str( self._console_count )
								thread_atom = { 'thread_id' : str( thred.ident ) ,
												'stop_alert'  : threading.Event() ,
												'instance' : thred
											  }
								App.get_running_app()._thrd.thrds[moniker] = thread_atom


							thred.start()






					def _on_ip_geography( self ,
										  ip = None ,
										  key_file = None ,
										  console = None  ) :
						"""

						:param ip:
						:param key_file:
						:param console:
						:return:
						"""

						out = str()
						call = str()

						App.get_running_app()._logger.info( self.__class__.__name__ + '...on_ip_geography'  )



						b_ret = False
						out = str()

						try :

							try :
								b_ret , out = kc_wireless.ip_geography( ip = ip ,
																        key_file = key_file )
								App.get_running_app()._logger.info( out )
							except proc.CalledProcessError as e :
								b_ret = False
						except Exception as e :
							b_ret = False
							App.get_running_app()._logger.error( e.message )

						try :
							thr = App.get_running_app()._thrd.thrds['ip geo console #'  + str( App.get_running_app()._console_count )]
							if thr :
								if thr['stop_alert'].isSet() :
									return
						except :
							pass

						boiler = str()
						if b_ret is False:
							boiler += '...ip geography....access key snafu?..'
						else :
							boiler = 'cci-maelstrom[app_discovery]->: ' + \
									 ' ' + ip
							boiler += '\n'
							boiler += out



						App.get_running_app()._logger.info( self.__class__.__name__ + '...boiler='  + boiler )

						id = '(ip=%s)' % ip
						self._post_function_call( 'insert_session_call' , [ App.get_running_app()._session_id ,
																			'app_discovery' ,
																			'ip_geography' ,
																			id ,
																			boiler] )
						id = call + ' ' + id
						self._update_console_payload( boiler ,console , id )







					def add_console(  self ,
								   content ,
								   tag  ) :
							"""

							:param content:
							:param tag:

							:return:
							"""


							layout = GridLayout( cols = 1  ,
												 orientation = 'horizontal' ,
												 id = tag
												  )
							layout.add_widget( Label( text = tag  ,
													  color = [ 1, 0 , 0 , 1] ,
													  font_size = 16 ,
													  id = 'tag_label' ,
													  size_hint_y = 0.1 ) )

							scrolly = Builder.load_string( self._retr_resource( 'text_scroller' ) )
							tx = scrolly.children[0]
							tx.text = content

							layout.add_widget( scrolly )
							layout.add_widget( Label( text =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S" )  ,
													font_size = 16  ,
													size_hint_y = 0.2 ,
													color = [ 1, 0 , 0 , 1] ) )

							return layout



# -------------------------------------------------------------------------------------------------
class TransportScreen( Screen ) :
					"""


					"""
					action_bar = ObjectProperty()
					accordion_id = ObjectProperty()
					_console_text = ObjectProperty()
					nmap_fire_box = ObjectProperty()
					console_timestamp = ObjectProperty()
					_is_full_screen = ObjectProperty()
					cci_action_prev = ObjectProperty()
					probe_recv_slider = ObjectProperty()
					retry_slider = ObjectProperty()
					max_probe_slider = ObjectProperty()
					probe_slider = ObjectProperty()
					ip_input_metric = ObjectProperty()
					console_count = ObjectProperty()
					transport_carousel_id = ObjectProperty()
					do_firewalk_btn = ObjectProperty()
					firewalk_grid = ObjectProperty()
					ip_zombie_metric = ObjectProperty()
					zombie_query_tx = ObjectProperty()

					def __init__( self , **kwargs ) :
						"""

						:param kwargs:
						:return:
						"""


						super( TransportScreen , self ).__init__( **kwargs )

						self._console_count = 0



					@staticmethod
					def _retr_resource( resource_id ) :
						"""

						:param resource_id:
						:return ui resource:
						"""

						return transport_resources.const_transport_resource_ids[resource_id]





					def _post_function_call( self , func , params ) :
						"""

						:param func:
						:param params:
						:return:
						"""

						package = ( func , params )
						App.get_running_app().dbq.put( package )




					def _post_payload( self , func , params ) :
						"""

						:param func:
						:param params:
						:return:
						"""

						if not App.get_running_app()._call_stack_debug :
							package = ( func , params )
							App.get_running_app().dbq.put( package )





					def _on_full_screen(self):
						"""

						:return:
						"""

						acc = self.ids.tcp_accordion
						cci = None
						if not self._is_full_screen:
							self._full_screen_lst = list()
							for item in acc.children:
								self._full_screen_lst.append(item)
								if item.title == 'cci-maelstrom':
									cci = item
							self._full_screen_lst.remove(cci)
							for item in self._full_screen_lst:
								acc.remove_widget(item)
							self._is_full_screen = True
						else:
							cci = acc.children[0]
							acc.remove_widget(cci)
							self._full_screen_lst.reverse()
							for item in self._full_screen_lst:
								acc.add_widget(item)
							acc.add_widget(cci)
							self._is_full_screen = False



					def add_console(  self ,
								   content ,
								   tag  ) :
							"""
							:param parent:
							:param content:
							:param: console_count:
							:param tag:

							:return:
							"""

							layout = GridLayout( cols = 1  ,
												 orientation = 'horizontal' ,
												 id = tag
												  )
							layout.add_widget( Label( text = tag  ,
													  color = [ 1, 0 , 0 , 1] ,
													  font_size = 16 ,
													  id = 'tag_label' ,
													  size_hint_y = 0.1 ) )

							scrolly = Builder.load_string( self._retr_resource( 'text_scroller' ) )
							tx = scrolly.children[0]
							tx.text = content

							layout.add_widget( scrolly )
							layout.add_widget( Label( text =  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S" )  ,
													font_size = 16  ,
													size_hint_y = 0.2 ,
													color = [ 1, 0 , 0 , 1] ) )

							return layout


					def _move_to_accordion_item( self , acc , tag = None ) :
							"""

							:param acc:
							:return:
							"""

							for child in acc.children :
								if child.title == tag :
									child.collapse = False
									child.canvas.ask_update()



					@mainthread
					def _update_console_payload( self , content , console , params = None ) :
						"""

						:param console slide:

						:return:
						"""


						console.children[1].children[0].text = content
						console.children[0].text = params + '\n' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
						console.children[0].halign = 'center'
						self.canvas.ask_update()



					def  _on_firewalk_start( self ) :
						"""

						:return:
						"""



						self._console_count += 1
						carousel = self.ids.transport_carousel_id

						console = self.add_console(  content = 'cci-maelstrom~transport-> :...working...this could be lenghty...no time updates' ,
																tag = 'firewalk console #%d' % self._console_count )

						carousel.add_widget( console  )
						carousel.index += 1
						self._move_to_accordion_item( self.ids.tcp_accordion , 'cci-maelstrom' )


						thred = threading.Thread( target = self._on_nmap_firewalk ,
												  kwargs=dict( ip = self.ip_input_metric.text ,
															   console=console ,
															   max_ports = self.max_probe_slider.value ,
													           max_retries = self.retry_slider.value ,
															   probe_timeout = self.probe_slider.value ,
															   recv_timeout = self.probe_recv_slider.value
															    ) )
						if thred :
							moniker = 'firewalk console #' + str( self._console_count )
							thread_atom = { 'thread_id' : str( thred.ident ) ,
											'stop_alert'  : threading.Event() ,
											'instance' : thred
										  }
							App.get_running_app()._thrd.thrds[moniker] = thread_atom


						thred.start()





					def on_touch_up( self , touch ) :
							self._selected_accordion_item()




					def _on_show_manip( self ) :
							"""

							:return:
							"""

							call_map = { 'christmas tree scan' : None ,
										 'half-open firewalk' : None ,
										 'broadcast-dhcp' : None ,
										 'broadcast-dns' : None
										}


							layout = GridLayout( orientation = 'horizontal' ,
											  cols = 1 )

							scroll = ScrollView()
							grid = GridLayout( cols=1 , orientation = 'horizontal' , size_hint_y = None , size=(400 , 800 ) )

							for key,value in call_map.iteritems() :
								grid.add_widget( Button( text = key  ,
														        halign = 'center' ,
																font_size = 16 ,
																background_color =  [0,0,0,0] ,
																color = [1,0,0,1] ,
																size_hint_y = None ,
																size_hint_x = 200  ) )
							scroll.add_widget( grid )
							layout.add_widget( scroll )
							self.ids.discovery_and_manip.add_widget( layout )
							"""
							popup = ConsolePopup( title='console history' , content=layout )
							btn = popup.content.children[1].children[0].children[0]
							btn.bind( on_press = lambda a:self._on_show_session_note() )
							"""




					def _selected_accordion_item( self  ) :
							"""

							:return accordion item selected:
							"""
							acc = self.ids.tcp_accordion
							for item in acc.children :
								try:
									if not item.collapse :
										if item.title == 'nmap firewalk' :
											App.get_running_app()._logger.info( item.title )
											if not screen_map['nmap firewalk'] :
												view = Builder.load_string( self._retr_resource('nmap_firewalk_view'  ) )
												self.max_probe_slider = view.ids.max_probe_slider
												self.probe_recv_slider = view.ids.probe_recv_slider
												self.retry_slider = view.ids.retry_slider
												self.probe_slider = view.ids.probe_slider
												self.ip_input_metric = view.ids.ip_input_metric
												view.ids.do_firewalk_btn.bind( on_press = lambda a: self._on_firewalk_start()  )
												self.ids.nmap_firewalk.add_widget( view )
												screen_map['nmap firewalk'] = True
										elif item.title == 'zombie' :
												App.get_running_app()._logger.info( item.title )
												if not screen_map['zombie'] :
													screen_map['zombie'] = True
													view = Builder.load_string( self._retr_resource('zombie_view'  ) )
													self.ip_zombie_metric = view.ids.ip_zombie_metric
													self.zombie_query_titem_zombie_scanx = view.ids.zombie_query_tx
													self.ids.item_zombie_scan.add_widget( view)
										elif item.title == 'discovery and port manip' :
												App.get_running_app()._logger.info( item.title )
												if not screen_map['discovery and port manip'] :
													self._on_show_manip()
													screen_map['discovery and port manip'] = True
										return item

								except Exception as e :
									App.get_running_app()._logger.error( e.message )





					def _on_nmap_firewalk( self ,
										   ip = None ,
										   console = None ,
										   max_ports = 0 ,
										   max_retries = 0 ,
										   probe_timeout = 0,
										   recv_timeout = 0 ) :
							"""
							:param: ip:
							:param : console :
							:return:
							"""

							out = str()
							call = str()

							App.get_running_app()._logger.info( self.__class__.__name__ + '...on_nmap_firewalk'  )



							b_ret = False
							out = str()

							try :

								try :
									b_ret , out = kc_nmap.firewalk(    ip = ip ,
																	   max_ports = max_ports ,
																	   max_retries = max_retries ,
																	   probe_timeout = probe_timeout,
																	   recv_timeout = recv_timeout )
									App.get_running_app()._logger.info( out )
								except proc.CalledProcessError as e :
									b_ret = False
							except Exception as e :
								b_ret = False
								App.get_running_app()._logger.error( e.message )

							try :
											thr = App.get_running_app()._thrd.thrds['firewalk console #'  + str( App.get_running_app()._console_count )]
											if thr :
												if thr['stop_alert'].isSet() :
													return
							except :
								pass

							boiler = 'maelstrom[transport]->firewalk: ' + \
									  ' ' + ip
							boiler += '\n'
							boiler += out
							if not b_ret :
								boiler += '...firewalk failed....no access to transport layer?..'
							App.get_running_app()._logger.info( self.__class__.__name__ + '...boiler='  + boiler )

							id = '(ip=%s)' % ip
							self._post_function_call( 'insert_session_call' , [ App.get_running_app()._session_id ,
																				'transport' ,
																				'nmap_firewalk' ,
																				id ,
																				boiler] )
							id = call + ' ' + id
							self._update_console_payload( boiler ,console , id )
							App.get_running_app()._logger.info( '..update_console_payload...' )



