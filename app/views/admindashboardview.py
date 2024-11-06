from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from app.forms import BiodataForm,UserRegistrationForm
from django.contrib import messages
from app.models import Biodata,User,City,Religion,Like,Plan
from django.core.paginator import Paginator
from django.http import JsonResponse
from app.serializers import BiodataSerializer
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST



# Create your views here.


@login_required(login_url='login')
def adminhome(request):
    if request.user.is_admin:
        newusers = Biodata.objects.filter(admin_approval=False).count()
        totalusers = Biodata.objects.all().count()
        free_users = Biodata.objects.filter(plan=1).count()
        premium_users = Biodata.objects.filter(plan=2).count()
        recentusers = Biodata.objects.all().order_by('-id')[:5]
        return render(request,'adminpages/adminhome.html',{'newusers': newusers,'totalusers': totalusers,'free_users': free_users,'premium_users': premium_users,'recentusers': recentusers})
    else:
        return redirect('home')
    
# @login_required(login_url='login')
# def adminadduser(request):
#     if request.user.is_admin:
#         if request.method == 'POST':
#             newuser = None
#             userform = UserRegistrationForm(request.POST)
#             if userform.is_valid():
#                 # Save the user without committing first to handle password
#                 user = userform.save(commit=False)
#                 user.set_password(userform.cleaned_data['password'])
#                 user.save()
#                 newuser = user
#             form = BiodataForm(request.POST, request.FILES)
#             print(form)
#             if form.is_valid():
#                 biodata = form.save(commit=False)
#                 biodata.user = newuser
#                 id  = Biodata.objects.latest('id').id
#                 biodata.user_id = id + 1
#                 biodata.save()
#                 messages.success(request,"Biodata created successfully!")
#                 return redirect('adminhome')
#             else:
#                 print(form.errors)
#         else:
#             form = BiodataForm()
#             userform = UserRegistrationForm()
#         messages.info(request,"Create your biodata first")
#         return render(request,'adminpages/adduser.html', {'form': form, 'userform': userform})
#     else:
#         return redirect('home')

@login_required(login_url='login')
def adminadduser(request):
    if request.user.is_admin:
        if request.method == 'POST':
            newuser = None
            userform = UserRegistrationForm(request.POST)
            
            # Check if the user form is valid
            if userform.is_valid():
                # Save the user without committing to handle the password
                user = userform.save(commit=False)
                user.set_password(userform.cleaned_data['password'])  # Set the password correctly
                user.save()
                newuser = user  # Store the newly created user
                
                # Debugging print to ensure user is saved
                print("User created:", newuser)
            else:
                print("User form errors:", userform.errors)  # Print form errors if invalid
            
            form = BiodataForm(request.POST, request.FILES)
            
            # Ensure newuser is not None before assigning to biodata
            if form.is_valid() and newuser:
                biodata = form.save(commit=False)
                biodata.user = newuser  # Assign the newly created user to biodata.user
                biodata.save()
                messages.success(request, "Biodata created successfully!")
                return redirect('adminhome')
            else:
                # Debugging print to see any form errors
                print("Biodata form errors:", form.errors)
        else:
            form = BiodataForm()
            userform = UserRegistrationForm()
        return render(request, 'adminpages/adduser.html', {'form': form, 'userform': userform})
    else:
        return redirect('home')



