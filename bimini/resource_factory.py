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
		background_color: [0,0,0,0]
		foreground_color: [1,1,1,1]
		multiline: True
		font_size: 16
		readonly: True
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
			icon: 'history.png'
			on_press: app._manip_extended_window()
		ActionButton:
			icon: 'menu-icon.png'
			on_press: app._manip_extended_window()
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





