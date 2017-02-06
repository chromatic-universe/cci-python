from llvm_metadata.models import llvm_build_metadata
from llvm_metadata.serializers import llvm_build_metadata_serializer
from rest_framework import mixins
from rest_framework import generics


class llvm_metadata_list( generics.ListCreateAPIView ):
    """
    list all llvm build machines , or create a new machine entry
    """
    queryset = llvm_build_metadata.objects.all()
    serializer_class = llvm_build_metadata_serializer


class llvm_metadata_detail( generics.RetrieveUpdateDestroyAPIView ):
    """
    retrieve, update or delete a machine entry.
    """
    queryset = llvm_build_metadata.objects.all()
    serializer_class = llvm_build_metadata_serializ