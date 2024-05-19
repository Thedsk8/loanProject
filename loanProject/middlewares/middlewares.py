from django.core.validators import ValidationError
from django.http import JsonResponse
from users.models import User


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Get email and password from headers
            email = request.headers.get("X-User-Email")
            password = request.headers.get("X-User-Password")

            # Validate the headers
            if not email or not password:
                raise ValidationError({"Error": "Email and password are required"})

            user_obj = self._validate_user_existence(email, password)

            request.user_obj = user_obj

            request.user_roles = user_obj.roles

            response = self.get_response(request)
            return response
        except ValidationError as err:
            return JsonResponse(err.args[0], status=401)

    @classmethod
    def _validate_user_existence(cls, email, password):
        user_obj = User.get_user_object_with_email_and_password(email, password)
        if not user_obj:
            raise ValidationError({"Error": "Email and Passwords are not Valid"})
        return user_obj
