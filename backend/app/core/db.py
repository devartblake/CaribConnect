from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import Payment, User, UserCreate
from app.schemas.payment import PaymentRequest

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)


# Dependency to get a session
def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_payment_record(db: Session, payment: PaymentRequest):
    db_payment = Payment(
        amount=payment.amount,
        user_id=payment.user_id,
        # Add other fields as necessary
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment
