"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: 'month' | 'year' | 'one-time';
  features: string[];
  popular?: boolean;
  credits?: number;
  maxVideos?: number;
  maxDuration?: number; // in minutes
}

export interface PricingConfig {
  credits_rate: number;
  music_generator: {
    "stable-audio": {
      price: number;
      description: string;
    };
    "clipizy-model": {
      price: number;
      description: string;
    };
  };
  image_generator: {
    "clipizy-model": {
      minute_rate: number;
      unit_rate: number;
      min: number;
      max: number | null;
      description: string;
    };
  };
  looped_animation_generator: {
    "clipizy-model": {
      minute_rate: number;
      unit_rate: number;
      min: number;
      max: number | null;
      description: string;
    };
  };
  recurring_scenes_generator: {
    "clipizy-model": {
      minute_rate: number;
      unit_rate: number;
      min: number;
      max: number | null;
      description: string;
    };
  };
  video_generator: {
    "clipizy-model": {
      "video-duration": number;
      minute_rate: number;
      min: number;
      max: number | null;
      description: string;
    };
  };
}

interface PricingContextType {
  plans: PricingPlan[];
  selectedPlan: PricingPlan | null;
  loading: boolean;
  pricing: PricingConfig;
  selectPlan: (plan: PricingPlan) => void;
  getPlanById: (id: string) => PricingPlan | undefined;
  calculatePrice: (plan: PricingPlan, isYearly?: boolean) => number;
}

const defaultPlans: PricingPlan[] = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    currency: 'USD',
    interval: 'month',
    features: [
      '3 music videos per month',
      'Up to 2 minutes duration',
      'Basic AI styles',
      'Standard quality export',
      'Community support'
    ],
    credits: 3,
    maxVideos: 3,
    maxDuration: 2,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 19,
    currency: 'USD',
    interval: 'month',
    features: [
      'Unlimited music videos',
      'Up to 10 minutes duration',
      'Premium AI styles',
      'HD quality export',
      'Priority support',
      'Custom branding',
      'Advanced editing tools'
    ],
    popular: true,
    credits: -1, // unlimited
    maxVideos: -1, // unlimited
    maxDuration: 10,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 99,
    currency: 'USD',
    interval: 'month',
    features: [
      'Everything in Pro',
      'Custom AI training',
      'API access',
      'White-label solution',
      'Dedicated support',
      'Custom integrations',
      'Team collaboration'
    ],
    credits: -1, // unlimited
    maxVideos: -1, // unlimited
    maxDuration: 30,
  },
];

const defaultPricingConfig: PricingConfig = {
  credits_rate: 20,
  music_generator: {
    "stable-audio": {
      price: 0.5,
      description: "Generate a music track based on the description."
    },
    "clipizy-model": {
      price: 1.0,
      description: "Generate a music track based on the description."
    }
  },
  image_generator: {
    "clipizy-model": {
      minute_rate: 0.10,
      unit_rate: 0.50,
      min: 3,
      max: null,
      description: "Generate an image based on the description."
    }
  },
  looped_animation_generator: {
    "clipizy-model": {
      minute_rate: 0.11,
      unit_rate: 1,
      min: 3,
      max: null,
      description: "Generate a looping animation based on the description."
    }
  },
  recurring_scenes_generator: {
    "clipizy-model": {
      minute_rate: 0.15,
      unit_rate: 1.5,
      min: 5,
      max: null,
      description: "Generate recurring scenes that repeat throughout the video."
    }
  },
  video_generator: {
    "clipizy-model": {
      "video-duration": 5,
      minute_rate: 10,
      min: 20,
      max: null,
      description: "Generate a video based on the description."
    }
  }
};

const PricingContext = createContext<PricingContextType | undefined>(undefined);

export function PricingProvider({ children }: { children: React.ReactNode }) {
  const [plans, setPlans] = useState<PricingPlan[]>(defaultPlans);
  const [selectedPlan, setSelectedPlan] = useState<PricingPlan | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load pricing plans from API or localStorage
    loadPricingPlans();
  }, []);

  const loadPricingPlans = async () => {
    setLoading(true);
    try {
      // TODO: Load from API
      // For now, use default plans
      setPlans(defaultPlans);

      // Load selected plan from localStorage
      if (typeof window !== 'undefined') {
        const storedPlan = localStorage.getItem('selectedPlan');
        if (storedPlan) {
          const plan = JSON.parse(storedPlan);
          setSelectedPlan(plan);
        }
      }
    } catch (error) {
      console.error('Error loading pricing plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectPlan = (plan: PricingPlan) => {
    setSelectedPlan(plan);

    // Store in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('selectedPlan', JSON.stringify(plan));
    }
  };

  const getPlanById = (id: string): PricingPlan | undefined => {
    return plans.find(plan => plan.id === id);
  };

  const calculatePrice = (plan: PricingPlan, isYearly: boolean = false): number => {
    if (plan.price === 0) return 0;

    if (isYearly && plan.interval === 'month') {
      // Apply yearly discount (2 months free)
      return plan.price * 10;
    }

    return plan.price;
  };

  const value: PricingContextType = {
    plans,
    selectedPlan,
    loading,
    pricing: defaultPricingConfig,
    selectPlan,
    getPlanById,
    calculatePrice,
  };

  return (
    <PricingContext.Provider value={value}>
      {children}
    </PricingContext.Provider>
  );
}

export function usePricing() {
  const context = useContext(PricingContext);
  if (context === undefined) {
    throw new Error('usePricing must be used within a PricingProvider');
  }
  return context;
}
