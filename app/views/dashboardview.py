from django.shortcuts import render,redirect
from app.models import Biodata,Like,Interest
from django.contrib import messages
from django.db.models import Count

def dashboard(request):
    user_id = request.user.id
    try:
        # Get the user's biodata
        biodata = Biodata.objects.get(user_id=user_id)
        
        # Get the number of likes for the user's biodata
        num_likes = Like.objects.filter(biodata=biodata).count()
        
        # Get the number of interested profiles (interest_status is 'Interested')
        num_interests = Interest.objects.filter(biodata=biodata).count()

        # interested profile
        interested = Interest.objects.filter(biodata=biodata)
        interested_profile = []
        for i in interested:
            user = Biodata.objects.get(id=i.user_id)
            interested_profile.append(user)
        print('here',interested)
        
        context = {
            'biodata': biodata,
            'user': request.user,
            'phone': request.user.phone,
            'email': request.user.email,
            'name': request.user.name,
            'num_likes': num_likes,  # Number of likes received
            'num_interests': num_interests,  # Number of interested profiles
            'interested_profile': interested_profile
        }
        
        return render(request, 'pages/dashboard.html', context)
    
    except Biodata.DoesNotExist:
        messages.warning(request, 'Please add your biodata first')
        return redirect('biodata')

def dashboardprofile(request):
    user = request.user.id
    print(user)
    try:
        biodata = Biodata.objects.get(user_id=user)
        print(biodata.age)
        context={'biodata':biodata,
                'user':user,
                'phone':request.user.phone,
                'email':request.user.email,
                'name':request.user.name
                }
        return render(request,'pages/dashboard_profile.html',context)
    except Exception as e:
        messages.warning(request,'Please add your biodata first')
        return redirect('biodata')
    
def dashboardsetting(request):
    user = request.user.id
    print(user)
    try:
        biodata = Biodata.objects.get(user_id=user)
        print(biodata.age)
        context={'biodata':biodata,
                'user':user,
                'phone':request.user.phone,
                'email':request.user.email,
                'name':request.user.name
                }
        return render(request,'pages/dashboard_setting.html',context)
    except Exception as e:
        messages.warning(request,'Please add your biodata first')
        return redirect('biodata')
    