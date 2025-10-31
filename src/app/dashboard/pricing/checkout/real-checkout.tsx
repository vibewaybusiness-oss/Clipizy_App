"use client";

import React, { useCallback, useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/ui/use-toast";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/contexts/auth-context";
import { getBackendUrl } from "@/lib/config";

// This is the real Stripe embedded checkout implementation
// Uncomment and use this when @stripe/stripe-js and @stripe/react-stripe-js are installed

/*
import { loadStripe } from '@stripe/stripe-js';
import {
  EmbeddedCheckoutProvider,
  EmbeddedCheckout
} from '@stripe/react-stripe-js';

// Make sure to call `loadStripe` outside of a component's render to avoid
// recreating the `Stripe` object on every render.
const stripePromise = loadStripe("pk_test_51SAaoRRpPDjqChm1swlR6XPBgET4MWb6npOo8EghMHHVmSqkA02hxYtY1tv18PE3rk4EHodCXrYn7oofLFxzHxZi00yr53GoWp");

const CheckoutForm = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [planId, setPlanId] = useState<string>('creator');

  // Get plan from URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const plan = urlParams.get('plan');
    if (plan && (plan === 'creator' || plan === 'pro')) {
      setPlanId(plan);
    }
  }, []);

  const fetchClientSecret = useCallback(async () => {
    try {
      const response = await fetch(`${getBackendUrl()}/api/credits/checkout`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          plan_id: planId,
          plan_type: 'subscription'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const data = await response.json();
      return data.client_secret;
    } catch (error) {
      console.error('Error creating checkout session:', error);
      toast({
        title: "Error",
        description: "Failed to create checkout session",
        variant: "destructive"
      });
      throw error;
    }
  }, [planId, toast]);

  const options = { fetchClientSecret };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <Link href="/dashboard/pricing" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Pricing
        </Link>
        <h1 className="text-3xl font-bold">Complete Your Subscription</h1>
        <p className="text-muted-foreground mt-2">Secure checkout powered by Stripe</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        // Order Summary
        <Card>
          <CardHeader>
            <CardTitle>Order Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold">
                    {planId === 'creator' ? 'Creator Plan' : 'Pro Plan'}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {planId === 'creator' ? '2,000 credits per month' : '6,000 credits per month'}
                  </p>
                </div>
                <span className="font-semibold">
                  {planId === 'creator' ? '$19.00/month' : '$49.00/month'}
                </span>
              </div>
              <div className="border-t pt-4">
                <div className="flex justify-between items-center font-semibold">
                  <span>Total</span>
                  <span>{planId === 'creator' ? '$19.00/month' : '$49.00/month'}</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        // Checkout Form
        <Card>
          <CardHeader>
            <CardTitle>Payment Information</CardTitle>
            <CardDescription>Enter your payment details to complete your subscription</CardDescription>
          </CardHeader>
          <CardContent>
            <div id="checkout">
              <EmbeddedCheckoutProvider
                stripe={stripePromise}
                options={options}
              >
                <EmbeddedCheckout />
              </EmbeddedCheckoutProvider>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default CheckoutForm;
*/

// Temporary placeholder component
const RealCheckoutPlaceholder = () => {
  return (
    <div className="container mx-auto p-6 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Real Stripe Embedded Checkout</CardTitle>
          <CardDescription>This component is ready to use when Stripe packages are installed</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              To use the real Stripe embedded checkout:
            </p>
            <ol className="list-decimal list-inside space-y-2 text-sm">
              <li>Install the required packages: <code className="bg-muted px-2 py-1 rounded">npm install @stripe/stripe-js @stripe/react-stripe-js</code></li>
              <li>Uncomment the code in this file</li>
              <li>Replace the mock checkout with the real implementation</li>
            </ol>
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Note:</strong> The mock checkout is currently working and provides a good user experience. 
                The real Stripe embedded checkout will provide the actual payment processing.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RealCheckoutPlaceholder;
