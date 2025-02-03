import os
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from .models import Rental, RegisterDb, RentalImage
from django.core.files.storage import default_storage
from django.contrib.auth.hashers import make_password, check_password
from .models import Rental
from django.contrib import messages


# Create your views here.

def home(request):
    rentals = Rental.objects.all().order_by('-id')[:6]  # Get latest 6 rentals

    if 'user_id' in request.session:
        user = RegisterDb.objects.get(UserID=request.session['user_id'])
        greet = f'Welcome Back, {user.Name}!'
    else:
        greet = 'Welcome, Guest!'  # Default greeting for guests (not logged in)

    return render(request, 'home.html', {'rentals': rentals, 'greet': greet})


def browseall(request):
    # Fetch all rental listings from the database
    rentals = Rental.objects.all().order_by('-id')  # Get all rentals, ordered by newest first
    return render(request, 'browseall.html', {'rentals': rentals})

from django.shortcuts import render
from django.db.models import Q
from .models import Rental

def search_rentals(request):
    query = request.GET.get('q', '')

    # Build the search query dynamically based on user input
    rental_filters = Q()

    if query:
        # Search across multiple fields using the `icontains` lookup
        rental_filters |= Q(title__icontains=query)
        rental_filters |= Q(description__icontains=query)
        rental_filters |= Q(location__icontains=query)
        rental_filters |= Q(property_type__icontains=query)
        rental_filters |= Q(rooms__icontains=query)

    # Get the rentals that match the filters
    rentals = Rental.objects.filter(rental_filters)

    return render(request, 'searchres.html', {'rentals': rentals, 'query': query})


def list_rental(request):
    # Check if user is logged in via session
    if 'user_id' not in request.session:
        # Save the current URL to redirect to it after login
        request.session['next_url'] = request.path
        return render(request, 'login.html', {'message': 'Please log in to list a rental.'})

    try:
        # Get the current logged-in user
        user = RegisterDb.objects.get(UserID=request.session['user_id'])
        owner_name = user.Name
        email = user.Email
        phone = getattr(user, 'Phone', '')  # Get phone if exists, else default to empty string
    except RegisterDb.DoesNotExist:
        owner_name = email = phone = ''

    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        property_type = request.POST.get('property_type')
        rooms = request.POST.get('rooms')
        location = request.POST.get('location')
        rent = request.POST.get('rent')
        deposit = request.POST.get('deposit')
        description = request.POST.get('description')

        # Save rental details with owner as foreign key
        rental = Rental.objects.create(
            title=title,
            property_type=property_type,
            rooms=rooms,
            location=location,
            rent=rent,
            deposit=deposit,
            description=description,
            owner=user,  # Set the logged-in user as the owner
        )

        # Handle multiple image uploads
        images = request.FILES.getlist('images')  # Get list of uploaded images
        for image in images:
            RentalImage.objects.create(rental=rental, image=image)

        # Add success message
        messages.success(request, 'Rental listing submitted successfully. Please wait for verification.')

        # Redirect to user rentals page after successful listing
        return redirect('userrentals')  # You can change this to your specific URL name for user rentals

    return render(request, 'listrental.html', {'owner_name': owner_name, 'email': email, 'phone': phone})


def rental_details(request, rental_id):
    """Display rental details only if verified or owned by the user."""

    # Check if the user is logged in
    if 'user_id' not in request.session:
        request.session['next_url'] = request.path
        messages.info(request, 'Please log in to view the rental details.')  # Flash message
        return redirect('login')  # Redirect to login page

    # Get the rental property by ID
    rental = get_object_or_404(Rental, id=rental_id)

    # Get all images related to this rental
    images = rental.images.all()

    # Get logged-in user
    user_id = request.session.get('user_id')
    
    # Check if the logged-in user is the owner
    is_owner = rental.owner.UserID == user_id

    # Only allow viewing if rental is verified or user is the owner
    if not rental.verified and not is_owner:
        messages.warning(request, "This rental is pending verification.")
        return redirect('userrentals')

    # Pass rental data to the template
    return render(request, 'rental_details.html', {
        'rental': rental,
        'images': images,
        'is_owner': is_owner
    })


def userrentals(request):
    """Show all rentals of the logged-in user."""
    
    # Check if the user is logged in
    if 'user_id' not in request.session:
        request.session['next_url'] = request.path
        messages.info(request, 'Please log in to view your rentals.')  # Flash message
        return redirect('login')

    # Retrieve the logged-in user
    try:
        user = RegisterDb.objects.get(UserID=request.session['user_id'])
    except RegisterDb.DoesNotExist:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    # Fetch rentals owned by the user
    rentals = Rental.objects.filter(owner=user)

    return render(request, 'user_rentals.html', {'rentals': rentals})

