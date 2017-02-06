# resource_factory.py    william k. johnson   2016


from time import gmtime, strftime , sleep


log_format = '%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s'




# kv resources
const_resource_ids = { 'text_scroller' :
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
					   'note_scroller' :
"""
ScrollView:
	id: scrlv
	TextInput:
		text: ''
		size_hint: 1, None
		cursor_blink: True
		#foreground_color: [0,0,0,0]
		#background_color: [1,1,1,1]
		multiline: True
		id: tx_in
		font_size: 16
		readonly: False
		height: max( (len(self._lines)+1) * self.line_height, scrlv.height)
"""
,
				       'action_bar' :
"""
ActionBar:
	pos_hint: {'top':1}
	ActionView:
		use_separator: True
		ActionPrevious:
			title: 'king console'
			with_previous: False
			app_icon: 'king-console32.png'
			on_press: app._manip_extended_window()
		ActionButton:
			text: 'back'
			on_press: app._manip_extended_window()
"""
,
	       'action_bar_plus' :
"""
ActionBar:
	pos_hint: {'top':1}
	ActionView:
		use_separator: True
		ActionPrevious:
			title: 'king console'
			with_previous: False
			app_icon: 'king-console32.png'
			on_press: app._manip_extended_window()
		ActionButton:
			text: 'back'
			on_press: app._manip_extended_window()
		ActionButton:
			text: 'expand'
			id: view_btn_b
			on_press: app._toggle_tree_view_manager_nodes( view_btn_b )


"""

,
				       'dlg_action_bar' :
"""
ActionBar:
	pos_hint: {'top':1}
	ActionView:
		use_separator: True
		ActionPrevious:
			title: 'king console'
			with_previous: False
			app_icon: 'king-console32.png'
		ActionButton:
			text: 'notes'

"""
,
 					 'dlg_action_bar_2' :
"""
ActionBar:
	pos_hint: {'top':1}
	ActionView:
		use_separator: True
		ActionPrevious:
			title: 'king console'
			with_previous: False
			app_icon: 'king-console32.png'
"""
,
 					 'dlg_action_bar_3' :
"""
ActionBar:
	id: action_bar
	pos_hint: {'top':1}
	ActionView:
	    id: action_view
		use_separator: True
		ActionPrevious:
			title: 'king console'
			with_previous: False
			app_icon: 'king-console32.png'
		ActionButton:
			text: 'manip'
			id: view_btn_a
"""
,
					   'application_acc_item' :
"""
Accordion:
    orientation: 'horizontal'
    AccordionItem:
        title: 'dns query'
    AccordionItem:
        title: 'ssh verify'
"""
,
					   'list_scrollview' :
"""
ScrollView:
	ListView:
		id: list_view_id
		size_hint_y: .75
		adapter:
			la.ListAdapter(
			data=["cci #{0}".format(i) for i in xrange(30)],
			selection_mode='single',
			allow_empty_selection=False,
			cls=lv.ListItemButton)
"""
,
				       'datalink_extended_screen' :
"""
Screen
    id: datalink_screen
    name: 'screen_datalink'
    GridLayout
        orientation: 'horizontal'
        cols: 1
        Accordion:
            id: datalink_accordion
            orientation: 'vertical'
            AccordionItem:
                title: 'arp monitor'
"""
,

					   'network_extended_screen' :
"""
Screen
    id: datalink_screen
    name: 'screen_network'
    GridLayout
        orientation: 'horizontal'
        cols: 1
        Accordion:
            id: network_accordion
            orientation: 'vertical'

"""
,

					   'console_carousel' :
"""
Carousel:
	id: carousel_id
	direction: 'right'
	GridLayout:
		orientation: 'horizontal'
		id: console_grid
		cols: 1
		pos_hint: {'top':1}
		ScrollView:
			id: console_scrlv
			TextInput:
				text: 'cci_maelstrom->arp-monitor-> '
				id: console_arp_monitor
				size_hint: 1, None
				cursor_blink: True
				background_color: [0,0,0,0]
				foreground_color: [1,1,1,1]
				multiline: True
				font_size: 16
				readonly: True
				height: max( (len(self._lines)+1) * self.line_height, console_scrlv.height)
"""
}

# json
settings_json='''
[
    {
        "type": "title",
        "title": "stream"
    },
    {
        "type": "numeric",
        "title": "reply packet timeout",
        "desc": "reply timeout(seconds)",
        "section": "stream",
        "key": "packet_timeout"
    },
    {
        "type": "bool",
        "title": "show output stream",
        "desc": "open display",
        "section": "stream",
        "key": "show_stream"
    },
    {
        "type": "title",
        "title": "network-icmp"
    },{
        "type": "numeric",
        "title": "reply packet timeout",
        "desc": "reply timeout(seconds)",
        "section": "network-icmp",
        "key": "packet_timeout"
    },
    {
        "type": "bool",
        "title": "show output stream",
        "desc": "open display",
        "section": "network-icmp",
        "key": "show_stream"
    },
    {
        "type": "string",
        "title": "default address",
        "desc": "default address or ip",
        "section": "network-icmp",
        "key": "default_address"
    }
]
'''
settings_env_json='''
[
    {
        "type": "title",
        "title": "stream"
    },
    {
        "type": "numeric",
        "title": "reply packet timeout",
        "desc": "reply timeout(seconds)",
        "section": "stream",
        "key": "packet_timeout"
    },
    {
        "type": "bool",
        "title": "show output stream",
        "desc": "open display",
        "section": "stream",
        "key": "show_stream"
    },
    {
        "type": "title",
        "title": "network-icmp"
    },{
        "type": "numeric",
        "title": "reply packet timeout",
        "desc": "reply timeout(seconds)",
        "section": "network-icmp",
        "key": "packet_timeout"
    },
    {
        "type": "bool",
        "title": "show output stream",
        "desc": "open display",
        "section": "network-icmp",
        "key": "show_stream"
    },
    {
        "type": "string",
        "title": "default address",
        "desc": "default address or ip",
        "section": "network-icmp",
        "key": "default_address"
    }
]
'''
settings_stream_json='''
[
    {
        "type": "title",
        "title": "stream"
    },
    {
        "type": "numeric",
        "title": "reply packet timeout",
        "desc": "reply timeout(seconds)",
        "section": "stream",
        "key": "packet_timeout"
    },
    {
        "type": "bool",
        "title": "show output stream",
        "desc": "open display",
        "section": "stream",
        "key": "show_stream"
    },
    {
        "type": "title",
        "title": "network-icmp"
    },{
        "type": "numeric",
        "title": "reply packet timeout",
        "desc": "reply timeout(seconds)",
        "section": "network-icmp",
        "key": "packet_timeout"
    },
    {
        "type": "bool",
        "title": "show output stream",
        "desc": "open display",
        "section": "network-icmp",
        "key": "show_stream"
    },
    {
        "type": "string",
        "title": "default address",
        "desc": "default address or ip",
        "section": "network-icmp",
        "key": "default_address"
    }
]
'''





