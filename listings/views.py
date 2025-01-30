import re
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.db import IntegrityError
from .models import RegisterDb  # Import RegisterDb
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.

def home(request):
    return render(request, 'home.html')

def browseall(request):
    return render(request, 'browseall.html')

def listrental(request):
    return render(request, 'listrental.html')

def showdetails(request):
    return render(request, 'showflat.html')

def viewprofile(request):
    return render(request, 'viewprofile.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = RegisterDb.objects.get(Email=email)  # Retrieve user from custom model
            if check_password(password, user.Password):  # Check if the password matches the hashed password
                # Log the user in (you might need a custom authentication mechanism here)
                request.session['user_id'] = user.UserID  # Example of setting a session for the logged-in user
                return render(request, 'home.html', {'greet': 'Welcome back!{}'.format(user.Name)})
            else:
                return render(request, 'login.html', {'error': 'Invalid email or password'})
        except RegisterDb.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid email or password'})
    return render(request, 'login.html')



def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        if not name or not email or not password or not confirm_password:
            return render(request, 'signup.html', {'error': 'Please fill in all fields'})

        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
        if not password_pattern.match(password):
            return render(request, 'signup.html', {'error': 'Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character'})

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        try:
            # Check if email already exists in RegisterDb model
            if RegisterDb.objects.filter(Email=email).exists():
                return render(request, 'signup.html', {'error': 'You already have an account! Please log in.'})

            # Hash the password
            hashed_password = make_password(password)

            # Save to custom RegisterDb model
            register_db = RegisterDb(Name=name, Email=email, Password=hashed_password, ConfirmPassword=hashed_password)
            register_db.save()

            return redirect('signup_success')  # Redirect to a success page
        except IntegrityError:
            return render(request, 'signup.html', {'error': 'You already have an account! Please log in.'})
        except Exception as e:
            return render(request, 'signup.html', {'error': f'Registration failed: {str(e)}'})
    return render(request, 'signup.html')

def signup_success(request):
    return render(request, 'login.html', {'message': 'Registration successful! Please log in to continue.'})


def logout_view(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return render(request, 'login.html', {'message': 'Logged out successfully!'})
