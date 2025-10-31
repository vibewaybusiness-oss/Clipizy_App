import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from api.db import Base
from sqlalchemy.dialects.postgresql import UUID as GUID


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    STRIPE_CARD = "stripe_card"
    STRIPE_BANK = "stripe_bank"
    PAYPAL = "paypal"
    CRYPTO = "crypto"


class CreditsTransactionType(str, enum.Enum):
    EARNED = "earned"
    SPENT = "spent"
    PURCHASED = "purchased"
    REFUNDED = "refunded"
    BONUS = "bonus"
    ADMIN_ADJUSTMENT = "admin_adjustment"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Stripe integration
    stripe_payment_intent_id = Column(String, nullable=True, unique=True)
    stripe_customer_id = Column(String, nullable=True)
    stripe_charge_id = Column(String, nullable=True)

    # Payment details
    amount_cents = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String, default="usd", nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

    # Credits purchase details
    credits_purchased = Column(Integer, nullable=False)
    credits_per_dollar = Column(Integer, default=100, nullable=False)  # 100 credits per $1

    # Metadata
    description = Column(Text, nullable=True)
    payment_metadata = Column(Text, nullable=True)  # JSON string for additional data

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")

    def __repr__(self):
        return (
            f"<Payment(id={self.id}, user_id={self.user_id}, amount_cents={self.amount_cents}, status={self.status})>"
        )


class CreditsTransaction(Base):
    __tablename__ = "credits_transactions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    transaction_type = Column(Enum(CreditsTransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # Positive for earned/purchased, negative for spent
    balance_after = Column(Integer, nullable=False)  # User's balance after this transaction

    description = Column(Text, nullable=True)
    reference_id = Column(String, nullable=True)  # Reference to job, payment, etc.
    reference_type = Column(String, nullable=True)  # job, payment, admin, etc.

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="credits_transactions")

    def __repr__(self):
        return f"<CreditsTransaction(id={self.id}, user_id={self.user_id}, type={self.transaction_type}, amount={self.amount})>"
