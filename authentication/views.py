import json
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# Helper function to create profile data dictionary
def create_profile_data(user):
    # Create a dictionary with user data
    profile_data = {
        'username': user.username,
        'email': user.email,
    }
    return profile_data

@csrf_exempt
def profile_api(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            # Get profile data for the authenticated user
            profile_data = create_profile_data(request.user)
            return JsonResponse(profile_data)
        else:
            # Return an error if the user is not authenticated
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    else:
        # Return an error for invalid HTTP methods
        return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            json_data = json.loads(request.body.decode('utf-8'))

            # Create a user registration form with the parsed data
            form = UserCreationForm(json_data)

            if form.is_valid():
                # Register the user and log them in
                user = form.save()
                login(request, user)

                # Get and return profile data for the registered user
                profile_data = create_profile_data(user)
                return JsonResponse(profile_data)
            else:
                # Return an error with form validation errors
                errors = form.errors
                return JsonResponse({'error': 'Invalid form data', 'errors': errors}, status=400)
        except json.JSONDecodeError as e:
            # Return an error for invalid JSON data
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        # Return an error for invalid HTTP methods
        return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        # Create an authentication form with POST data
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            # If credentials are valid, log in the user
            user = form.get_user()
            login(request, user)

            # Get and return profile data for the logged-in user
            profile_data = create_profile_data(user)
            return JsonResponse(profile_data)
        else:
            # Return an error for invalid credentials
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    else:
        # Return an error for invalid HTTP methods
        return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
@csrf_exempt
def delete_user(request):
    if request.method == 'DELETE':
        # Get the currently authenticated user
        user_to_delete = request.user

        # Delete the user
        user_to_delete.delete()

        # Return a success message after deleting the user
        return JsonResponse({'message': 'User deleted successfully'})
    else:
        # Return an error for invalid HTTP methods
        return JsonResponse({'error': 'Invalid method'}, status=405)

def logout_view(request):
    # Log the user out and return a success message
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'})
