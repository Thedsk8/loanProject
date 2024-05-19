import random
import string
from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = "Create initial test users"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                "These are initial set of test users and are only meant for testing"
            )
        )

        users_data = [
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": self._generate_password(),
                "roles": ["borrower"],
            },
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com",
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
            {
                "first_name": "Jack",
                "last_name": "Daniels",
                "email": "jack.daniels@example.com",
                "password": self._generate_password(),
                "roles": ["borrower", "approver"],
            },
        ]

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
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"User {user.email} created successfully with Password {user.password} and roles {user.roles}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"User {user.email} already exists with Password {user.password} and roles {user.roles}"
                    )
                )

    @classmethod
    def _generate_password(cls):
        return "".join(
            random.choice(string.ascii_letters + string.digits) for _ in range(8)
        )
