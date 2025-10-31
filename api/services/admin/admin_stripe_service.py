"""
ADMIN STRIPE SERVICE
Business logic for admin Stripe management
"""

import os
import logging
from typing import Dict, Any, List

import stripe

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class AdminStripeService:
    @staticmethod
    def get_products() -> Dict[str, Any]:
        """
        Get all Stripe products
        
        Returns:
            Dict containing products data
        """
        products = stripe.Product.list(limit=100)
        return {"success": True, "data": products.data, "count": len(products.data)}

    @staticmethod
    def get_prices() -> Dict[str, Any]:
        """
        Get all Stripe prices
        
        Returns:
            Dict containing prices data
        """
        prices = stripe.Price.list(limit=100)
        return {"success": True, "data": prices.data, "count": len(prices.data)}

    @staticmethod
    def get_payment_links() -> Dict[str, Any]:
        """
        Get all Stripe payment links
        
        Returns:
            Dict containing payment links data
        """
        payment_links = stripe.PaymentLink.list(limit=100)
        return {"success": True, "data": payment_links.data, "count": len(payment_links.data)}

    @staticmethod
    def get_customers() -> Dict[str, Any]:
        """
        Get all Stripe customers
        
        Returns:
            Dict containing customers data
        """
        customers = stripe.Customer.list(limit=100)
        return {"success": True, "data": customers.data, "count": len(customers.data)}

    @staticmethod
    def get_subscriptions() -> Dict[str, Any]:
        """
        Get all Stripe subscriptions
        
        Returns:
            Dict containing subscriptions data
        """
        subscriptions = stripe.Subscription.list(limit=100)
        return {"success": True, "data": subscriptions.data, "count": len(subscriptions.data)}

    @staticmethod
    def get_payments() -> Dict[str, Any]:
        """
        Get recent Stripe payments
        
        Returns:
            Dict containing payments data
        """
        payments = stripe.PaymentIntent.list(limit=100)
        return {"success": True, "data": payments.data, "count": len(payments.data)}

    @staticmethod
    def get_balance() -> Dict[str, Any]:
        """
        Get Stripe account balance
        
        Returns:
            Dict containing balance data
        """
        balance = stripe.Balance.retrieve()
        return {"success": True, "data": balance}

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Get Stripe account statistics
        
        Returns:
            Dict containing statistics data
        """
        products = stripe.Product.list(limit=1)
        prices = stripe.Price.list(limit=1)
        customers = stripe.Customer.list(limit=1)
        subscriptions = stripe.Subscription.list(limit=1)
        payment_links = stripe.PaymentLink.list(limit=1)

        stats = {
            "products_count": products.total_count,
            "prices_count": prices.total_count,
            "customers_count": customers.total_count,
            "subscriptions_count": subscriptions.total_count,
            "payment_links_count": payment_links.total_count,
        }

        return {"success": True, "data": stats}
