import logging
import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


logger = logging.getLogger(__name__)


class User(models.Model):
    first_name = models.CharField(blank=False, max_length=100)
    last_name = models.CharField(blank=False, max_length=100)
    email = models.EmailField(blank=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # passwords needs to save as hash in database but for sake of simplicity here this is skipped
    password = models.CharField(max_length=1000, blank=False)
    roles = ArrayField(
        models.CharField(
            max_length=20, choices=[("borrower", "Borrower"), ("approver", "Approver")]
        ),
        default=list,
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email

    def can_borrow_loans(self):
        return "borrower" in self.roles

    def can_approve_loans(self):
        return "approver" in self.roles

    @classmethod
    def get_user_object_with_email_and_password(cls, email, password):
        try:
            user_obj = User.objects.get(email=email, password=password)
            return user_obj
        except User.DoesNotExist:
            logger.exception(f"User with given email does not exist {email}")
        except Exception as err:
            logger.exception(
                f"Exception Occurred while fetching user with {email} and {err}"
            )
