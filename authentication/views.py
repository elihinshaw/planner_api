import json
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session

# Helper function to create profile data dictionary

@csrf_exempt
def create_profile_data(user):
    profile_data = {
        "username": user.username,
        "email": user.email,
    }
    return profile_data

@csrf_exempt
def profile_api(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            # Get profile data for the authenticated user
            profile_data = {
                "username": request.user.username,
                "email": request.user.email,
            }
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
                # Register the user
                user = form.save()

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
    print(request.POST)
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Get the session key from the user's session
            session_key = request.session.session_key
            # Return the session key in the response JSON
            return JsonResponse({'session_key': session_key})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    else:
        return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required
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


@csrf_exempt
def logout_view(request):
    # Get the session key from the client-side (assuming it's being passed as a query parameter)
    session_key = request.GET.get('session_key')

    # Delete the session from the database
    Session.objects.filter(session_key=session_key).delete()

    # Log the user out using Django's logout method
    logout(request)

    print("Server successfully logged out.")
    return JsonResponse({'message': 'Logged out successfully'})
