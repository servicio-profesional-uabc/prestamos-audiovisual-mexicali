from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

# Create your views here.
def test(request):
    return HttpResponse("OK")