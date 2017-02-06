# tr_trinity.py    william k. johnson  2016

import os
import subprocess as proc
import StringIO
import sys
import Queue



click_queue = Queue.Queue()
key_queue = Queue.Queue()

key_motions = {
				'key_down' : 0 ,
				'key_up' : 1
			  }

# ---------------------------------------------------------------------
def process_linux_clicks( log=None  ) :
			"""
			:param log:
			:param q:
			:return:
			"""


			import pyautogui
			try:

				while not click_queue.empty() :
					x , y = click_queue.get()
					log.info( '..remote click....x%d:y%d'  % ( x , y  ) )
					currentMouseX, currentMouseY = pyautogui.position()
					log.info( '.local mouse....x%d:y%d'  % ( 	currentMouseX , currentMouseY ) )
					pyautogui.moveTo( x , y )
					pyautogui.click()
			except Exception as e :
				log.error( '...click....'  )
				log.error( e.message )
				return 'error'

			return 'done'




# ---------------------------------------------------------------------
def process_android_clicks( log=None  ) :
			"""
			:param log:
			:return:
			"""


			try:

				while not click_queue.empty() :
					x , y = click_queue.get()
					log.info( '..remote click....x%d:y%d'  % ( x , y  ) )
					cmd = [ 'su' , '-c' , '/system/bin/orng' ,
							'-t' ,
							'/dev/input/event3' ,
							str( x )  ,
							str( y ) ]
					out = proc.check_output( cmd )
					log.info( out )

			except proc.CalledProcessError as e :
				log.error( e.message )
			except Exception as e :
				log.error( '...click....'  )
				log.error( e.message )
				return 'error'

			return 'done'


# ---------------------------------------------------------------------
def process_android_keys( log=None , key_motion = 'key_down' ) :
			"""
			:param log:
			:return:
			"""


			try:
				motion =  '-k'
				if key_motions[key_motion] :
					motion = '-u'

				while not key_queue.empty() :

					key = key_queue.get()
					log.info( '..remote key....%d' % key  )

					cmd = [ 'su' ,
							'-c' ,
							'/system/bin/orng' ,
							'-k' ,
							'/dev/input/event3' ,
							str( key )  ,
							'0' ]
					out = proc.check_output( cmd )
					log.info( out )

			except Exception as e :
				log.error( '...keys....'  )
				log.error( e.message )
				return 'error'

			return 'done'



# ---------------------------------------------------------------------
def process_linux_keys( log=None , key_motion = 'key_down' ) :
			"""
			:param log:
			:return:
			"""

			import pyautoguid
			try:

				motion =  '-k'
				if key_motions[key_motion] :
					motion = '-u'


				while not key_queue.empty() :

					key = key_queue.get()

					log.info( '..remote key....%d' % key  )
					pyautogui.keyDown( chr( key ) , 0.15 )

			except Exception as e :
				log.error( '...keys....'  )
				log.error( e.message )
				return 'error'

			return 'done'


# ---------------------------------------------------------------------
def platform( log=None ) :
            """

            :return string platform id:
            """

            ret = None
            try :
                cmd = ['busybox' , 'uname' , '-a' ]
                out = proc.check_output( cmd )

                pos = out.find( 'armv7' )
                if pos == -1 :
                    ret = 'linux'
                else : 
                    ret = 'android'

            except :
                return None

            return ret

                
    


# ---------------------------------------------------------------------
def capture_screen( log=None ) :
            """
            :param path to saved image:
            :return
            """


            b_ret = False
            out = str()
            buf = None

            try :
                    p = platform( log )
                    if not platform :
                        log.error( '...could not determine platform...'  )
                        return 
                    
                    if p == 'android' :
                        
                        process_android_clicks( log=log )
                        process_android_keys( log=log )
                        out = proc.check_output( ['su' ,
                                                  '-c' , 
                                                  '/system/bin/screencap' , 
                                                  '-p' ] )                        
                        b_ret = True                                                

                    elif p == 'linux' :
                        # linux
                        import pyscreenshot as ImageGrab

                        process_linux_clicks( log=log )
                        process_linux_keys( log=log )
                        screen = ImageGrab.grab()
                        buf = StringIO.StringIO()
                        screen.save( buf , 'PNG', quality=75)
                        buf.seek( 0 )

                        b_ret = True
                        return b_ret , buf.getvalue()

            except proc.CalledProcessError as e :
                    # this throws if the function call was
                    # made and failed. If the binary was
                    # not found we get a naked system exception ,
                    # handled next
                    log.error( e.message  )
                    return b_ret , e.message
            except Exception as e :
                    log.error( '..error in tr_bimini...'  )
                    out = e.message
            finally :
                    if buf :
                        buf.close()

            return b_ret , out




# ---------------------------------------------------------------------
def capture_clicks( log=None  , request = None ) :
			"""
			:param log:
			:return:
			"""

			log.info( '...capture_clicks....' )
			x = int( request.args.get('x') )
			y = int( request.args.get('y') )
			clk = ( x , y )

			click_queue.put( clk )

			return 'done'



# ---------------------------------------------------------------------
def capture_keys( log=None  , request = None ) :
			"""

			:param log:
			:param request:
			:return:
			"""

			log.info( '...capture_keys....' )
			k = int( request.args.get( 'key' ) )

			key_queue.put( k )

			return 'done'



# ------------------------------------------------------------------------------
if __name__ == "__main__" :

			capture_screen()
