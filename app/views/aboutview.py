from django.shortcuts import render
from app.models import Couples

# Create your views here.


def about(request):
    return render(request,'pages/about.html')