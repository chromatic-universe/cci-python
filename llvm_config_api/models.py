from __future__ import unicode_literals

import doctest
from django.db import models

class llvm_build_metadata( models.Model ):
    """
    llvm_build_metadata
    db wrapper llvm_config
    """

    created = models.DateTimeField(auto_now_add=True)
    switch = models.CharField(primary_key=True , max_length=100, blank=False, default='')
    description = models.CharField(max_length=100, blank=False, default='')
    volatile = models.BooleanField(default=False)
    data = models.CharField(max_length=1000, blank=False, default='')

    class Meta:
        ordering = ('created',)
