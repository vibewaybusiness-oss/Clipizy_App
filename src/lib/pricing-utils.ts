// =========================
// PRICING UTILITIES
// =========================

export interface PricingPlan {
  id: string;
  name: string;
  price: string;
  credits: string;
  features: string[];
  popular?: boolean;
  color: string;
  icon: string;
}

export interface PricingStats {
  totalPlans: number;
  activePlans: number;
  totalRevenue: number;
  conversionRate: number;
}

// =========================
// PRICING CONFIGURATION
// =========================

export const PRICING_PLANS: PricingPlan[] = [
  {
    id: 'free',
    name: 'Free Tier',
    price: '$0/month',
    credits: '60 credits',
    features: [
      '60 Credits Included',
      '720p Max (Watermarked)',
      '1 GB Cloud Storage (Max 5 drafts/7 days)',
      'Basic BPM & Key Analysis',
      'Regular Model LLM',
      'Basic Views Count Analytics',
      'Community Support'
    ],
    color: 'bg-gray-500',
    icon: '🎵'
  },
  {
    id: 'creator',
    name: 'Tier 1: Creator',
    price: '$25/month',
    credits: '1,500 credits',
    features: [
      '1,500 Credits Included',
      '1080p Full HD (No Watermark)',
      '50 GB Cloud Storage (Unlimited Drafts)',
      'Full Advanced Music Analysis',
      'Regular Model LLM',
      'Video Automation Access (Scheduling Only)',
      '1 Upload/Day Automated',
      'Standard Priority Queue',
      'Commercial Licensing',
      'Email Support (Standard SLA)'
    ],
    popular: true,
    color: 'bg-blue-500',
    icon: '🎬'
  },
  {
    id: 'pro',
    name: 'Tier 2: Pro',
    price: '$59/month',
    credits: '5,000 credits',
    features: [
      '5,000 Credits Included',
      '1080p Full HD',
      '250 GB Cloud Storage (Unlimited History)',
      'Full Advanced Music Analysis',
      'Regular Model LLM',
      'Video Automation Access (Auto-Upload Included)',
      '4 Uploads/Day Automated',
      'Standard Priority Queue',
      'Full Social Media Stats & Potential Gains',
      'Priority Email Support'
    ],
    color: 'bg-purple-500',
    icon: '👑'
  },
  {
    id: 'business',
    name: 'Tier 3: Business',
    price: '$119/month',
    credits: '12,500 credits',
    features: [
      '12,500 Credits Included',
      '1080p Full HD',
      '1 TB Cloud Storage (Unlimited History)',
      'Full Advanced Music Analysis',
      'Premium Model LLM',
      'Video Automation Access (Advanced Queue Management)',
      '5 Uploads/Day Automated',
      'Priority Queue Access',
      'Full Social Media Stats & Dedicated Reporting',
      'Dedicated Account Manager/SLA'
    ],
    color: 'bg-amber-500',
    icon: '🏢'
  }
];

// =========================
// PRICING CALCULATIONS
// =========================

export function calculatePlanValue(plan: PricingPlan): number {
  const credits = parseInt(plan.credits.replace(/[^\d]/g, ''));
  const price = parseFloat(plan.price.replace(/[^\d.]/g, ''));
  return credits / price;
}

export function getBestValuePlan(plans: PricingPlan[] = PRICING_PLANS): PricingPlan {
  return plans.reduce((best, current) => {
    const currentValue = calculatePlanValue(current);
    const bestValue = calculatePlanValue(best);
    return currentValue > bestValue ? current : best;
  });
}

export function formatPrice(price: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(price);
}

export function formatCredits(credits: number): string {
  if (credits >= 1000) {
    return `${(credits / 1000).toFixed(credits % 1000 === 0 ? 0 : 1)}k credits`;
  }
  return `${credits} credits`;
}

// =========================
// STRIPE INTEGRATION UTILITIES
// =========================

export interface StripeConfig {
  publishableKey: string;
  products: {
    [key: string]: {
      priceId: string;
      productId: string;
    };
  };
}

