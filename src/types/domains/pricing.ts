// PRICING DOMAIN TYPES

export interface PricingPlan {
  id: string;
  name: string;
  price: string;
  credits: string;
  features: string[];
  popular?: boolean;
  color: string;
  icon: string;
  billingInterval: 'monthly' | 'yearly';
  stripePriceId?: string;
  stripeProductId?: string;
}

export interface PricingStats {
  totalPlans: number;
  activePlans: number;
  totalRevenue: number;
  conversionRate: number;
}

export interface StripeConfig {
  publishableKey: string;
  products: {
    [key: string]: {
      priceId: string;
      productId: string;
    };
  };
}

export interface StripeData {
  products: StripeProduct[];
  prices: StripePrice[];
  paymentLinks: StripePaymentLink[];
  customers: StripeCustomer[];
}

export interface StripeProduct {
  id: string;
  name: string;
  description: string;
  active: boolean;
  created: number;
  defaultPrice?: string;
}

export interface StripePrice {
  id: string;
  object: string;
  active: boolean;
  currency: string;
  unitAmount: number;
  recurring?: {
    interval: string;
  };
  product: string;
  created: number;
}

export interface StripePaymentLink {
  id: string;
  url: string;
  active: boolean;
  created: number;
  lineItems: Array<{
    price: string;
    quantity: number;
  }>;
}

export interface StripeCustomer {
  id: string;
  email: string;
  name?: string;
  created: number;
  subscriptions?: {
    data: Array<{
      id: string;
      status: string;
      currentPeriodEnd: number;
    }>;
  };
}



