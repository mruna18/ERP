from rest_framework.exceptions import APIException
from rest_framework import status


class CustomApiException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A server error occurred."
    default_code = "error"

    def __init__(self, status_code=None, detail=None, code=None):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {"status": self.status_code, "message": detail}
        else:
            self.detail = {"status": self.status_code, "message": self.default_detail}
        if code:
            self.default_code = code
