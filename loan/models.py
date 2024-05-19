import logging
import uuid

from django.db import models
from django.utils import timezone

from users.models import User


logger = logging.getLogger(__name__)


class Loan(models.Model):
    STATUS_CHOICES = [("approved", "Approved"), ("pending", "Pending")]

    PAYMENT_STRATEGY_CHOICES = [
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.FloatField(blank=False)
    tenure = models.IntegerField(blank=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    paid = models.BooleanField(default=False)
    borrower = models.ForeignKey(
        User, related_name="borrowed_loans", on_delete=models.CASCADE
    )
    approver = models.ForeignKey(
        User,
        related_name="approved_loans",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    issued_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_strategy = models.CharField(
        max_length=10, choices=PAYMENT_STRATEGY_CHOICES, default="weekly"
    )

    @classmethod
    def create_loan(cls, **kwargs):
        try:
            loan_obj = Loan.objects.create(**kwargs)
            return loan_obj.id
        except Exception as err:
            logger.exception(f"Error Occurred while creating Load {err}")
            raise Exception(err)

    @classmethod
    def get_loan_info(cls, **kwargs):
        try:
            loan_obj = Loan.objects.get(**kwargs)
            return loan_obj.to_dict()
        except Loan.DoesNotExist:
            return {}
        except Exception as err:
            logger.exception(
                {"Error": f"Error Occurred while Loan Fetching Info {err}"}
            )
            return {}

    @classmethod
    def get_loan_obj(cls, **kwargs):
        try:
            loan_obj = Loan.objects.get(**kwargs)
            return loan_obj
        except Loan.DoesNotExist:
            return {}
        except Exception as err:
            logger.exception(
                {"Error": f"Error Occurred while Loan Fetching Object {err}"}
            )
            return {}

    @classmethod
    def is_exist(cls, loan_id):
        try:
            return Loan.objects.filter(id=loan_id).exists()
        except Exception as err:
            logger.exception(
                {"Error": f"Error Occurred while checking Loan Existence {err}"}
            )
            return False

    def to_dict(self):
        return {
            "id": str(self.id),
            "amount": self.amount,
            "tenure": self.tenure,
            "status": self.status,
            "paid": self.paid,
            "borrower_id": str(self.borrower_id),
            "approver_id": str(self.approver_id) if self.approver_id else None,
            "issued_at": self.issued_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "payment_strategy": self.payment_strategy,
        }


class Repayment(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("paid", "Paid")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan = models.ForeignKey(Loan, related_name="repayments", on_delete=models.CASCADE)
    amount = models.FloatField(blank=False)
    due_date = models.DateTimeField(blank=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"Repayment {self.id} - {self.loan.id}"
