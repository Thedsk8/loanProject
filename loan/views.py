import logging

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.views import View

from loan.handler import (
    ApproveRequestHandler,
    CreateLoanViewSetHandler,
    FetchLoanInfoHandler,
    RepaymentViewHandler,
)
from loan.validators import (
    CreateLoanViewSetValidator,
    ApproveLoanValidator,
    RepaymentViewValidator,
)


logger = logging.getLogger(__name__)


class CreateLoanViewSet(View):

    def __init__(self):
        self.handler = CreateLoanViewSetHandler()
        self.validator = CreateLoanViewSetValidator()

    def post(self, request):
        try:
            self.validator.validate_create_request(request)
            loan_id = self.handler.create_loan(request)
            return JsonResponse(
                {
                    "Success": f"Loan Request Successfully Submitted with ID {loan_id}",
                    "loan_id": loan_id,
                }
            )
        except ValidationError as err:
            return JsonResponse(err.args[0], status=400)
        except PermissionDenied as err:
            return JsonResponse(err.args[0], status=403)
        except Exception as err:
            logger.exception(f"Exception Occurred while creating loan {err}")
            return JsonResponse({"Error": "Internal Server Error"}, status=500)


class FetchLoanInfo(View):

    def __init__(self):
        self.handler = FetchLoanInfoHandler()

    def get(self, request, loan_id):
        try:
            data = self.handler.get_loan_info(request, loan_id)
            return JsonResponse(data, status=200)
        except ValidationError as err:
            return JsonResponse(err.args[0], status=400)
        except Exception as err:
            logger.exception(f"Exception Occurred while creating loan {err}")
            return JsonResponse({"Error": "Internal Server Error"}, status=500)


class ApproveLoan(View):

    def __init__(self):
        self.handler = ApproveRequestHandler()
        self.validator = ApproveLoanValidator()

    def post(self, request, loan_id):
        try:
            self.validator.validate_approve_request(request, loan_id)
            self.handler.approve_request(request, loan_id)
            data = {"Loan": loan_id, "status": "Approved"}
            return JsonResponse(data, status=200)
        except PermissionDenied as err:
            return JsonResponse(err.args[0], status=403)
        except ValidationError as err:
            return JsonResponse(err.args[0], status=400)
        except Exception as err:
            logger.exception(f"Exception Occurred while creating loan {err}")
            return JsonResponse({"Error": "Internal Server Error"}, status=500)


class RepaymentView(View):

    def __init__(self):
        self.handler = RepaymentViewHandler()
        self.validator = RepaymentViewValidator()

    def post(self, request, loan_id):
        try:
            self.validator.validate_repay_request(request, loan_id)
            amount = self.handler.process_payment(request, loan_id)
            if amount > 0:
                return JsonResponse(
                    {
                        "message": "Repayment successful with overpayment",
                        "overpayment": amount,
                    },
                    status=200,
                )

            return JsonResponse({"message": "Repayment successful"}, status=200)
        except ValidationError as err:
            return JsonResponse(err.args[0], status=400)
        except Exception as err:
            logger.exception(f"Exception Occurred while creating loan {err}")
            return JsonResponse({"Error": "Internal Server Error"}, status=500)
