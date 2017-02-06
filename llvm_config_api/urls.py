__author__ = 'wiljoh'


from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from llvm_config_api import views

urlpatterns = [
    url(r'^llvm_config/$', views.llvm_metadata_list.as_view()),
    url(r'^llvm_config/(?P<pk>[0-9]+)/$', views.llvm_metadata_detail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)