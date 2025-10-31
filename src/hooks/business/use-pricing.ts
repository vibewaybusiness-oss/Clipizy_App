import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { useToast } from '@/hooks/ui/use-toast';
import { 
  PRICING_PLANS, 
  createCheckoutSession, 
  trackPlanView, 
  trackPlanClick,
  type PricingPlan,
  type CheckoutOptions 
} from '@/lib/pricing-utils';

// =========================
// PRICING HOOK
// =========================

export interface UsePricingOptions {
  autoTrack?: boolean;
  onPlanSelect?: (plan: PricingPlan) => void;
  onCheckoutStart?: (plan: PricingPlan) => void;
  onCheckoutComplete?: (plan: PricingPlan) => void;
}

export function usePricing(options: UsePricingOptions = {}) {
  const { autoTrack = true, onPlanSelect, onCheckoutStart, onCheckoutComplete } = options;
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [selectedPlan, setSelectedPlan] = useState<PricingPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  // Memoized plans to prevent recreation
  const plans = useMemo(() => PRICING_PLANS, []);

  // Track plan views
  useEffect(() => {
    if (autoTrack && selectedPlan) {
      trackPlanView(selectedPlan.id);
    }
  }, [selectedPlan, autoTrack]);

  const selectPlan = useCallback((plan: PricingPlan) => {
    setSelectedPlan(plan);
    setCheckoutError(null);
    onPlanSelect?.(plan);
    
    if (autoTrack) {
      trackPlanClick(plan.id);
    }
  }, [onPlanSelect, autoTrack]);

  const startCheckout = useCallback(async (plan: PricingPlan, options?: Partial<CheckoutOptions>) => {
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please sign in to continue with checkout",
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    setCheckoutError(null);
    onCheckoutStart?.(plan);

    try {
      const checkoutOptions: CheckoutOptions = {
        planId: plan.id,
        customerEmail: user.email,
        ...options
      };

      const session = await createCheckoutSession(checkoutOptions);
      
      if (session.error) {
        throw new Error(session.error);
      }

      // Redirect to Stripe Checkout
      if (session.url) {
        window.location.href = session.url;
      } else {
        throw new Error('No checkout URL received');
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Checkout failed';
      setCheckoutError(errorMessage);
      
      toast({
        title: "Checkout Error",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  }, [user, toast, onCheckoutStart]);

  const clearSelection = useCallback(() => {
    setSelectedPlan(null);
    setCheckoutError(null);
  }, []);

  return {
    plans,
    selectedPlan,
    isLoading,
    checkoutError,
    selectPlan,
    startCheckout,
    clearSelection
  };
}

// =========================
// PRICING COMPARISON HOOK
// =========================

export function usePricingComparison() {
  const [selectedPlans, setSelectedPlans] = useState<Set<string>>(new Set(['free', 'creator']));

  const togglePlan = useCallback((planId: string) => {
    setSelectedPlans(prev => {
      const newSet = new Set(prev);
      if (newSet.has(planId)) {
        newSet.delete(planId);
      } else {
        newSet.add(planId);
      }
      return newSet;
    });
  }, []);

  const selectAllPlans = useCallback(() => {
    setSelectedPlans(new Set(PRICING_PLANS.map(plan => plan.id)));
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedPlans(new Set());
  }, []);

  const filteredPlans = useMemo(() => {
    return PRICING_PLANS.filter(plan => selectedPlans.has(plan.id));
  }, [selectedPlans]);

  return {
    selectedPlans,
    filteredPlans,
    togglePlan,
    selectAllPlans,
    clearSelection
  };
}

// =========================
// STRIPE INTEGRATION HOOK
// =========================

export function useStripeIntegration() {
  const [stripe, setStripe] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadStripe = async () => {
      try {
        // Dynamic import to avoid SSR issues
        const { loadStripe: loadStripeLib } = await import('@stripe/stripe-js');
        const stripeInstance = await loadStripeLib(
          process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || ''
        );
        
        if (!stripeInstance) {
          throw new Error('Failed to load Stripe');
        }
        
        setStripe(stripeInstance);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load Stripe');
      } finally {
        setIsLoading(false);
      }
    };

    loadStripe();
  }, []);

  const createCheckoutSession = useCallback(async (options: CheckoutOptions) => {
    if (!stripe) {
      throw new Error('Stripe not loaded');
    }

    // Call credits router directly for payment processing
    const response = await fetch('/api/credits/purchase', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('access_token') : ''}`,
      },
      body: JSON.stringify({
        amount_dollars: options.planId === 'free' ? 0 : parseFloat(options.planId.replace('plan_', ''))
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Payment processing failed');
    }

    const session = await response.json();

    if (session.error) {
      throw new Error(session.error);
    }

    return session;
  }, [stripe]);

  const redirectToCheckout = useCallback(async (sessionId: string) => {
    if (!stripe) {
      throw new Error('Stripe not loaded');
    }

    const { error } = await stripe.redirectToCheckout({ sessionId });
    
    if (error) {
      throw new Error(error.message);
    }
  }, [stripe]);

  return {
    stripe,
    isLoading,
    error,
    createCheckoutSession,
    redirectToCheckout
  };
}
