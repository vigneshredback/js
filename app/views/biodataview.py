from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from app.forms import BiodataForm,Biodata,BiodataUpdateForm
from datetime import date
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from app.models import Biodata,City,Religion,Like,Interest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from app.models import Like, Biodata, Plan
from app.serializers import LikeSerializer
from django.db.models import Count


def create_biodata(request):
    if request.method == 'POST':
        form = BiodataForm(request.POST, request.FILES)
        if form.is_valid():
            biodata = form.save(commit=False)
            biodata.user = request.user
            biodata.save()

            # Redirect the user to the plan selection page after creating biodata
            messages.success(request, "Biodata created successfully! Please select a plan.")
            return redirect('plan')  # Redirect to plan selection page
        else:
            print(form.errors)
    else:
        form = BiodataForm()
    messages.info(request, "Create your biodata first")
    return render(request, 'pages/biodata_form.html', {'form': form})


def select_plan(request):
    plan1 = Plan.objects.get(name='free')  # Retrieve all plans (free and premium)
    print(plan1)
    plan2 = Plan.objects.get(name='premium')  # Retrieve all plans (free and premium)
    print(plan2)
    if request.method == 'POST':
        selected_plan_id = request.POST.get('plan_id')
        selected_plan = Plan.objects.get(id=selected_plan_id)
        biodata = Biodata.objects.get(user=request.user)  # Get biodata for the current user
        
        # Associate the selected plan with the biodata
        biodata.plan = selected_plan
        biodata.save()

        messages.success(request, f"You have selected the {selected_plan.name} plan!")
        return redirect('home')  # Redirect to home page or another page after selection

    return render(request, 'pages/plans.html', {'plan1': plan1, 'plan2': plan2})

def calculate_age(birthdate):
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

@login_required(login_url='login')
def allprofiles(request):
    # Check if the user has a biodata and if the plan is not selected
    try:
        user_biodata = Biodata.objects.get(user=request.user)
        if user_biodata.plan is None:  # Check if the plan is not selected
            messages.info(request, "Please select a plan to view profiles.")
            return redirect('plan')  # Redirect to the plan selection page
    except Biodata.DoesNotExist:
        # Handle the case where the user does not have a biodata yet
        messages.warning(request, "You need to create a biodata first.")
        return redirect('biodata')

    # Continue with normal profile listing logic if the plan is selected
    profiles = Biodata.objects.filter(admin_approval=True)
    cities = City.objects.all()
    religions = Religion.objects.all()
    context = {'cities': cities, 'religions': religions}
    totalprofiles = profiles.count()

    paginator = Paginator(profiles, 5)  # 5 profiles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check if request is AJAX
        profiles_data = []
        for profile in page_obj:
            # Check if the user has liked this profile
            user_has_liked = Like.objects.filter(user=request.user, biodata=profile).exists()
            # Check if the user has interest this profile
            user_has_interest = Interest.objects.filter(user=request.user, biodata=profile).exists()

            profiles_data.append({
                'id': profile.id,
                'gender': profile.gender,
                'name': profile.user.name,  # Assuming `user` is a ForeignKey in `Biodata`
                'degree': profile.degree,
                'profession': profile.profession,
                'age': profile.age,
                'height': profile.height,
                'image1': profile.image1.url if profile.image1 else '',  # Convert ImageField to URL
                'user_has_liked': user_has_liked,  # Add like status to the data
                'user_has_interest': user_has_interest,  # Add like status to the data,
                'plan_id': profile.plan_id
            })
        
        data = {
            'profiles': profiles_data,
            'has_next': page_obj.has_next(),
        }
        if totalprofiles < 5:
            return JsonResponse('no data', safe=False)
        return JsonResponse(data)


    # Pass the same data for HTML response
    for profile in page_obj:
        profile.user_has_liked = Like.objects.filter(user=request.user, biodata=profile).exists()
        profile.user_has_interest = Interest.objects.filter(user=request.user, biodata=profile).exists()

    return render(request, 'pages/allprofiles.html', {
        'profiles': page_obj,
        'totalprofiles': totalprofiles,
        'cities': cities,
        'religions': religions
    })


# @login_required(login_url='login')
# def searchprofile(request):
#     # Check if the user has a biodata and if the plan is not selected
#     try:
#         user_biodata = Biodata.objects.get(user=request.user)
#         if user_biodata.plan is None:  # Check if the plan is not selected
#             messages.info(request, "Please select a plan to search profiles.")
#             return redirect('plan')  # Redirect to the plan selection page
#     except Biodata.DoesNotExist:
#         # Handle the case where the user does not have a biodata yet
#         messages.warning(request, "You need to create a biodata first.")
#         return redirect('create_biodata')

#     # Continue with the normal search logic if the plan is selected
#     if request.method == 'POST' or request.method == 'GET':
#         # Retrieve filters from request
#         gender = request.GET.get('gender', 'all') if request.method == 'GET' else request.POST.get('gender', 'all')
#         age = request.GET.get('age', 'all') if request.method == 'GET' else request.POST.get('age', 'all')
#         city = request.GET.get('city', 'all') if request.method == 'GET' else request.POST.get('city', 'all')
#         religion = request.GET.get('religion', 'all') if request.method == 'GET' else request.POST.get('religion', 'all')
#         profile_type = request.GET.get('profile_type') if request.method == 'GET' else request.POST.get('profile_type')

#         cities = City.objects.all()
#         religions = Religion.objects.all()

#         # Start with the base queryset
#         profiles = Biodata.objects.filter(admin_approval=True)
        

#         print(profile_type)
#         message = 'you are viewing all profiles'

#         # Apply profile type filter
#         if profile_type == 'premium':
#             profiles = profiles.filter(plan_id=1)
#             message = 'you are viewing premium profiles'
#         elif profile_type == 'free':
#             profiles = profiles.filter(plan_id=2)
#             message = 'you are viewing free profiles'
        

#         # Apply filters
#         if gender != 'all':
#             profiles = profiles.filter(gender=gender)

#         if age != 'all':
#             if age == '1':
#                 profiles = profiles.filter(age__gte=18, age__lte=30)
#             elif age == '2':
#                 profiles = profiles.filter(age__gte=31, age__lte=40)
#             elif age == '3':
#                 profiles = profiles.filter(age__gte=41, age__lte=50)

#         if city != 'all':
#             profiles = profiles.filter(city__name=city)

#         if religion != 'all':
#             profiles = profiles.filter(religion__name=religion)

#         # Count the total profiles
#         totalprofiles = profiles.count()

#         # Implement pagination, displaying 5 profiles per page
#         paginator = Paginator(profiles, 5)
#         page_number = request.GET.get('page', 1)
#         page_obj = paginator.get_page(page_number)

#         # Initialize `user_has_liked` to avoid UnboundLocalError
#         user_has_liked = False

#         # Prepare profiles data for the JSON response
#         profiles_data = []
#         for profile in page_obj:
#             user_has_liked = Like.objects.filter(user=request.user, biodata=profile).exists()
#             user_has_interest = Interest.objects.filter(user=request.user, biodata=profile).exists()
#             profiles_data.append({
#                 'id': profile.id,
#                 'gender': profile.gender,
#                 'name': profile.user.name,
#                 'degree': profile.degree,
#                 'profession': profile.profession,
#                 'age': profile.age,
#                 'height': profile.height,
#                 'image1': profile.image1.url if profile.image1 else '',
#                 'user_has_liked': user_has_liked,
#                 'user_has_interest': user_has_interest
#             })
        


