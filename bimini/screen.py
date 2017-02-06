# screen.py     william k. johnson 2016
import threading
from kivy.app import App
from kivy.clock import Clock , mainthread
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.treeview import TreeViewLabel
from kivy.uix.screenmanager import ScreenManager, \
	                               Screen ,\
	                               RiseInTransition ,\
								   SwapTransition , \
								   FallOutTransition , \
								   SlideTransition

#cci
from bimini import resource_factory \
	                     as resources

from time import gmtime, strftime , sleep
import subprocess as proc





# -------------------------------------------------------------------------------------------------
def add_console( self ,
				  parent ,
				  content ,
				  console_count ,
				  tag  ) :
				"""
				:param parent:
				:param content:
				:param: console_count:
				:param tag:

				:return:
				"""

				layout = GridLayout( cols = 1 ,
									 padding = [0 , 5 , 0 ,5]
									  )
				self._console_count += 1
				layout.add_widget( Label( text = tag + str( console_count ) ,
										color = [ 1, 0 , 0 , 1] ,
										font_size = 16 ,
										size_hint_y = 0.1 ) )

				scrolly = Builder.load_string( self._retr_resource( 'text_scroller' ) )
				tx = scrolly.children[0]
				tx.text = content
				layout.add_widget( scrolly )
				layout.add_widget( Label( text = strftime("%Y-%m-%d %H:%M:%S", gmtime()) ,
										font_size = 16  ,
										size_hint_y = 0.2 ,
										color = [ 1, 0 , 0 , 1] ) )
				parent,add_widget( layout )




# -------------------------------------------------------------------------------------------------
class TreeManagerLabel( TreeViewLabel ) :
	"""

	"""
	font_size = 18



