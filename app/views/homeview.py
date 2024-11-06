from django.shortcuts import render
from app.models import Couples
from app.models import City,Religion,Blog

# Create your views here.

def home(request):
    couples = Couples.objects.all()
    cities = City.objects.all()
    religions = Religion.objects.all()
    blog = Blog.objects.all().order_by('-id')[:3]
    context = {'couples':couples,'cities':cities,'religions':religions,'blog':blog}

    print(request.user)
    return render(request,'pages/home.html',context)


def service(request):
    return render(request,'pages/services.html')