export const STRIPE_CONFIG: StripeConfig = {
  publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '',
  products: {
    creator: {
      priceId: 'price_1SAfyCRpPDjqChm1bjiivK16',
      productId: 'prod_T6tlpHdA9aMrgm'
    },
    pro: {
      priceId: 'price_1SAfyHRpPDjqChm1oYM7RnnU',
      productId: 'prod_T6tlJ9FvMmO3Rn'
    }
  }
};

// =========================
// CHECKOUT UTILITIES
// =========================

export interface CheckoutOptions {
  planId: string;
  successUrl?: string;
  cancelUrl?: string;
  customerEmail?: string;
}

export async function createCheckoutSession(options: CheckoutOptions): Promise<any> {
  const { paymentService } = await import('./api/payment');
  const { planId, successUrl, cancelUrl, customerEmail } = options;
  
  return paymentService.createCheckoutSession({
    planId,
    successUrl: successUrl || `${window.location.origin}/dashboard/settings?tab=subscription&success=true`,
    cancelUrl: cancelUrl || `${window.location.origin}/pricing`,
    customerEmail,
  });
}

// =========================
// PRICING VALIDATION
// =========================

export function validatePlanSelection(planId: string): boolean {
  return PRICING_PLANS.some(plan => plan.id === planId);
}

export function getPlanById(planId: string): PricingPlan | undefined {
  return PRICING_PLANS.find(plan => plan.id === planId);
}

// =========================
// PRICING ANALYTICS
// =========================

export function trackPlanView(planId: string): void {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', 'view_pricing_plan', {
      plan_id: planId,
      plan_name: getPlanById(planId)?.name
    });
  }
}

export function trackPlanClick(planId: string): void {
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', 'click_pricing_plan', {
      plan_id: planId,
      plan_name: getPlanById(planId)?.name
    });
  }
}

// =========================
// PRICING COMPARISON
// =========================

export interface PlanComparison {
  feature: string;
  free: boolean | string;
  creator: boolean | string;
  pro: boolean | string;
  business: boolean | string;
}

export const PLAN_COMPARISON: PlanComparison[] = [
  {
    feature: 'Monthly Credits Included',
    free: '60 Credits',
    creator: '1,500 Credits',
    pro: '5,000 Credits',
    business: '12,500 Credits'
  },
  {
    feature: 'Export Resolution',
    free: '720p Max (Watermarked)',
    creator: '1080p Full HD (No Watermark)',
    pro: '1080p Full HD',
    business: '1080p Full HD'
  },
  {
    feature: 'Project Cloud Storage',
    free: '1 GB (Max 5 drafts/7 days)',
    creator: '50 GB (Unlimited Drafts)',
    pro: '250 GB (Unlimited History)',
    business: '1 TB (Unlimited History)'
  },
  {
    feature: 'Video Script/Prompt LLM',
    free: 'Regular Model',
    creator: 'Regular Model',
    pro: 'Regular Model',
    business: 'Premium Model'
  },
  {
    feature: 'Music Analysis',
    free: 'Basic BPM & Key',
    creator: 'Full Advanced Analysis',
    pro: 'Full Advanced Analysis',
    business: 'Full Advanced Analysis'
  },
  {
    feature: 'Video Automation Access',
    free: false,
    creator: 'Scheduling Only',
    pro: 'Auto-Upload Included',
    business: 'Advanced Queue Management'
  },
  {
    feature: 'Automated Upload Limit',
    free: 'N/A',
    creator: '1 Upload/Day',
    pro: '4 Uploads/Day',
    business: '5 Uploads/Day'
  },
  {
    feature: 'Priority Processing Queue',
    free: false,
    creator: 'Standard',
    pro: 'Standard',
    business: 'Priority Queue Access'
  },
  {
    feature: 'Analytics & Stats',
    free: 'Basic Views Count',
    creator: 'Commercial Licensing',
    pro: 'Full Social Media Stats & Potential Gains',
    business: 'Full Social Media Stats & Dedicated Reporting'
  },
  {
    feature: 'Support',
    free: 'Community',
    creator: 'Email Support (Standard SLA)',
    pro: 'Priority Email Support',
    business: 'Dedicated Account Manager/SLA'
  }
];
