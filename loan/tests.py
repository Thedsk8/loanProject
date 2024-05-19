import json
import random
import string

from django.test import RequestFactory, TestCase

from loan.models import Loan
from loan.views import ApproveLoan
from loan.views import CreateLoanViewSet
from loan.views import FetchLoanInfo
from loan.views import RepaymentView
from users.models import User


class CreateTestUsers(TestCase):

    def __init__(self, *args, **kwargs):
        self.factory = RequestFactory()
        super().__init__(*args, **kwargs)

    def setUp(self, *args, **kwargs):
        users = self.create_users()
        self.borrower_user = users[0]
        self.approver_user = users[1]
        super().setUp(*args, **kwargs)

    def create_users(self):
        users_data = [
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": self._generate_password(),
                "roles": ["borrower"],
            },
            {
                "first_name": "Jim",
                "last_name": "Beam",
                "email": "jim.beams@example.com",
                "password": self._generate_password(),
                "roles": ["approver"],
            },
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                email=user_data["email"],
                defaults={
                    "password": user_data["password"],
                    "roles": user_data["roles"],
                },
            )
            users.append(user)

        return users

    @classmethod
    def _generate_password(cls):
        return "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(8)
        )


class LoanApplicationTest(CreateTestUsers):

    def test_successful_loan_creation(self):
        data = {"amount": 100000, "tenure": 12}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        loan_id = json.loads(response.content).get("loan_id")
        loan_info = Loan.get_loan_info(
            **{"id": loan_id, "borrower": self.borrower_user}
        )
        self.assertEqual(loan_id, loan_info.get("id"))
        self.assertEqual("pending", loan_info.get("status"))

    def test_loan_creation_with_invalid_amount(self):
        data = {"amount": 1500000, "tenure": 12}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertIn(
            "Please select an amount less than equals to 1000000", content.get("Error")
        )

        data = {"amount": False, "tenure": 12}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertIn("Amount should be of type Float", content.get("Error"))

        data = {"tenure": 12}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertIn("['amount', 'tenure'] are required", content.get("Error"))

    def test_loan_creation_with_invalid_tenure(self):
        data = {"amount": 15000, "tenure": 120}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertIn(
            "Please select a Tenure less than equals to 100", content.get("Error")
        )

        data = {"amount": 10000, "tenure": "12"}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertIn("Tenure should be of type integer", content.get("Error"))

        data = {"amount": 10000}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertIn("['amount', 'tenure'] are required", content.get("Error"))

    def test_invalid_user(self):
        data = {"amount": 100000, "tenure": 12}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["approval"]
        request.user_obj = self.approver_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)

    def test_loan_creation_with_invalid_json(self):
        data = {"amount": 100000, "tenure": 12}
        request = self.factory.post(
            path="/loans/create",
            data=data,
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertIn("Data Sent is not of type JSON", content.get("Error"))


class FetchLoanInfoTestCase(CreateTestUsers):
    def create_loan(self):
        data = {"amount": 100000, "tenure": 12}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        loan_id = json.loads(response.content).get("loan_id")
        return loan_id

    def test_fetch_loan_info_success(self):
        loan_id = self.create_loan()

        request = self.factory.get(path="/loans/<loan_id>/fetch")
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = FetchLoanInfo.as_view()
        response = view(request, loan_id)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content.get("id"), loan_id)

    def test_fetch_loan_info_invalid_user(self):
        loan_id = self.create_loan()

        request = self.factory.get(
            path="/loans/<loan_id>/fetch",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.approver_user
        view = FetchLoanInfo.as_view()
        response = view(request, loan_id)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(
            f"No Loan {loan_id} is associated to you", content.get("Error")
        )


class ApproveLoanTestCase(CreateTestUsers):
    def create_loan(self):
        data = {"amount": 100000, "tenure": 12}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        loan_id = json.loads(response.content).get("loan_id")
        return loan_id

    def test_approval_success(self):
        loan_id = self.create_loan()

        request = self.factory.post(path="/loans/<loan_id>/approve")
        request.user_roles = ["approver"]
        request.user_obj = self.approver_user
        view = ApproveLoan.as_view()
        response = view(request, loan_id)
        self.assertEqual(response.status_code, 200)
        loan_info = Loan.get_loan_info(
            **{"id": loan_id, "borrower": self.borrower_user}
        )
        self.assertEqual(loan_id, loan_info.get("id"))
        self.assertEqual("approved", loan_info.get("status"))

    def test_approval_invalid_user(self):
        loan_id = self.create_loan()

        request = self.factory.post(
            path="/loans/<loan_id>/approve",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = ApproveLoan.as_view()
        response = view(request, loan_id)
        self.assertEqual(response.status_code, 403)

    def test_approval_invalid_loan_id(self):
        loan_id = "xyz"
        request = self.factory.post(
            path="/loans/<loan_id>/approve",
        )
        request.user_roles = ["approver"]
        request.user_obj = self.approver_user
        view = ApproveLoan.as_view()
        response = view(request, loan_id)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(f"Loan with id {loan_id} does not exist", content.get("Error"))


class TestRepayments(CreateTestUsers):

    def create_loan(self):
        data = {"amount": 10000, "tenure": 5}
        request = self.factory.post(
            path="/loans/create",
            data=data,
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = CreateLoanViewSet.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        loan_id = json.loads(response.content).get("loan_id")
        return loan_id

    def approve_loan(self, loan_id):
        request = self.factory.post(path="/loans/<loan_id>/approve")
        request.user_roles = ["approver"]
        request.user_obj = self.approver_user
        view = ApproveLoan.as_view()
        response = view(request, loan_id)
        self.assertEqual(response.status_code, 200)
        loan_info = Loan.get_loan_info(
            **{"id": loan_id, "borrower": self.borrower_user}
        )
        self.assertEqual(loan_id, loan_info.get("id"))
        self.assertEqual("approved", loan_info.get("status"))

    def test_repayments_unapproved_loan(self):
        loan_id = self.create_loan()
        request = self.factory.post(
            "loan/<loan-id>/repayment",
            data={"amount": 2000},
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = RepaymentView.as_view()
        response = view(request, loan_id)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(f"Loan is not approved yet", content.get("Error"))

    def test_loan_does_not_exist(self):
        request = self.factory.post(
            "loan/<loan-id>/repayment",
            data={"amount": 2000},
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = RepaymentView.as_view()
        response = view(request, "xyz")
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(f"No Loan xyz is associated to you", content.get("Error"))

    def test_repayments_insufficient_amount(self):
        loan_id = self.create_loan()
        self.approve_loan(loan_id)
        request = self.factory.post(
            "loan/<loan-id>/repayment",
            data={"amount": 200},
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = RepaymentView.as_view()
        response = view(request, loan_id)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(f"Minimum allowed amount is 2000.0", content.get("Error"))

    def test_repayments_success(self):
        loan_id = self.create_loan()
        self.approve_loan(loan_id)
        for i in range(0, 5):
            request = self.factory.post(
                "loan/<loan-id>/repayment",
                data={"amount": 2000},
                content_type="application/json",
            )
            request.user_roles = ["borrower"]
            request.user_obj = self.borrower_user
            view = RepaymentView.as_view()
            response = view(request, loan_id)
            self.assertEqual(response.status_code, 200)

        request = self.factory.post(
            "loan/<loan-id>/repayment",
            data={"amount": 2000},
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = RepaymentView.as_view()
        response = view(request, loan_id)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(f"Loan is already paid", content.get("Error"))

    def test_overpayment_than_actual_amount(self):
        loan_id = self.create_loan()
        self.approve_loan(loan_id)
        request = self.factory.post(
            "loan/<loan-id>/repayment",
            data={"amount": 10005},
            content_type="application/json",
        )
        request.user_roles = ["borrower"]
        request.user_obj = self.borrower_user
        view = RepaymentView.as_view()
        response = view(request, loan_id)
        self.assertEqual(response.status_code, 400)
        content = json.loads(response.content)
        self.assertEqual(
            f"Amount Should not be greater than actual loan amount",
            content.get("Error"),
        )

    def test_over_repayment(self):
        loan_id = self.create_loan()
        self.approve_loan(loan_id)
        for i in range(0, 2):
            request = self.factory.post(
                "loan/<loan-id>/repayment",
                data={"amount": 5001},
                content_type="application/json",
            )
            request.user_roles = ["borrower"]
            request.user_obj = self.borrower_user
            view = RepaymentView.as_view()
            response = view(request, loan_id)
            self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            {"message": "Repayment successful with overpayment", "overpayment": 2.0},
            content,
        )
