"""
Stripe Payment Service
Handles Stripe payment processing and webhook handling
"""

import json
import os
from typing import Any, Dict, Optional

import stripe
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.config.logging import get_project_logger
from api.models import Payment, User
from api.models.pricing import PaymentMethod, PaymentStatus
from api.schemas import PaymentIntentCreate, PaymentIntentResponse, PaymentWebhookData
from api.services.business.pricing_service import credits_service

logger = get_project_logger()

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


class CheckoutSessionRequest(BaseModel):
    plan_id: str
    plan_type: str  # "subscription" or "credits"
    custom_amount: float = None


class StripeService:
    def __init__(self):
        logger.info("StripeService initialized")
        if not stripe.api_key:
            logger.warning("STRIPE_SECRET_KEY not found in environment variables")

    def create_checkout_session(self, db: Session, user_id: str, request: CheckoutSessionRequest) -> Dict[str, str]:
        """Create a Stripe checkout session for subscription or credits purchase"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")

            # Create or get Stripe customer
            stripe_customer_id = user.billing_id
            if not stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email, name=user.username or user.email, metadata={"user_id": str(user_id)}
                )
                stripe_customer_id = customer.id
                user.billing_id = stripe_customer_id
                db.commit()

            # Get pricing information
            from api.services.business.pricing_service import PRICES

            if request.plan_type == "subscription":
                plan_info = PRICES["subscription_plans"].get(request.plan_id)
                if not plan_info:
                    raise ValueError(f"Subscription plan {request.plan_id} not found")

                if plan_info["price"] == 0:
                    raise ValueError("Free plan does not require payment")

                stripe_price_id = plan_info["stripe_price_id"]
                if not stripe_price_id:
                    # Use custom pricing when Stripe price ID is not configured
                    amount_cents = int(plan_info["price"] * 100)
                    session = stripe.checkout.Session.create(
                        customer=stripe_customer_id,
                        payment_method_types=["card"],
                        line_items=[
                            {
                                "price_data": {
                                    "currency": "usd",
                                    "product_data": {
                                        "name": f'{plan_info["name"]} Plan',
                                        "description": f'Monthly subscription to {plan_info["name"]} plan',
                                    },
                                    "unit_amount": amount_cents,
                                    "recurring": {
                                        "interval": "month",
                                    },
                                },
                                "quantity": 1,
                            }
                        ],
                        mode="subscription",
                        success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/settings?tab=subscription&success=true",
                        cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/settings/subscription?cancelled=true",
                        metadata={"user_id": str(user_id), "plan_id": request.plan_id, "plan_type": "subscription"},
                    )
                else:
                    # Use configured Stripe price ID
                    session = stripe.checkout.Session.create(
                        customer=stripe_customer_id,
                        payment_method_types=["card"],
                        line_items=[
                            {
                                "price": stripe_price_id,
                                "quantity": 1,
                            }
                        ],
                        mode="subscription",
                        success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/settings?tab=subscription&success=true",
                        cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/settings/subscription?cancelled=true",
                        metadata={"user_id": str(user_id), "plan_id": request.plan_id, "plan_type": "subscription"},
                    )

            elif request.plan_type == "credits":
                if request.custom_amount:
                    # Custom amount purchase
                    amount_cents = int(request.custom_amount * 100)
                    credits_purchased = int(request.custom_amount * 20)  # 20 credits per dollar

                    session = stripe.checkout.Session.create(
                        customer=stripe_customer_id,
                        payment_method_types=["card"],
                        line_items=[
                            {
                                "price_data": {
                                    "currency": "usd",
                                    "product_data": {
                                        "name": f"Custom Credits - {credits_purchased} credits",
                                        "description": f"Purchase {credits_purchased} credits for ${request.custom_amount}",
                                    },
                                    "unit_amount": amount_cents,
                                },
                                "quantity": 1,
                            }
                        ],
                        mode="payment",
                        success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/credits?success=true",
                        cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/credits/purchase?cancelled=true",
                        metadata={
                            "user_id": str(user_id),
                            "plan_type": "credits",
                            "custom_amount": str(request.custom_amount),
                            "credits_purchased": str(credits_purchased),
                        },
                    )
                else:
                    # Predefined credits package
                    package_info = PRICES["credits_packages"].get(request.plan_id)
                    if not package_info:
                        raise ValueError(f"Credits package {request.plan_id} not found")

                    stripe_price_id = package_info["stripe_price_id"]
                    if not stripe_price_id:
                        # Use custom pricing when Stripe price ID is not configured
                        amount_cents = int(package_info["price"] * 100)
                        total_credits = package_info["credits"] + package_info.get("bonus", 0)
                        session = stripe.checkout.Session.create(
                            customer=stripe_customer_id,
                            payment_method_types=["card"],
                            line_items=[
                                {
                                    "price_data": {
                                        "currency": "usd",
                                        "product_data": {
                                            "name": package_info["name"],
                                            "description": f'Purchase {total_credits} credits ({package_info["credits"]} + {package_info.get("bonus", 0)} bonus)',
                                        },
                                        "unit_amount": amount_cents,
                                    },
                                    "quantity": 1,
                                }
                            ],
                            mode="payment",
                            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/credits?success=true",
                            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/credits/purchase?cancelled=true",
                            metadata={
                                "user_id": str(user_id),
                                "plan_id": request.plan_id,
                                "plan_type": "credits",
                                "credits_purchased": str(total_credits),
                            },
                        )
                    else:
                        # Use configured Stripe price ID
                        session = stripe.checkout.Session.create(
                            customer=stripe_customer_id,
                            payment_method_types=["card"],
                            line_items=[
                                {
                                    "price": stripe_price_id,
                                    "quantity": 1,
                                }
                            ],
                            mode="payment",
                            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/credits?success=true",
                            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/credits/purchase?cancelled=true",
                            metadata={"user_id": str(user_id), "plan_id": request.plan_id, "plan_type": "credits"},
                        )
            else:
                raise ValueError(f"Invalid plan type: {request.plan_type}")

            logger.info(f"Created checkout session {session.id} for user {user_id}")

            return {"checkout_url": session.url, "session_id": session.id}

        except Exception as e:
            logger.error(f"Error creating checkout session for user {user_id}: {str(e)}")
            raise

    def create_payment_intent(
        self, db: Session, user_id: str, payment_data: PaymentIntentCreate
    ) -> PaymentIntentResponse:
        """Create a Stripe payment intent for credits purchase"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")

            amount_cents = int(payment_data.amount_dollars * 100)
            credits_purchased = int(payment_data.amount_dollars * payment_data.credits_per_dollar)

            # Create or get Stripe customer
            stripe_customer_id = user.billing_id
            if not stripe_customer_id:
                customer = stripe.Customer.create(
                    email=user.email, name=user.username or user.email, metadata={"user_id": str(user_id)}
                )
                stripe_customer_id = customer.id
                user.billing_id = stripe_customer_id
                db.commit()

            # Create payment intent
            intent_data = {
                "amount": amount_cents,
                "currency": payment_data.currency,
                "customer": stripe_customer_id,
                "metadata": {
                    "user_id": str(user_id),
                    "credits_purchased": str(credits_purchased),
                    "credits_per_dollar": str(payment_data.credits_per_dollar),
                },
            }

            if payment_data.payment_method_id:
                intent_data["payment_method"] = payment_data.payment_method_id
                intent_data["confirmation_method"] = "manual"
                intent_data["confirm"] = True

            payment_intent = stripe.PaymentIntent.create(**intent_data)

            # Create payment record in database
            payment = Payment(
                user_id=user_id,
                stripe_payment_intent_id=payment_intent.id,
                stripe_customer_id=stripe_customer_id,
                amount_cents=amount_cents,
                currency=payment_data.currency,
                payment_method=PaymentMethod.STRIPE_CARD,
                credits_purchased=credits_purchased,
                credits_per_dollar=payment_data.credits_per_dollar,
                status=PaymentStatus.PENDING,
                description=payment_data.description or f"Purchase of {credits_purchased} credits",
            )

            db.add(payment)
            db.commit()
            db.refresh(payment)

            logger.info(f"Created payment intent {payment_intent.id} for user {user_id}")

            return PaymentIntentResponse(
                client_secret=payment_intent.client_secret,
                payment_intent_id=payment_intent.id,
                amount_cents=amount_cents,
                credits_purchased=credits_purchased,
                status=payment_intent.status,
            )

        except Exception as e:
            logger.error(f"Error creating payment intent for user {user_id}: {str(e)}")
            db.rollback()
            raise

    def confirm_payment_intent(self, db: Session, payment_intent_id: str) -> Payment:
        """Confirm a payment intent"""
        try:
            payment = db.query(Payment).filter(Payment.stripe_payment_intent_id == payment_intent_id).first()

            if not payment:
                raise ValueError(f"Payment not found for intent {payment_intent_id}")

            # Retrieve payment intent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == "succeeded":
                payment.status = PaymentStatus.COMPLETED
                payment.stripe_charge_id = intent.latest_charge
                payment.completed_at = intent.created

                # Add credits to user's account
                credits_service.add_credits(
                    db=db,
                    user_id=str(payment.user_id),
                    amount=payment.credits_purchased,
                    transaction_type="purchased",
                    description=f"Credits purchase - {payment.credits_purchased} credits",
                    reference_id=str(payment.id),
                    reference_type="payment",
                )

                db.commit()
                logger.info(f"Payment {payment_intent_id} confirmed and credits added")

            elif intent.status == "requires_payment_method":
                payment.status = PaymentStatus.FAILED
                db.commit()
                logger.warning(f"Payment {payment_intent_id} requires payment method")

            return payment

        except Exception as e:
            logger.error(f"Error confirming payment intent {payment_intent_id}: {str(e)}")
            db.rollback()
            raise

    def handle_webhook(self, db: Session, payload: str, signature: str) -> bool:
        """Handle Stripe webhook events"""
        try:
            if not STRIPE_WEBHOOK_SECRET:
                logger.warning("STRIPE_WEBHOOK_SECRET not configured")
                return False

            event = stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)

            logger.info(f"Received Stripe webhook: {event['type']}")

            if event["type"] == "payment_intent.succeeded":
                payment_intent = event["data"]["object"]
                self._handle_payment_succeeded(db, payment_intent)

            elif event["type"] == "payment_intent.payment_failed":
                payment_intent = event["data"]["object"]
                self._handle_payment_failed(db, payment_intent)

            elif event["type"] == "payment_intent.canceled":
                payment_intent = event["data"]["object"]
                self._handle_payment_canceled(db, payment_intent)

            return True

        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return False

    def _handle_payment_succeeded(self, db: Session, payment_intent: Dict[str, Any]):
        """Handle successful payment"""
        try:
            payment = db.query(Payment).filter(Payment.stripe_payment_intent_id == payment_intent["id"]).first()

            if not payment:
                logger.warning(f"Payment not found for intent {payment_intent['id']}")
                return

            if payment.status == PaymentStatus.COMPLETED:
                logger.info(f"Payment {payment_intent['id']} already processed")
                return

            payment.status = PaymentStatus.COMPLETED
            payment.stripe_charge_id = payment_intent.get("latest_charge")
            payment.completed_at = payment_intent["created"]

            # Add credits to user's account
            credits_service.add_credits(
                db=db,
                user_id=str(payment.user_id),
                amount=payment.credits_purchased,
                transaction_type="purchased",
                description=f"Credits purchase - {payment.credits_purchased} credits",
                reference_id=str(payment.id),
                reference_type="payment",
            )

            db.commit()
            logger.info(f"Payment {payment_intent['id']} processed successfully")

        except Exception as e:
            logger.error(f"Error handling payment succeeded: {str(e)}")
            db.rollback()

    def _handle_payment_failed(self, db: Session, payment_intent: Dict[str, Any]):
        """Handle failed payment"""
        try:
            payment = db.query(Payment).filter(Payment.stripe_payment_intent_id == payment_intent["id"]).first()

            if payment:
                payment.status = PaymentStatus.FAILED
                db.commit()
                logger.info(f"Payment {payment_intent['id']} marked as failed")

        except Exception as e:
            logger.error(f"Error handling payment failed: {str(e)}")
            db.rollback()

    def _handle_payment_canceled(self, db: Session, payment_intent: Dict[str, Any]):
        """Handle canceled payment"""
        try:
            payment = db.query(Payment).filter(Payment.stripe_payment_intent_id == payment_intent["id"]).first()

            if payment:
                payment.status = PaymentStatus.CANCELLED
                db.commit()
                logger.info(f"Payment {payment_intent['id']} marked as canceled")

        except Exception as e:
            logger.error(f"Error handling payment canceled: {str(e)}")
            db.rollback()

    def get_payment_history(self, db: Session, user_id: str, limit: int = 50) -> list[Payment]:
        """Get user's payment history"""
        try:
            payments = (
                db.query(Payment)
                .filter(Payment.user_id == user_id)
                .order_by(Payment.created_at.desc())
                .limit(limit)
                .all()
            )
            return payments

        except Exception as e:
            logger.error(f"Error getting payment history for user {user_id}: {str(e)}")
            raise

    def refund_payment(self, db: Session, payment_id: str, amount_cents: Optional[int] = None) -> bool:
        """Refund a payment"""
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")

            if payment.status != PaymentStatus.COMPLETED:
                raise ValueError(f"Payment {payment_id} is not completed")

            if not payment.stripe_charge_id:
                raise ValueError(f"No charge ID found for payment {payment_id}")

            # Create refund in Stripe
            refund_amount = amount_cents or payment.amount_cents
            refund = stripe.Refund.create(charge=payment.stripe_charge_id, amount=refund_amount)

            # Update payment status
            payment.status = PaymentStatus.REFUNDED

            # Calculate credits to refund
            refund_credits = int((refund_amount / payment.amount_cents) * payment.credits_purchased)

            # Refund credits to user
            if refund_credits > 0:
                credits_service.refund_credits(
                    db=db,
                    user_id=str(payment.user_id),
                    amount=refund_credits,
                    description=f"Refund for payment {payment_id}",
                    reference_id=payment_id,
                )

            db.commit()
            logger.info(f"Refunded payment {payment_id}: {refund_amount} cents, {refund_credits} credits")
            return True

        except Exception as e:
            logger.error(f"Error refunding payment {payment_id}: {str(e)}")
            db.rollback()
            return False

    def process_payment_intent_creation(self, db: Session, user_id: str, payment_data: PaymentIntentCreate) -> PaymentIntentResponse:
        """Process payment intent creation with full business logic"""
        return self.create_payment_intent(db, user_id, payment_data)

    def process_checkout_session_creation(self, db: Session, user_id: str, checkout_request: CheckoutSessionRequest) -> Dict[str, str]:
        """Process checkout session creation with full business logic"""
        return self.create_checkout_session(db, user_id, checkout_request)

    def process_payment_confirmation(self, db: Session, payment_intent_id: str) -> dict:
        """Process payment confirmation with response formatting"""
        payment = self.confirm_payment_intent(db, payment_intent_id)
        return {
            "message": "Payment confirmed successfully",
            "payment_id": str(payment.id),
            "status": payment.status.value,
            "credits_added": payment.credits_purchased,
        }

    def process_payment_refund(self, db: Session, payment_id: str, amount_cents: Optional[int] = None) -> dict:
        """Process payment refund with response formatting"""
        success = self.refund_payment(db, payment_id, amount_cents)
        if success:
            return {"message": "Refund processed successfully"}
        else:
            raise ValueError("Failed to process refund")

    def process_webhook(self, db: Session, payload: str, signature: str) -> dict:
        """Process webhook with response formatting"""
        success = self.handle_webhook(db, payload, signature)
        if success:
            return {"status": "success"}
        else:
            raise ValueError("Webhook processing failed")


# Create a default instance
stripe_service = StripeService()
