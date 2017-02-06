

# kv resources
const_transport_resource_ids = {
					   'transport_extended_screen' :
"""
TransportScreen:
	id: transport_screen
    name: 'screen_transport'
	GridLayout
		orientation: 'horizontal'
		cols: 1
		Accordion:
			id: tcp_accordion
			orientation: 'vertical'
			AccordionItem:
				title: 'discovery and port manip'
				id: discovery_and_manip
			AccordionItem:
				title: 'nmap firewalk'
				id: nmap_firewalk
				orientation: 'vertical'
			AccordionItem:
				title: 'zombie'
				id: item_zombie_scan
				orientation: 'vertical'
			AccordionItem:
				title: 'cci-maelstrom'
				GridLayout
					orientation: 'horizontal'
					cols: 1
					ActionBar:
						pos_hint: {'top':1}
						ActionView:
							use_separator: True
							ActionPrevious:
								id: cci_action_prev
								title: 'king console'
								with_previous: False
								on_press: root._on_full_screen()
								app_icon: 'king-console32.png'
							ActionButton:
								text: 'history'
								on_press: app._on_view_manager()
							ActionButton:
								text: 'back'
								on_press: app._manip_extended_window()
					Carousel:
                        id: transport_carousel_id
                        direction: 'right'
                        GridLayout:
                            orientation: 'horizontal'
                            id: console_grid
                            cols: 1
                            Label:
                            	text: 'caveat emptor => Post hoc ergo propter hoc'
                            	color: [ 1, 0 , 0 , 1]
								font_size: 16
"""
,
					   'nmap_firewalk_view' :
"""
BoxLayout:
	orientation: 'vertical'
	id: firewalk_nmap
	ScrollView:
		GridLayout:
			id: firewalk_grid
			orientation: 'horizontal'
			size_hint_y: None
			size: ( 480 , 500 )
			cols: 1

			Label:
				text: 'max retries: ' + '{0:}'.format( retry_slider.value )
			Slider:
				orientation: 'horizontal'
				id: retry_slider
				step: 1
				min: 1
				max: 5
				value: 1
			Label:
				text: 'probe timeout(ms): ' + '{0:}'.format( probe_slider.value )
			Slider:
				orientation: 'horizontal'
				id: probe_slider
				step: 20
				min: 0
				max: 800
				value: 0

			Label:
				text: 'recv timeout(ms): ' + '{0:}'.format( probe_recv_slider.value )
			Slider:
				orientation: 'horizontal'
				id: probe_recv_slider
				step: 20
				min: 0
				max: 800
				value: 0

			Label:
				text: 'max ports(-1=all): ' + '{0:}'.format( max_probe_slider.value )
			Slider:
				orientation: 'horizontal'
				id: max_probe_slider
				step: 1
				min: -1
				max: 500
				value: 7
			Button:
				id: do_firewalk_btn
				text: 'execute firewalk'
				background_color: [0,0,0,0]
				color: [1,0,0,1]
			Label:
				text: 'resource metric ip:'
			TextInput:
				text: 'cci-aws-1'
				id: ip_input_metric
				cursor_blink: True
				readonly: False
				multiline: True



"""
,
							   		 'zombie_view' :
"""
BoxLayout
	orientation: 'vertical'
	id: zombie_walk
	GridLayout
		orientation: 'horizontal'
		id: zombie_grid
		cols: 1
		Button:
			id: do_zombie_btn
			text: 'query zombie'
			background_color: [0,0,0,0]
			color: [1,0,0,1]
			size_hint_y: 0.15
	    Label:
			text: 'zombie scan target:'
			size_hint_y: 0.15
		TextInput:
			text: '173.167.195.34'
			id: ip_zombie_metric
			size_hint_y: 0.15
			cursor_blink: True
			readonly: False
			multiline: False
		Label:
			id: zombie_query_tx
			text: 'target not probed'
			size_hint_y: 0.15
	BoxLayout
		orientation: 'horizontal'
"""
,
 				'text_scroller' :
"""
ScrollView:
	id: scrlv
	TextInput:
		text: 'foo'
		size_hint: 1, None
		cursor_blink: True
		background_color: [1,0,0,0]
		foreground_color: [1,1,1,1]
		multiline: True
		id: tx_in
		font_size: 16
		readonly: True
		height: max( (len(self._lines)+1) * self.line_height, scrlv.height)
"""
,
}

