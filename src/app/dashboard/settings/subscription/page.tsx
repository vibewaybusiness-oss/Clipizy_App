"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  CreditCard,
  CheckCircle,
  XCircle,
  Star,
  Zap,
  Crown,
  ArrowLeft,
  Settings
} from "lucide-react";
import { useAuth } from "@/contexts/auth-context";
import Link from "next/link";
import { useToast } from "@/hooks/ui/use-toast";
import { getBackendUrl } from "@/lib/config";
import { ClipizyLoading } from "@/components/ui/clipizy-loading";

interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  interval: string;
  features: string[];
  credits: number;
  popular?: boolean;
  current?: boolean;
}

export default function SubscriptionPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [currentPlan, setCurrentPlan] = useState<string>("free");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    setIsLoading(true);
    try {
      // Load available plans
      const plansResponse = await fetch('/api/subscription/plans');
      if (plansResponse.ok) {
        const plansData = await plansResponse.json();
        setPlans(plansData);
      }

      // Load current subscription
      const subscriptionResponse = await fetch('/api/subscription/current');
      if (subscriptionResponse.ok) {
        const subscriptionData = await subscriptionResponse.json();
        setCurrentPlan(subscriptionData.plan_id || "free");
      }
    } catch (error) {
      console.error('Error loading subscription data:', error);
      toast({
        title: "Error",
        description: "Failed to load subscription information",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubscribe = async (planId: string) => {
    try {
      // Get the Stripe price ID for the selected plan
      const response = await fetch(`${getBackendUrl()}/api/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ 
          plan_id: planId,
          plan_type: 'subscription'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.checkout_url) {
          // Redirect to Stripe checkout
          window.location.href = data.checkout_url;
        } else {
          throw new Error('No checkout URL received');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to create checkout session');
      }
    } catch (error) {
      console.error('Error subscribing to plan:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to subscribe to plan",
        variant: "destructive"
      });
    }
  };

  const handleCancelSubscription = async () => {
    try {
      const response = await fetch('/api/subscription/cancel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: "Subscription cancelled successfully"
        });
        loadSubscriptionData();
      } else {
        throw new Error('Failed to cancel subscription');
      }
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      toast({
        title: "Error",
        description: "Failed to cancel subscription",
        variant: "destructive"
      });
    }
  };

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case 'free':
        return <Star className="w-5 h-5" />;
      case 'pro':
        return <Zap className="w-5 h-5" />;
      case 'premium':
        return <Crown className="w-5 h-5" />;
      default:
        return <CreditCard className="w-5 h-5" />;
    }
  };

  const getPlanColor = (planId: string) => {
    switch (planId) {
      case 'free':
        return 'text-gray-600';
      case 'pro':
        return 'text-blue-600';
      case 'premium':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 space-y-6">
        <div className="flex items-center justify-center h-64">
          <ClipizyLoading message="Loading subscription..." size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground mb-1">Subscription Plans</h1>
          <p className="text-muted-foreground">
            Choose the perfect plan for your video creation needs
          </p>
        </div>
        <Button variant="outline" asChild>
          <Link href="/dashboard/settings">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Settings
          </Link>
        </Button>
      </div>

      {/* CURRENT SUBSCRIPTION STATUS */}
      <Card className="bg-card border border-border">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="w-5 h-5" />
            <span>Current Subscription</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {getPlanIcon(currentPlan)}
              <div>
                <div className="font-medium capitalize">{currentPlan} Plan</div>
                <div className="text-sm text-muted-foreground">
                  {currentPlan === 'free' ? 'Free tier with limited features' : 'Active subscription'}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant={currentPlan === 'free' ? 'secondary' : 'default'}>
                {currentPlan === 'free' ? 'Free' : 'Active'}
              </Badge>
              {currentPlan !== 'free' && (
                <Button variant="outline" size="sm" onClick={handleCancelSubscription}>
                  Cancel
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* SUBSCRIPTION PLANS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {plans.filter(plan => {
          // Show only current plan and higher tier plans
          const planOrder = ['free', 'pro', 'premium', 'enterprise'];
          const currentIndex = planOrder.indexOf(currentPlan);
          const planIndex = planOrder.indexOf(plan.id);
          return planIndex >= currentIndex;
        }).map((plan) => (
          <Card 
            key={plan.id} 
            className={`bg-card border ${
              plan.popular ? 'border-primary ring-2 ring-primary/20' : 'border-border'
            } ${plan.current ? 'bg-primary/5' : ''}`}
          >
            {plan.popular && (
              <div className="bg-primary text-primary-foreground text-center py-2 text-sm font-medium">
                Most Popular
              </div>
            )}
            <CardHeader className="text-center">
              <div className={`mx-auto mb-2 ${getPlanColor(plan.id)}`}>
                {getPlanIcon(plan.id)}
              </div>
              <CardTitle className="text-xl">{plan.name}</CardTitle>
              <CardDescription>{plan.description}</CardDescription>
              <div className="mt-4">
                <span className="text-3xl font-bold">{plan.price === 0 ? 'Free' : `$${plan.price}`}</span>
                {plan.price > 0 && (
                  <span className="text-muted-foreground">/{plan.interval}</span>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-sm">{plan.credits} credits included</span>
                </div>
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-sm">{feature}</span>
                  </div>
                ))}
              </div>

              <Separator />

              <Button 
                className="w-full" 
                variant={plan.current ? "secondary" : plan.popular ? "default" : "outline"}
                disabled={plan.current}
                onClick={() => handleSubscribe(plan.id)}
              >
                {plan.current ? (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Current Plan
                  </>
                ) : plan.price === 0 ? (
                  'Get Started'
                ) : (
                  'Subscribe'
                )}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* BILLING INFORMATION */}
      <Card className="bg-card border border-border">
        <CardHeader>
          <CardTitle>Billing Information</CardTitle>
          <CardDescription>
            Manage your payment methods and billing details
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium">Payment Method</div>
              <div className="text-sm text-muted-foreground">
                No payment method on file
              </div>
            </div>
            <Button variant="outline" asChild>
              <Link href="/dashboard/settings/billing">
                <CreditCard className="w-4 h-4 mr-2" />
                Manage Billing
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
