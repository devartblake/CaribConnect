from pydantic import BaseModel


class PaymentRequest(BaseModel):
    amount: float
    user_id: int
    # Add other relevant fields

class PaymentResponse(BaseModel):
    task_id: str
    status: str
