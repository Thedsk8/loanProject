import json
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from loan.models import Loan
from loan.payment_strategies import WeeklyPaymentStrategy


class CreateLoanViewSetHandler:

    def create_loan(self, request):
        data = json.loads(request.body)
        payment_strategy = data.get("payment_strategy", "weekly")
        amount = data.get("amount")
        tenure = data.get("tenure")
        borrower = request.user_obj
        loan_id = self.create_loan_in_db(amount, borrower, tenure, payment_strategy)
        return loan_id

    @classmethod
    def create_loan_in_db(cls, amount, borrower, tenure, payment_strategy):
        return Loan.create_loan(
            **{
                "amount": amount,
                "borrower": borrower,
                "tenure": tenure,
                "payment_strategy": payment_strategy,
            }
        )


class FetchLoanInfoHandler:

    @classmethod
    def get_loan_info(cls, request, loan_id):
        data = {"borrower": request.user_obj, "id": loan_id}
        loan_info = Loan.get_loan_info(**data)
        if not loan_info:
            raise ValidationError({"Error": f"No Loan {loan_id} is associated to you"})
        return loan_info


class ApproveRequestHandler:
    def __init__(self):
        self.payment_strategies = {
            "weekly": WeeklyPaymentStrategy(),
            # Future strategies can be added here
        }

    def approve_request(self, request, loan_id):
        loan_obj = Loan.get_loan_obj(**{"id": loan_id})
        if not loan_obj:
            raise ValidationError({"Error": f"Loan with Id {loan_id} Does not exist"})
        if loan_obj.status == "approved":
            raise ValidationError(
                {"Error": f"Loan with Id {loan_id} is already approved"}
            )
        # either both happens or nothing happened
        with transaction.atomic():
            self.save_loan(request, loan_obj)
            # setting up schedule of loan
            self.payment_strategies.get(loan_obj.payment_strategy).generate_schedule(
                loan_obj
            )

    @classmethod
    def save_loan(cls, request, loan_obj):
        loan_obj.approver = request.user_obj
        loan_obj.status = "approved"
        loan_obj.approved_at = timezone.now()
        loan_obj.save()


class RepaymentViewHandler:

    def process_payment(self, request, loan_id):
        loan_obj = Loan.get_loan_obj(**{"id": loan_id})
        if not loan_obj:
            raise ValidationError({"Error": f"Loan with id {loan_id} Does not exist"})
        data = json.loads(request.body)
        repayments = loan_obj.repayments.filter(status="pending").order_by("due_date")
        if not repayments.exists():
            raise ValidationError({"Error": "No pending repayments found"})

        if data.get("amount") < repayments[0].amount:
            raise ValidationError(
                {"Error": f"Minimum allowed amount is {repayments[0].amount}"}
            )

        return self.add_payment(data.get("amount"), loan_obj, repayments)

    @classmethod
    def add_payment(cls, amount, loan, repayments):
        with transaction.atomic():
            for repayment in repayments:
                if amount >= repayment.amount:
                    amount -= repayment.amount
                    repayment.status = "paid"
                    repayment.save()
                else:
                    repayment.amount -= amount
                    repayment.save()
                    amount = 0
                    break

            if all(repayments.status == "paid" for repayments in loan.repayments.all()):
                loan.status = "paid"
                loan.paid_at = timezone.now()
                loan.save()

            return amount