# -------------------------------------------------------------------------------------------------
# screens
class CciScreen( Screen ) :
				"""

				"""

				stop = threading.Event()

				accordion_id = ObjectProperty()
				_console_text = ObjectProperty()
				_console_count = 1


				@staticmethod
				def _retr_resource( resource_id ) :
					"""

					:param resource_id:
					:return ui resource:
					"""

					return resources.const_resource_ids[resource_id]


				def _on_ping_start( self ) :
					"""

					:return:
					"""
					threading.Thread( target = self.ping_thread_exec ,kwargs=dict(func=self.on_ping_ip_input)).start()


				def _on_ping_subnet_start( self ) :
					"""

					:return:
					"""
					App.get_running_app()._thrd = threading.Thread( target = self.ping_thread_exec ,
																	kwargs=dict(func=self.on_ping_ip_subnet) ).start()


				@mainthread
				def move_to_accordion_item( self , acc , tag = None ) :
					"""
					workaround for android nesting bug
					:param acc:
					:return:
					"""

					for child in acc.children :
						if child.title == 'king console' :
							child.collapse = False
							child.canvas.ask_update()

					self.ids.ping_btn.text = "execute"


				def ping_thread_exec( self , func = None ) :
					"""

					:return:
					"""


					if func == self.on_ping_ip_input :
						# update main thread from decorator
						self.move_to_accordion_item( self.ids.cci_accordion ,
																 'ids_ping' )
						self._update_main_console( App.get_running_app()._console_count )
						func()
					elif func == self.on_ping_ip_subnet :
						# update main thread from decorator
						self.move_to_accordion_item( self.ids.cci_accordion ,
																 'ids_ping_subnet' )
						self._update_main_console( App.get_running_app()._console_count , True )




				@mainthread
				def _update_main_console( self , count , threaded = False ) :
					"""

					:return:
					"""



					self.ids.cci_action_prev.title = 'king console(' + str( count ) + ')'

					carousel = self.ids.maelstrom_carousel_id
					layout = GridLayout( cols = 1 ,
										 padding = [0 , 5 , 0 ,5]
										  )
					App.get_running_app()._console_count += 1
					layout.add_widget( Label( text = 'icmp ping console #'  + str( App.get_running_app()._console_count ),
											color = [ 1, 0 , 0 , 1] ,
											font_size = 16 ,
											id = 'content' ,
											size_hint_y = 0.1 ) )

					scrolly = Builder.load_string( self._retr_resource( 'text_scroller' ) )
					tx = scrolly.children[0]
					self._console_text = tx
					tx.text = 'standby...working...'
					layout.add_widget( scrolly )

					layout.add_widget( Label( text = strftime("%Y-%m-%d %H:%M:%S", gmtime()) ,
											font_size = 16  ,
											size_hint_y = 0.2 ,
											color = [ 1, 0 , 0 , 1] ) )


					carousel.add_widget( layout )
					carousel.index = len( carousel.slides ) - 1
					self.canvas.ask_update()

					if threaded :
						self.on_ping_ip_subnet()




				@mainthread
				def _update_console_content( self , content , container ) :
					"""

					:param console slide:

					:return:
					"""

					container.text += content + '\n'
					self.canvas.ask_update()


				def _on_full_screen( self ) :
					"""

					:return:
					"""

					if not App.get_running_app()._full_screen :
						pass


				# icmp handlers
				def on_ping_ip_input( self  , in_ip = None ) :
					"""
					input ping variable
					:return:
					"""

					out = str()
					b_ret = True
					App.get_running_app()._logger.info( self.__class__.__name__ + '...on_ping_ip_input'  )

					ip = str()
					if in_ip is None :
						ip = self.ids.ip_input.text
					else :
						ip = in_ip

					try :

						cmd = ["su" ,
							   "-c" ,
							   "/data/data/com.hipipal.qpyplus/files/bin/qpython.sh" ,
							   "./king_console/kc_ping.pyo" ,
							   "-s" ,
							   ip
							  ]

						try :
							out = proc.check_output( cmd  )
							App.get_running_app()._logger.info( out )
						except proc.CalledProcessError as e :
							b_ret = False
					except Exception as e :
						b_ret = False
						App.get_running_app()._logger.error( e.message )


					boiler = 'maelstrom[icmp]->ping: ' + \
							  ' ' + self.ids.ip_input.text
					boiler += '\n'
					boiler += out
					App.get_running_app()._logger.info( self.__class__.__name__ + '...boiler='  + boiler)

					pos = boiler.find( '#[QPython]' )
					if pos :
						boiler = boiler[:pos]

					if in_ip is None :
						self._console_text.text = boiler

					return boiler



				def on_ping_ip_subnet( self  ) :
					"""
					input ping variable
					:return:
					"""

					# sentinel function so we don't have to use  lock object
					# started at at end of ui update
					threading.Thread( target = self._ping_ip_subnet ).start()




				def _ping_ip_subnet( self ) :
					"""

					:return:
					"""


					App.get_running_app()._logger.info( self.__class__.__name__ + '...on_ping_ip_subnet'  )


					ip = self.ids.ip_subnet_input.text
					prefix = ping.chomp( source_str = ip , delimiter = '.' , keep_trailing_delim = True )

					slide = self.ids.maelstrom_carousel_id.current_slide
					#text box
					container = slide.children[1].children[0]
					container.text = 'working...\n'
					# for each address in subnet
					for addr in range( 0 , 254 ):
						if App.get_running_app().stop_event.isSet() :
							break
						try :

							reply = self.on_ping_ip_input( in_ip=prefix + str( addr ) )
							pos = reply.find( '<reply>' )
							rejoinder = str()
							if pos == -1 :
								rejoinder = 'failed'
							else :
								rejoinder = 'succeeded'

							# have to update main thread by proxy - opengl
							self._update_console_content( prefix + str( addr ) + '... ' + rejoinder , container )
							#container.text += reply + '\n'

							sleep( 0.5 )


						except Exception as err :
							print err



# ------------------------------------------------------------------------------------------------
class BiminiScreen ( Screen ) :

		"""

		"""
		pass


# ------------------------------------------------------------------------------------------------
class LoginScreen ( Screen ) :

		"""

		"""
		pass


# -------------------------------------------------------------------------------------------------
class FullScreen( Screen ) :
		"""

		"""
		_visible = ObjectProperty()

# -------------------------------------------------------------------------------------------------
class ViewManagerScreen( Screen ) :
		"""


		"""


		def __init__( self ) :
			"""

			ctor
			"""

			super( ViewManagerScreen , self ).__init__()



# -------------------------------------------------------------------------------------------------
class ScreenManagement( ScreenManager ) :
		"""


		"""

		transition = SlideTransition()