# @login_required(login_url='login')
def adminregister(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user without committing first to handle password
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')  # Redirect to login or any other page after successful registration
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

@login_required(login_url='login')
def adminalluser(request):
    if request.user.is_admin:
        email = request.GET.get('email', '')
        biodata = Biodata.objects.all()

        # Filter by email if the email parameter is present
        if email:
            biodata = biodata.filter(user__email__icontains=email)

        # Implement pagination, displaying 15 profiles per page
        paginator = Paginator(biodata, 15)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Check if the request is AJAX for search or pagination
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            users_data = []
            for biodata_item in page_obj:
                users_data.append({
                    'id': biodata_item.id,
                    'name': biodata_item.user.name,
                    'email': biodata_item.user.email,
                    'phone': biodata_item.user.phone,
                    'plan': biodata_item.plan.name,
                    'city': biodata_item.city.name if biodata_item.city else '',
                    'date_of_birth': biodata_item.date_of_birth.strftime('%Y-%m-%d') if biodata_item.date_of_birth else '',
                    'admin_approval': biodata_item.admin_approval
                })
            
            data = {
                'users': users_data,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages
            }
            return JsonResponse(data)

        # Regular render for non-AJAX requests
        return render(request, 'adminpages/adminallusers.html', {
            'page_obj': page_obj
        })

    else:
        return redirect('home')

@login_required(login_url='login')
def toggle_approvals(request, user_id):
    if request.method == 'POST' and request.user.is_admin:
        try:
            biodata_item = Biodata.objects.get(id=user_id)
            biodata_item.admin_approval = not biodata_item.admin_approval  # Toggle approval status
            biodata_item.save()
            print(biodata_item.admin_approval)
            return JsonResponse({
                'status': 'success',
                'new_approval_status': biodata_item.admin_approval
            })
        except Biodata.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

@login_required(login_url='login')
def adminfreeuser(request):
    if request.user.is_admin:
        email = request.GET.get('email', '')
        biodata = Biodata.objects.filter(plan=1)
        print(biodata)

        # Filter by email if the email parameter is present
        if email:
            biodata = biodata.filter(user__email__icontains=email )

        # Implement pagination, displaying 5 profiles per page
        paginator = Paginator(biodata, 15)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Check if the request is AJAX for search or pagination
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            users_data = []
            for biodata_item in page_obj:
                users_data.append({
                    'id': biodata_item.id,
                    'name': biodata_item.user.name,
                    'email': biodata_item.user.email,
                    'phone': biodata_item.user.phone,
                    'plan': biodata_item.plan.name,
                    'city': biodata_item.city.name if biodata_item.city else '',
                    'date_of_birth': biodata_item.date_of_birth.strftime('%Y-%m-%d') if biodata_item.date_of_birth else ''
                })
            
            data = {
                'users': users_data,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages
            }
            return JsonResponse(data)

        # Regular render for non-AJAX requests
        return render(request, 'adminpages/adminfreeuser.html', {
            'page_obj': page_obj
        })

    else:
        return redirect('home')
    

@login_required(login_url='login')
def adminpremiumuser(request):
    if request.user.is_admin:
        email = request.GET.get('email', '')
        biodata = Biodata.objects.filter(plan=2)
        print(biodata)

        # Filter by email if the email parameter is present
        if email:
            biodata = biodata.filter(user__email__icontains=email)

        # Implement pagination, displaying 5 profiles per page
        paginator = Paginator(biodata, 15)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Check if the request is AJAX for search or pagination
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            users_data = []
            for biodata_item in page_obj:
                users_data.append({
                    'id': biodata_item.id,
                    'name': biodata_item.user.name,
                    'email': biodata_item.user.email,
                    'phone': biodata_item.user.phone,
                    'plan': biodata_item.plan.name,
                    'city': biodata_item.city.name if biodata_item.city else '',
                    'date_of_birth': biodata_item.date_of_birth.strftime('%Y-%m-%d') if biodata_item.date_of_birth else ''
                })            
            data = {
                'users': users_data,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages
            }
            return JsonResponse(data)

        # Regular render for non-AJAX requests
        return render(request, 'adminpages/adminpremiumuser.html', {
            'page_obj': page_obj
        })

    else:
        return redirect('home')


@login_required(login_url='login')
def adminupdateuser(request, user_id):
    # Ensure that the logged-in user is an admin
    if request.user.is_admin:
        # Get the user and their corresponding biodata
        user = get_object_or_404(User, pk=user_id)
        biodata = get_object_or_404(Biodata, user=user)

        if request.method == 'POST':
            # Create a user form and biodata form with the POST data
            userform = UserRegistrationForm(request.POST, instance=user)
            form = BiodataForm(request.POST, request.FILES, instance=biodata)

            # Check if both forms are valid
            if userform.is_valid() and form.is_valid():
                # Save the user and biodata
                userform.save()
                form.save()
                messages.success(request, "User and Biodata updated successfully!")
                return redirect('adminhome')
            else:
                print("Errors:", userform.errors, form.errors)
        else:
            # Load the form with the existing data
            userform = UserRegistrationForm(instance=user)
            form = BiodataForm(instance=biodata)

        return render(request, 'adminpages/updateuser.html', {'form': form, 'userform': userform, 'user': user})
    else:
        return redirect('home')
    

def adminnewuserrequests(request):
    if request.user.is_admin:
        newusers = Biodata.objects.filter(admin_approval=False)
        return render(request, 'adminpages/adminnewuserrequests.html', {'newusers': newusers})
    else:
        return redirect('home')

@require_POST
def toggle_approval(request, user_id):
    if request.user.is_admin:
        print('here')
        try:
            biodata = Biodata.objects.get(user_id=user_id)
            biodata.admin_approval = not biodata.admin_approval  # Toggle approval status
            biodata.save()
            return JsonResponse({'status': 'success', 'approved': biodata.admin_approval})
        except Biodata.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
    return JsonResponse({'status': 'error', 'message': 'Unauthorized'})

@login_required(login_url='login')
def adminadvancedsearch(request):
    if request.method=='POST':
        gender =  request.POST.get('gender')
        age = request.POST.get('age')
        city = request.POST.get('city')
        plan = request.POST.get('plan')
        religion = request.POST.get('religion')
        profile_type = request.POST.get('profile_type')

        cities = City.objects.all()
        religions = Religion.objects.all()
        profiles = Biodata.objects.filter(admin_approval=True)

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

        return render(request, 'adminpages/adminadvancedsearchresults.html', {'profiles': profiles, 'gender':gender, 'age':age, 'city':city, 'plan':plan, 'religion':religion, 'profile_type':profile_type})

        
    else:
        city = City.objects.all()
        plan = Plan.objects.all()
        religion = Religion.objects.all()
        return render(request,'adminpages/adminadvancedsearch.html',{'city':city,'plan':plan,'religion':religion})


