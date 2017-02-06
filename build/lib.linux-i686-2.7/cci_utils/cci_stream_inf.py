# cci_stream_intf.py    william k. johnson 2016


from abc import ABCMeta , abstractmethod


class cci_stream_intf( object ) :
    """
    abstract stream
    """

    __metaclass__ =  ABCMeta

    def __init__(self) :
        pass


    # -------------------------------------------------------------------------
    @abstractmethod
    def enum_profile_metadata( self , ec2 )  :
        pass


    # -------------------------------------------------------------------------
    @abstractmethod
    def _default_output_handler( self , output ) :
        pass


    # -------------------------------------------------------------------------
    @abstractmethod
    def output_to_list_handler( self , output ) :
        pass


    @abstractmethod
    def output_to_buffer_handler( self , output ) :
        pass


    # -------------------------------------------------------------------------
    @abstractmethod
    def enum_all_profiles( self ) :
        pass


    # -------------------------------------------------------------------------
    @abstractmethod
    def enum_instance_info( self , instance_id = None ) :
        pass