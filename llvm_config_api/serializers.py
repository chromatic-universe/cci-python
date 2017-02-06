__author__ = 'wiljoh'


from rest_framework import serializers
from llvm_config_api.models import llvm_build_metadata


class llvm_build_metadata_serializer( serializers.ModelSerializer ):
    class Meta:
        model = llvm_build_metadata
        fields = ( 'switch', 'description', 'volatile' ,'data' )