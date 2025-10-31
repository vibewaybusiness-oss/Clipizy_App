import { BaseApiClient } from './base';
import { API_BASE_URL, API_PATHS } from './config';

export interface PaymentService {
  createCheckoutSession: (options: CheckoutOptions) => Promise<any>;
  createSubscription: (options: SubscriptionOptions) => Promise<any>;
  cancelSubscription: (subscriptionId: string) => Promise<any>;
  getPaymentHistory: () => Promise<any>;
}

export interface CheckoutOptions {
  planId: string;
  successUrl: string;
  cancelUrl: string;
  customerEmail?: string;
}

export interface SubscriptionOptions {
  planId: string;
  customerEmail?: string;
}

class PaymentApiClient extends BaseApiClient {
  constructor() {
    super(API_BASE_URL);
  }

  async createCheckoutSession(options: CheckoutOptions): Promise<any> {
    return this.post(API_PATHS.PAYMENTS.CHECKOUT, options);
  }

  async createSubscription(options: SubscriptionOptions): Promise<any> {
    return this.post(API_PATHS.PAYMENTS.SUBSCRIPTIONS, options);
  }

  async cancelSubscription(subscriptionId: string): Promise<any> {
    return this.delete(`${API_PATHS.PAYMENTS.SUBSCRIPTIONS}/${subscriptionId}`);
  }

  async getPaymentHistory(): Promise<any> {
    return this.get(API_PATHS.PAYMENTS.SUBSCRIPTIONS);
  }
}

export const paymentService = new PaymentApiClient();
