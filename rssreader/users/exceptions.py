from rest_framework.exceptions import APIException


class UserAlreadyExistsException(APIException):
    status_code = 400
    default_code = 'user_already_exists'


class UserNotFoundException(APIException):
    status_code = 404
    default_code = 'user_not_found'