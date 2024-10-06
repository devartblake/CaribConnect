from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.db import create_engine, create_payment_record, get_database_session
from app.models import Payment, User
from app.schemas.payment import PaymentRequest, PaymentResponse
from app.services.tasks import process_payment, refund_payment
from app.workers.payment_worker import process_payment_task

router = APIRouter()

@router.post("/pay/")
async def pay(payment_id: str, user_id: str, amount: float):
    # Create a new payment record
    with Session(create_engine) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        payment = Payment(user_id=user_id, amount=amount)
        session.add(payment)
        session.commit()

        # Trigger payment processing in background
        process_payment_task.delay(str(payment.id))

        return {"status": "Payment initiated", "payment_id": str(payment.id)}

@router.post("/process-payment/", response_model=PaymentResponse)
async def process_payment(payment: PaymentRequest, db: Session = Depends(get_database_session)):
    # Create payment record in the database
    db_payment = create_payment_record(db, payment)
    db.commit()
    db.refresh(db_payment)

    # Trigger Celery task
    task = process_payment.delay(db_payment.id)

    return PaymentResponse(task_id=task.id, status="processing")

@router.post("/refund_payment/")
async def refund_payment_route(payment_id: int, amount: float):
    refund_payment.delay(payment_id, amount)
    return {"message": "Refund is being processed"}
