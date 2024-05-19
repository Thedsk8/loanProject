from django.urls import path
from loan.views import ApproveLoan
from loan.views import CreateLoanViewSet
from loan.views import FetchLoanInfo
from loan.views import RepaymentView


urlpatterns = [
    path("create", view=CreateLoanViewSet.as_view(), name="create_loan"),
    path(
        r"<loan_id>/fetch",
        view=FetchLoanInfo.as_view(),
        name="fetch_loan",
    ),
    path(
        r"<loan_id>/approve",
        view=ApproveLoan.as_view(),
        name="approve_loan",
    ),
    path(
        r"<loan_id>/repayment",
        view=RepaymentView.as_view(),
        name="approve_loan",
    ),
]
