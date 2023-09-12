import jwt
import bcrypt
from .models import CustomUser
from django.http import JsonResponse
from django.views.generic import View
from datetime import datetime, timedelta
from planner_api.settings import SECRET_KEY
from functools import wraps

def is_authenticated(view_func):
    @wraps(view_func)
    def _wrapped_view(self, *args, **kwargs):
        data = {}
        token = self.request.META.get('HTTP_AUTHORIZATION')

        if not token:
            data['message'] = 'JWT token is missing.'
            return JsonResponse(data, status=401)

        try:
            payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            self.request.user_id = user_id
        except jwt.ExpiredSignatureError:
            data['message'] = 'JWT token has expired.'
            return JsonResponse(data, status=401)
        except jwt.DecodeError:
            data['message'] = 'JWT token is invalid.'
            return JsonResponse(data, status=401)
        except Exception as e:
            data['message'] = str(e)
            return JsonResponse(data, status=401)

        return view_func(self, *args, **kwargs)

    return _wrapped_view

class SayHello(View):
    @is_authenticated
    def get(self, *args, **kwargs):
        data = {
            'message': 'Hello',
            'user_id': self.request.user_id,
        }
        return JsonResponse(data)


class CreateToken(View):


    def post(self, request):
        data = {}
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            data['message'] = 'username and password are required.'
        else:
            try:
                user = CustomUser.objects.get(username=username)
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    expiration_time = datetime.now() + timedelta(hours=24)
                    exp_timestamp = int(expiration_time.timestamp())
                    payload = {
                        'user_id': user.id,
                        'exp': exp_timestamp,
                    }

                    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

                    data['jwt'] = token
                    data['username'] = user.username
                    data['user_id'] = user.id

                    data['message'] = 'JWT token created successfully.'
                else:
                    data['message'] = 'Invalid credentials, unable to create token.'
            except CustomUser.DoesNotExist:
                data['message'] = 'User not found.'

        return JsonResponse(data)


class SignUp(View):
    def post(self, request):
        data = {}
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            data['message'] = 'Username and password are required.'
        else:
            try:
                CustomUser.objects.get(username=username)
                data['message'] = 'Username already exists.'
            except CustomUser.DoesNotExist:
                if len(password) < 5:
                    data['message'] = 'Password must be at least 5 characters long.'
                else:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    new_user = CustomUser(username=username, password=hashed_password.decode('utf-8'))
                    new_user.save()
                    data['message'] = 'User registered successfully.'

        return JsonResponse(data)