def edit_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)

    # Check if the logged-in user is the owner of the rental
    if 'user_id' not in request.session or rental.owner_id != request.session.get('user_id'):
        messages.error(request, 'You are not authorized to edit this rental.')
        return redirect('home')

    if request.method == 'POST':
        rental.title = request.POST.get('title')
        rental.property_type = request.POST.get('property_type')
        rental.rooms = request.POST.get('rooms')
        rental.location = request.POST.get('location')
        rental.rent = request.POST.get('rent')
        rental.deposit = request.POST.get('deposit')
        rental.description = request.POST.get('description')

        rental.save()

        # Debugging: Print the data to check if delete_images checkboxes are being submitted
        delete_image_ids = request.POST.getlist('delete_images')
        print("Delete Images:", delete_image_ids)  # Print the IDs of images to be deleted

        if delete_image_ids:
            RentalImage.objects.filter(id__in=delete_image_ids).delete()

        # Handle new image uploads
        new_images = request.FILES.getlist('images')
        for image in new_images:
            RentalImage.objects.create(rental=rental, image=image)
            
        messages.success(request, 'Rental details updated successfully!')
        return redirect('rental_details', rental_id=rental.id)

    # Fetch associated images for the rental and pass them to the template
    images = RentalImage.objects.filter(rental=rental)

    return render(request, 'edit_rentals.html', {'rental': rental, 'images': images})




def delete_rental(request, rental_id):

    print(f"Deleting rental ID: {rental_id}")

    rental = get_object_or_404(Rental, id=rental_id)
    
    if rental.owner.UserID != request.session.get('user_id'):
        return render(request, 'error.html', {'message': 'You are not authorized to delete this rental.'})
    
    for image in rental.images.all():
        image_path = image.image.path
        if os.path.exists(image_path):
            os.remove(image_path)
        image.delete()
    
    print(f"Session User ID: {request.session.get('user_id')}")
    print(f"Rental Owner ID: {rental.owner.UserID}")

    rental.delete()
    print(f"Rental {rental_id} deleted successfully.")

    messages.success(request, 'The rental has been deleted successfully.')

    return redirect('userrentals')

def delete_image(request, image_id):
    # Get the image object (assuming you have a model for images linked to rental)
    image = get_object_or_404(RentalImage, id=image_id)
    
    # Get the image file path
    image_path = image.file.path
    
    # Delete the image from the database
    image.delete()

    # Check if file exists and then delete it from the filesystem
    if os.path.exists(image_path):
        os.remove(image_path)

    messages.success(request, 'Image deleted successfully.')
    
    return redirect('rental_details', rental_id=image.rental.id)


def viewprofile(request):
    # Ensure the user is logged in
    user_id = request.session.get('user_id')
    if 'user_id' not in request.session:
        request.session['next_url'] = request.path  # Redirect to login if user is not authenticated
        messages.error(request, 'Please log in to view your profile.')  # Add message for unauthenticated users
        return redirect('login')  # Redirect to login if not logged in

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
        messages.error(request, 'User not found. Please log in again.')  # Add message for user not found
        return redirect('login')

def editprofile(request):
    if 'user_id' not in request.session:
        request.session['next_url'] = request.path  # Redirect to login if not logged in
        messages.error(request, 'Please log in to edit your profile.')  # Add message for unauthenticated users
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
            messages.error(request, 'Passwords do not match!')  # Show error message if passwords don't match
            return render(request, 'editprofile.html', {'user': user})

        user.Name = name
        user.Email = email
        user.Location = location
        user.Phone = phone
        if password:
            user.Password = make_password(password)  # Hash new password if provided

        user.save()
        messages.success(request, 'Profile updated successfully!')  # Success message after update
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

                # Check if 'next_url' is set in session, else redirect to home
                next_url = request.session.get('next_url', '/')
                
                if 'next_url' in request.session:
                    del request.session['next_url']
                
                return redirect(next_url)

            else:
                messages.error(request, 'Invalid email or password')  # Error message for invalid password
        except RegisterDb.DoesNotExist:
            messages.error(request, 'Invalid email or password')  # Error message if email is not found

    # After any failed login attempt, re-render the login page
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')

        # Check if all fields are filled
        if not name or not email or not password or not confirm_password:
            messages.error(request, 'Please fill in all fields')
            return render(request, 'signup.html')

        # Validate password strength
        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
        if not password_pattern.match(password):
            messages.error(request, 'Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character')
            return render(request, 'signup.html')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'signup.html')

        # Check if email already exists
        try:
            if RegisterDb.objects.filter(Email=email).exists():
                messages.error(request, 'You already have an account! Please log in.')
                return render(request, 'signup.html')

            # Hash the password and save the user to the database
            hashed_password = make_password(password)
            register_db = RegisterDb(Name=name, Email=email, Password=hashed_password, ConfirmPassword=hashed_password)
            register_db.save()

            # Set success message and redirect to the login page
            messages.success(request, 'Registration successful! Please log in to continue.')
            return redirect('login')  # This should properly redirect to the login page

        except IntegrityError:
            messages.error(request, 'Email already exists. Please log in.')
            return render(request, 'signup.html')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'signup.html')
    
    return render(request, 'signup.html')

def logout_view(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    messages.success(request, 'Logged out successfully!')

    return redirect('login') 


