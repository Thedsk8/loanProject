from datetime import timedelta
from loan.models import Repayment


class PaymentStrategy:
    def generate_schedule(self, loan):
        raise NotImplementedError("Subclasses should implement this method")


class WeeklyPaymentStrategy(PaymentStrategy):
    def generate_schedule(self, loan):
        repayment_amount = loan.amount / loan.tenure
        repayments = []

        for i in range(loan.tenure):
            due_date = loan.issued_at + timedelta(weeks=i + 1)
            repayment = Repayment(
                loan=loan, amount=repayment_amount, due_date=due_date, status="pending"
            )
            repayment.save()
            repayments.append(repayment)

        return repayments
