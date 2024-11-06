from django.shortcuts import render, redirect,HttpResponse,get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from app.forms import RegistrationForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app.models import Biodata
from django.contrib.auth.decorators import login_required
from app.forms import UserEditForm
from django.http import JsonResponse

User = get_user_model()



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Send email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('pages/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [user.email])

            messages.success(request, 'email sent to your email. Please confirm your email address to complete the registration.')
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'pages/register.html')

# def register(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()
#             messages.success(request, 'registration successfully please wait for admin approval')
#             return redirect('home')
#         else:
#             print(form.errors)
#             messages.error(request, "form details are not valid")
#             return redirect('register')
#     else:
#         form = RegistrationForm()
#     return render(request, 'pages/register.html')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated!, you can login now')
        return redirect('login')
    else:
        return render(request, 'pages/activation_invalid.html')
    


def loginview(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            try:
                biodata = Biodata.objects.get(user=user)
                messages.info(request,'succesfull login')
                return redirect('home')

            except Biodata.DoesNotExist:
                return redirect('biodata')

        else:
            messages.error(request, "Invalid username or password!")
            return render(request, 'pages/login.html')
    else:
        return render(request, 'pages/login.html')
    

def logoutview(request):
    """
    Logs out the user and redirects them to the homepage or another page.
    """
    logout(request)  # This logs out the user
    messages.success(request, "Logged out successfully!")
    return redirect('home')  # Redirect to a named URL (e.g., homepage or login page)

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            user = get_object_or_404(User, email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))
            message = f"Reset your password by clicking the link: {reset_url}"
            send_mail(
                'Password Reset Request',
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return redirect('password_reset_done')
    return render(request, 'pages/password_reset.html')

def password_reset_done(request):
    return render(request, 'pages/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password and password == confirm_password:
                user.set_password(password)
                user.save()
                return redirect('password_reset_complete')
            else:
                return HttpResponse('Passwords do not match', status=400)
        return render(request, 'pages/password_reset_confirm.html', {'validlink': True})
    else:
        return render(request, 'pages/password_reset_confirm.html', {'validlink': False})

def password_reset_complete(request):
    return render(request, 'pages/password_reset_complete.html')



# views.py
@login_required
def edit_account(request):
    user = request.user  # Get the currently logged-in user

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            # If a new password is provided, hash it before saving
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)  # Hash and set the new password

            form.save(commit=False)  # Save the form without committing yet
            user.save()  # Save the user with the new hashed password
            messages.success(request, 'Your account has been updated successfully! login again with new password')
            return redirect('login')
        else:
            messages.error(request, 'error happened try again!')
            return redirect('edit_account')
    
    else:
        form = UserEditForm(instance=user)  # Pre-fill the form with the user's data
        return render(request, 'edit_account.html', {'form': form})
