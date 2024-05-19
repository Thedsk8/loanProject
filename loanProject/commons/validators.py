import logging
import json

from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


class BaseJsonRequestValidator:

    def __init__(self, msg={"Error": "Data Sent is not of type JSON"}):
        self.json_conversion_error_message = msg

    def validate_json_body(self, request, instance_type=dict):
        self.validate_json(request.body)
        data = json.loads(request.body)
        if not isinstance(data, instance_type):
            raise ValidationError(self.json_conversion_error_message)

    def validate_json(self, data, msg=None):
        if not msg:
            msg = self.json_conversion_error_message
        try:
            data = json.loads(data)
        except Exception as error:
            logger.error(
                "Json {} sent is not Json Serializable and error {}".format(data, error)
            )
            raise ValidationError(msg)


class RolesValidator:
    @classmethod
    def is_borrower(cls, request):
        return "borrower" in request.user_roles

    @classmethod
    def is_approver(cls, request):
        return "approver" in request.user_roles
