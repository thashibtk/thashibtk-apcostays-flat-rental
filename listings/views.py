import os
import re
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login as auth_login
from django.db import IntegrityError
from .models import RegisterDb  # Import RegisterDb
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from .models import Rental
from django.core.files.storage import FileSystemStorage
from .models import Rental
from django.contrib.auth.models import User

# Create your views here.

def home(request):
    return render(request, 'home.html')

def browseall(request):
    return render(request, 'browseall.html')

def list_rental(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        property_type = request.POST.get('property_type')
        rooms = request.POST.get('rooms')
        location = request.POST.get('location')
        rent = request.POST.get('rent')
        deposit = request.POST.get('deposit')
        description = request.POST.get('description')
        phone = request.POST.get('phone')

        # Get logged-in user's name and email
        if request.user.is_authenticated:
            owner_name = request.user.get_full_name()
            email = request.user.email
        else:
            owner_name = request.POST.get('owner_name')  # Use user input if not logged in
            email = request.POST.get('email')

        # Handle image upload
        image_url = None
        if 'image' in request.FILES:
            image = request.FILES['image']
            fs = FileSystemStorage(location='media/rentals/')  # Saves in media/rentals/
            filename = fs.save(image.name, image)
            image_url = 'rentals/' + filename  # Save relative path

        # Save rental to the database
        rental = Rental.objects.create(
            title=title,
            property_type=property_type,
            rooms=rooms,
            location=location,
            rent=rent,
            deposit=deposit,
            description=description,
            owner_name=owner_name,
            email=email,
            phone=phone,
            image=image_url
        )
        rental.save()

        return redirect('rental_success')

    return render(request, 'listrental.html')


def rental_success(request):
    return render(request, 'listrental.html', {'message': 'Rental listing submitted successfully.'})


def rental_details(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    images = rental.images.all()  # Fetch related images

    return render(request, 'details.html', {'rental': rental, 'images': images})


def viewprofile(request):
    # Ensure the user is logged in
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # Redirect to login if user is not authenticated

    try:
        # Fetch the user details
        user = RegisterDb.objects.get(UserID=user_id)
        context = {
            'name': user.Name,
            'email': user.Email,
            'location': user.Location if hasattr(user, 'Location') else 'Not Provided',
            'phone': user.Phone if hasattr(user, 'Phone') else 'Not Provided'
        }
        return render(request, 'viewprofile.html', context)
    except RegisterDb.DoesNotExist:
        return redirect('login')

def editprofile(request):
    # Check if the user is logged in
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login if not logged in

    user_id = request.session['user_id']  # Get logged-in user ID
    user = RegisterDb.objects.get(UserID=user_id)  # Fetch user data

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        location = request.POST.get('location')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password and password != confirm_password:
            return render(request, 'editprofile.html', {'user': user, 'error': 'Passwords do not match!'})

        # Update user details
        user.Name = name
        user.Email = email
        user.Location = location
        user.Phone = phone
        if password:
            user.Password = make_password(password)  # Hash new password

        user.save()
        return redirect('viewprofile')  # Redirect to profile page after update

    return render(request, 'editprofile.html', {'user': user})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = RegisterDb.objects.get(Email=email)  # Retrieve user from custom model
            if check_password(password, user.Password):  # Check if the password matches the hashed password
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
