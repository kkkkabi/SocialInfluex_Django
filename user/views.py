from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages 
from .models import Profile
from django.contrib.auth.decorators import login_required


# Create your views here.

def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(username=email, password = password)

        if user is not None: #if the user is registered, redirect to the homepage
            auth.login(request, user)
            return redirect('/dashboard')
        else: # if the user is not registered, report error message and redirect to signin page
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
  
    else:
        return render(request, 'signin.html')


def signup(request):
    # if the data has been post, get the value of the data using the name
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']                        
        # set password criteria
        if password == password2:

            # check if the e-mail exist in the email list
            if User.objects.filter(email = email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')                                    
            # if username is not taken, create a new user
            else: 
                user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name )
                user.set_password(password)
                user.save()

                # user login-> create a new profile-> redirect to setting page
                # log user in and redirect to settings page
                user_login = auth.authenticate(email=email, password = password)
                auth.login(request, user_login)

                # create a profile object for new user
                user_model = User.objects.get(username = email)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id, first_name=first_name, last_name=last_name, email=email)
                new_profile.save()

                return redirect('signin') #change to setting page after create profile

        else: 
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')  #it will go to templates/signuphtml

@login_required(login_url='signin') 
def logout(request):
    auth.logout(request)
    return redirect('signin')

def setting(request):
    return render(request, 'setting.html')


# @login_required(login_url='signin') 
def dashboard(request):
    return render(request, 'base_dashboard.html')


