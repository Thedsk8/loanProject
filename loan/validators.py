import json

from django.core.exceptions import PermissionDenied
from django.core.validators import ValidationError
from loan.models import Loan
from loanProject.commons.validators import BaseJsonRequestValidator, RolesValidator


class CreateLoanViewSetValidator(BaseJsonRequestValidator, RolesValidator):

    def __init__(self):
        self.allowed_fields = ["amount", "tenure"]
        self.amount_limit = 1000000
        self.tenure_limit = 100
        super().__init__()

    def validate_create_request(self, request):
        self.validate_json_body(request)
        self.validate_user_role(request)
        self.validate_body_parameters(request)

    def validate_user_role(self, request):
        if not self.is_borrower(request):
            raise PermissionDenied({"Error": "Forbidden"})

    def validate_body_parameters(self, request):
        data = json.loads(request.body)
        if not set(data.keys()).issubset(set(self.allowed_fields)):
            raise ValidationError(
                {"Error": f"Allowed fields are {self.allowed_fields}"}
            )
        if not set(self.allowed_fields).issubset(set(data.keys())):
            raise ValidationError({"Error": f"{self.allowed_fields} are required"})
        self.validate_amount(data)
        self.validate_tenure(data)

    def validate_amount(self, data):
        amount = data.get("amount")
        if not isinstance(amount, float) and not isinstance(amount, int):
            raise ValidationError({"Error": "Amount should be of type Float"})

        if isinstance(amount, bool):
            raise ValidationError({"Error": "Amount should be of type Float"})

        if amount > self.amount_limit:
            raise ValidationError(
                {
                    "Error": f"Please select an amount less than equals to {self.amount_limit}"
                }
            )

        if amount <= 0:
            raise ValidationError({"Error": f"Please select an amount greater than 0"})

    def validate_tenure(self, data):
        tenure = data.get("tenure")
        if not isinstance(tenure, int):
            raise ValidationError({"Error": "Tenure should be of type integer"})

        if tenure > self.tenure_limit:
            raise ValidationError(
                {
                    "Error": f"Please select a Tenure less than equals to {self.tenure_limit}"
                }
            )

        if tenure <= 0:
            raise ValidationError({"Error": f"Please select tenure greater than 0"})


class ApproveLoanValidator(RolesValidator):

    def validate_approve_request(self, request, loan_id):
        self.validate_user_role(request)
        self.check_loan_exist(loan_id)

    def validate_user_role(self, request):
        if not self.is_approver(request):
            raise PermissionDenied({"Error": "Forbidden"})

    @classmethod
    def check_loan_exist(cls, loan_id):
        if not Loan.is_exist(loan_id):
            raise ValidationError({"Error": f"Loan with id {loan_id} does not exist"})


class RepaymentViewValidator(BaseJsonRequestValidator, RolesValidator):

    def validate_repay_request(self, request, loan_id):
        self.validate_json_body(request)
        self.validate_user_role(request)
        loan_info = self.check_loan_exist(request, loan_id)
        data = json.loads(request.body)
        self.check_amount(data, loan_info)
        self.check_loan_status(loan_info)

    def validate_user_role(self, request):
        if not self.is_borrower(request):
            raise PermissionDenied({"Error": "Forbidden"})

    @classmethod
    def check_loan_exist(cls, request, loan_id):
        data = {"borrower": request.user_obj, "id": loan_id}
        loan_info = Loan.get_loan_info(**data)
        if not loan_info:
            raise ValidationError({"Error": f"No Loan {loan_id} is associated to you"})
        return loan_info

    @classmethod
    def check_amount(cls, data, loan_info):
        amount = data.get("amount")
        if not amount:
            raise ValidationError({"Error": "amount is a required field"})
        if not isinstance(amount, float) and not isinstance(amount, int):
            raise ValidationError({"Error": "Amount should be of type Float"})
        if isinstance(amount, bool):
            raise ValidationError({"Error": "Amount should be of type Float"})
        if amount > loan_info.get("amount"):
            raise ValidationError(
                {"Error": "Amount Should not be greater than actual loan amount"}
            )

    @classmethod
    def check_loan_status(cls, loan_info):
        if loan_info.get("status") == "paid":
            raise ValidationError({"Error": "Loan is already paid"})
        if loan_info.get("status") != "approved":
            raise ValidationError({"Error": "Loan is not approved yet"})
