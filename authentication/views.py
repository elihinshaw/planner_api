import jwt
import bcrypt
from .models import CustomUser
from django.http import JsonResponse
from django.views.generic import View
from datetime import datetime, timedelta
from planner_api.settings import SECRET_KEY
from functools import wraps


# Decorator function for authentication
def is_authenticated(view_func):
    # Define a wrapper function to handle authentication
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        data = {}

        token = request.META.get('HTTP_AUTHORIZATION')

        if not token: # Check if the token is missing
            data['message'] = 'JWT token is missing.'
            return JsonResponse(data, status=401)

        try:
            # Decode the JWT token and take the user_id from said decoding
            payload = jwt.decode(token.split(
                " ")[1], SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            request.user_id = user_id # Attach the user_id to the request for later use
        except jwt.ExpiredSignatureError:
            data['message'] = 'JWT token has expired.' # Handle if the JWT is expired
            return JsonResponse(data, status=401)
        except jwt.DecodeError:
            data['message'] = 'JWT token is invalid.' # Handle if JWT is invalid
            return JsonResponse(data, status=401)
        except Exception as e:
            # Handle other exceptions that may occur during decoding
            data['message'] = str(e)
            return JsonResponse(data, status=401)

        # Handle any other exceptions that may occur during decoding process
        return view_func(request, *args, **kwargs)

    return _wrapped_view # Return the wrapped view


# This was created to check the function above worked
class SayHello(View):
    @is_authenticated
    def get(self, *args, **kwargs):
        data = {
            'message': 'Hello',
            'user_id': self.request.user_id,
        }
        return JsonResponse(data)


class CreateToken(View):

    def post(self, request): # handle POST to create JWT tokens
        data = {}
        # Get username and password from POST request
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if both username and password are provided
        if not username or not password:
            data['message'] = 'username and password are required.'
        else:
            try:
                # Attempt to retrieve a user with given username
                user = CustomUser.objects.get(username=username)

                # Compare the provided password and stored password (both hashed and encoded) to check if they match
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    # Generate expiration time for the JWT token
                    expiration_time = datetime.now() + timedelta(days=1)
                    exp_timestamp = int(expiration_time.timestamp())

                    # Create JWT payload using user information and expiration time
                    payload = {
                        'user_id': user.id,
                        'exp': exp_timestamp,
                    }

                    # Encode the payload to generate the JWT token
                    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

                    # Add JWT token and user information to the response
                    data['jwt'] = token
                    data['username'] = user.username
                    data['user_id'] = user.id
                    data['exp'] = exp_timestamp
                    data['message'] = 'JWT token created successfully.'
                else:
                    # Handle case when the login is invalid
                    data['message'] = 'Invalid credentials, unable to create token.'
            except CustomUser.DoesNotExist:
                # Handle case when username is not found
                data['message'] = 'User not found.'

        # Return the response data as JSON
        return JsonResponse(data)


class SignUp(View):
    def post(self, request):
        data = {}
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if both username and password exist
        if not username or not password:
            data['message'] = 'Username and password are required.'
            return JsonResponse(data, status=400)
        else:
            try:
                # Check if username already exists
                CustomUser.objects.get(username=username)
                data['message'] = 'Username already exists.'
                return JsonResponse(data, status=409)
            except CustomUser.DoesNotExist:
                # Check if password is less than 5, if so send error
                if len(password) < 5:
                    data['message'] = 'Password must be at least 5 characters long.'
                    return JsonResponse(data, status=401)
                else:
                    # Hash password before storing it
                    hashed_password = bcrypt.hashpw(
                        password.encode('utf-8'), bcrypt.gensalt())
                    # Create CustomUser with username and hashed password
                    new_user = CustomUser(
                        username=username, password=hashed_password.decode('utf-8'))
                    new_user.save()
                    # Save new user in the database
                    data['message'] = 'User registered successfully.'

        return JsonResponse(data, status=201)
