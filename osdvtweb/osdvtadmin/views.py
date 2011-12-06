#from django.shortcuts import render_to_response

#def index(request):
#    return render_to_response("index.html", {'nome': 'Amador'})

from osdvtweb.osdvtadmin.models import *
from djangorestframework.views import View
class VM(View):
    def get(self, request):
        return {'nome': 'Amador'}