#         # Handle AJAX requests for infinite scroll
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             data = {
#                 'profiles': profiles_data,
#                 'has_next': page_obj.has_next(),  # Check if more profiles exist
#             }
#             print(data)
#             if totalprofiles < 5:
#                 return JsonResponse('no data', safe=False)
#             return JsonResponse(data)
        
#         # Pass the same data for HTML response
#         for profile in page_obj:
#             profile.user_has_liked = Like.objects.filter(user=request.user, biodata=profile).exists()
#             profile.user_has_interest = Interest.objects.filter(user=request.user, biodata=profile).exists()

#         # Regular non-AJAX response for initial page load
#         # messages.success(request, message)
#         return render(request, 'pages/filteredprofiles.html', {
#             'profiles': page_obj,
#             'profile_type': profile_type,
#             'totalprofiles': totalprofiles,
#             'gender': gender,
#             'age': age,
#             'city': city,
#             'religion': religion,
#             'cities': cities,
#             'religions': religions,
#             'user_has_liked': user_has_liked,  # Pass a default value for user_has_liked
#             'user_has_interest': user_has_interest
#         })

#     return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required(login_url='login')
def searchprofile(request):
    # Check if the user has a biodata and if the plan is not selected
    try:
        user_biodata = Biodata.objects.get(user=request.user)
        if user_biodata.plan is None:
            messages.info(request, "Please select a plan to search profiles.")
            return redirect('plan')
    except Biodata.DoesNotExist:
        messages.warning(request, "You need to create a biodata first.")
        return redirect('create_biodata')

    user_has_liked = False  # Initialize default value
    user_has_interest = False  # Initialize default value

    # Continue with the normal search logic if the plan is selected
    if request.method in ['POST', 'GET']:
        gender = request.GET.get('gender', 'all') if request.method == 'GET' else request.POST.get('gender', 'all')
        age = request.GET.get('age', 'all') if request.method == 'GET' else request.POST.get('age', 'all')
        city = request.GET.get('city', 'all') if request.method == 'GET' else request.POST.get('city', 'all')
        religion = request.GET.get('religion', 'all') if request.method == 'GET' else request.POST.get('religion', 'all')
        profile_type = request.GET.get('profile_type') if request.method == 'GET' else request.POST.get('profile_type')

        cities = City.objects.all()
        religions = Religion.objects.all()

        profiles = Biodata.objects.filter(admin_approval=True)
        message = 'you are viewing all profiles'

        # Apply profile type filter
        if profile_type == 'premium':
            profiles = profiles.filter(plan_id=1)
            message = 'you are viewing premium profiles'
        elif profile_type == 'free':
            profiles = profiles.filter(plan_id=2)
            message = 'you are viewing free profiles'

        # Apply filters
        if gender != 'all':
            profiles = profiles.filter(gender=gender)

        if age != 'all':
            if age == '1':
                profiles = profiles.filter(age__gte=18, age__lte=30)
            elif age == '2':
                profiles = profiles.filter(age__gte=31, age__lte=40)
            elif age == '3':
                profiles = profiles.filter(age__gte=41, age__lte=50)

        if city != 'all':
            profiles = profiles.filter(city__name=city)

        if religion != 'all':
            profiles = profiles.filter(religion__name=religion)

        totalprofiles = profiles.count()
        paginator = Paginator(profiles, 5)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        profiles_data = []
        for profile in page_obj:
            user_has_liked = Like.objects.filter(user=request.user, biodata=profile).exists()
            user_has_interest = Interest.objects.filter(user=request.user, biodata=profile).exists()
            profiles_data.append({
                'id': profile.id,
                'gender': profile.gender,
                'name': profile.user.name,
                'degree': profile.degree,
                'profession': profile.profession,
                'age': profile.age,
                'height': profile.height,
                'plan': profile.plan_id,
                'image1': profile.image1.url if profile.image1 else '',
                'user_has_liked': user_has_liked,
                'user_has_interest': user_has_interest
            })

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'profiles': profiles_data,
                'has_next': page_obj.has_next(),
            }
            if totalprofiles < 5:
                return JsonResponse('no data', safe=False)
            return JsonResponse(data)

        # Pass the same data for HTML response
        for profile in page_obj:
            profile.user_has_liked = Like.objects.filter(user=request.user, biodata=profile).exists()
            profile.user_has_interest = Interest.objects.filter(user=request.user, biodata=profile).exists()

        return render(request, 'pages/filteredprofiles.html', {
            'profiles': page_obj,
            'profile_type': profile_type,
            'totalprofiles': totalprofiles,
            'gender': gender,
            'age': age,
            'city': city,
            'religion': religion,
            'cities': cities,
            'religions': religions,
            'user_has_liked': user_has_liked,
            'user_has_interest': user_has_interest
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def profile_detail(request, pk):
    try:
        # Annotate the profile with the number of likes
        profile = Biodata.objects.annotate(like_count=Count('likes')).get(pk=pk)
        profile.age = calculate_age(profile.date_of_birth)

        # Annotate recommended profiles with their like count and calculate age
        recommended_profiles = Biodata.objects.annotate(like_count=Count('likes')).filter(city=profile.city, gender=profile.gender).exclude(id=pk)[:4]
        
        for rec_profile in recommended_profiles:
            rec_profile.age = calculate_age(rec_profile.date_of_birth)

        return render(request, 'pages/profile_detail.html', {
            'profile': profile, 
            'recommended_profiles': recommended_profiles
        })
    except Biodata.DoesNotExist:
        messages.warning(request, "Create your profile first")
        return redirect('biodata')

def biodata_update_view(request):
    user_id = request.user.id

    try:
        # Try to get the existing Biodata object for the logged-in user
        biodata = Biodata.objects.get(user_id=user_id)
    except Biodata.DoesNotExist:
        # Handle the case where the Biodata object does not exist
        biodata = None
        messages.error(request, "Biodata does not exist.")
        return redirect('biodata')  # Redirect to an error page or some other page

    # If a Biodata object exists, continue with the form handling
    if request.method == 'POST':
        form = BiodataUpdateForm(request.POST, request.FILES, instance=biodata)
        if form.is_valid():
            print('Form is valid')
            form.save()
            messages.success(request, "Biodata updated successfully!")
            return redirect('home')  # Redirect to a success page
        else:
            print('Form is not valid')
            messages.error(request, "Error updating biodata. Please try again.")
    else:
        # GET request: Display the form with the current Biodata instance
        form = BiodataUpdateForm(instance=biodata)

    return render(request, 'pages/biodata_update.html', {'form': form})

from django.views.decorators.http import require_POST
class LikeToggleView(APIView):
    def post(self, request, pk, *args, **kwargs):
        user = request.user
        biodata = get_object_or_404(Biodata, pk=pk)
        
        # Check if the user already liked this Biodata
        like = Like.objects.filter(user=user, biodata=biodata).first()
        
        if like:
            # User already liked, remove the like (unlike)
            like.delete()
            liked = False
        else:
            # Add a new like
            Like.objects.create(user=user, biodata=biodata)
            liked = True

        # Return the like status (True for liked, False for unliked)
        
        return Response({"liked": liked}, status=status.HTTP_200_OK)
    

class InterestToggleView(APIView):
    def post(self, request, pk, *args, **kwargs):
        user = request.user
        biodata = get_object_or_404(Biodata, pk=pk)
        
        # Check if the user already Interested in  this Biodata
        interest = Interest.objects.filter(user=user, biodata=biodata).first()
        
        if interest:
            # User already liked, remove the like (unlike)
            interest.delete()
            interested = False
        else:
            # Add a new Interest
            Interest.objects.create(user=user, biodata=biodata)
            interested = True

        # Return the Interest status (True for liked, False for unliked)
        
        return Response({"interested": interested}, status=status.HTTP_200_OK)