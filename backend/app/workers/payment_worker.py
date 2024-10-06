from datetime import datetime

from sqlmodel import Session, create_engine, select

from app.models import Payment, PaymentStatus
from app.workers.celery_worker import celery_worker


@celery_worker.task(name="process_payment_task")
def process_payment_task(payment_id: str):
    with Session(create_engine) as session:
        payment = session.exec(select(Payment).where(Payment.id == payment_id)).first()

        if not payment:
            return {"error": "Payment not found"}

        # Simulate payment processing
        try:
            payment.status = PaymentStatus.COMPLETED
            payment.completed_at = datetime.utcnow()
            session.add(payment)
            session.commit()
            return {"status": "Payment processed", "payment_id": payment_id}
        except Exception as e:
            payment.status = PaymentStatus.FAILED
            session.add(payment)
            session.commit()
            return {"error": str(e)}
