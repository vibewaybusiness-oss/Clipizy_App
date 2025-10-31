"use client";

import React, { useCallback, useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/ui/use-toast";
import { ArrowLeft, Loader2, Moon, Sun } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/contexts/auth-context";
import { useTheme } from "@/contexts/ThemeContext";
import { getBackendUrl } from "@/lib/config";

// Mock Stripe components for now - replace with actual Stripe imports when packages are installed
const loadStripe = (publishableKey: string) => {
  return Promise.resolve({
    embeddedCheckout: {
      create: async (options: any) => {
        // Mock implementation
        return {
          mount: (element: string) => {
            const el = document.getElementById(element);
            if (el) {
              el.innerHTML = `
                <div style="padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; background: #f9fafb;">
                  <h3 style="margin-bottom: 16px;">Stripe Checkout (Mock)</h3>
                  <p style="margin-bottom: 12px;">Plan: ${options.clientSecret ? 'Creator Plan' : 'Pro Plan'}</p>
                  <p style="margin-bottom: 12px;">Price: $${options.clientSecret ? '19.00' : '49.00'}/month</p>
                  <p style="margin-bottom: 16px;">This is a mock checkout form. In production, this would be the actual Stripe embedded checkout.</p>
                  <button onclick="window.location.href='/dashboard/settings?tab=subscription&success=true'" 
                          style="background: #3b82f6; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; width: 100%;">
                    Complete Mock Payment
                  </button>
                </div>
              `;
            }
          }
        };
      }
    }
  });
};

const EmbeddedCheckoutProvider = ({ children, stripe, options }: any) => {
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (options.fetchClientSecret) {
      options.fetchClientSecret().then((secret: string) => {
        setClientSecret(secret);
        setLoading(false);
      });
    }
  }, [options]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span className="ml-2">Loading checkout...</span>
      </div>
    );
  }

  return <div>{children}</div>;
};

const EmbeddedCheckout = ({ planId }: { planId: string }) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const { theme } = useTheme();

  const planDetails = {
    creator: {
      name: 'Creator Plan',
      price: '$19.00/month',
      credits: '2,000 credits'
    },
    pro: {
      name: 'Pro Plan',
      price: '$49.00/month',
      credits: '6,000 credits'
    }
  };

  const currentPlan = planDetails[planId as keyof typeof planDetails] || planDetails.creator;

  useEffect(() => {
    // Enhanced mock checkout form rendering with theme support
    const checkoutElement = document.getElementById('checkout-form');
    if (checkoutElement) {
      const isDark = theme === 'dark';
      const bgGradient = isDark 
        ? 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)' 
        : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
      const cardBg = isDark ? '#1f2937' : 'white';
      const textColor = isDark ? 'white' : '#1f2937';
      const labelColor = isDark ? '#d1d5db' : '#374151';
      const inputBg = isDark ? '#374151' : 'white';
      const inputBorder = isDark ? '#4b5563' : '#e5e7eb';
      const inputFocus = isDark ? '#60a5fa' : '#3b82f6';
      
      checkoutElement.innerHTML = `
        <div style="
          background: ${bgGradient};
          border-radius: 12px;
          padding: 20px;
          color: white;
          box-shadow: 0 10px 25px rgba(0,0,0,0.1);
          position: relative;
          overflow: hidden;
          height: 100%;
          display: flex;
          flex-direction: column;
        ">
          <!-- Background Pattern -->
          <div style="
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 15px 15px;
            animation: float 20s ease-in-out infinite;
          "></div>
          
          <div style="position: relative; z-index: 1; flex: 1; display: flex; flex-direction: column;">
            <!-- Header -->
            <div style="text-align: center; margin-bottom: 20px; flex-shrink: 0;">
              <div style="
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: rgba(255,255,255,0.2);
                padding: 6px 12px;
                border-radius: 16px;
                margin-bottom: 12px;
                backdrop-filter: blur(10px);
              ">
                <div style="width: 6px; height: 6px; background: #f59e0b; border-radius: 50%;"></div>
                <span style="font-size: 12px; font-weight: 500;">Demo Checkout</span>
              </div>
              <h3 style="margin: 0; font-size: 18px; font-weight: 700; margin-bottom: 6px;">
                ${currentPlan.name}
              </h3>
              <p style="margin: 0; font-size: 14px; opacity: 0.9;">
                ${currentPlan.credits} • ${currentPlan.price}
              </p>
            </div>

            <!-- Plan Summary -->
            <div style="
              background: rgba(255,255,255,0.15);
              border-radius: 8px;
              padding: 12px;
              margin-bottom: 16px;
              backdrop-filter: blur(10px);
              border: 1px solid rgba(255,255,255,0.2);
              flex-shrink: 0;
            ">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 600; font-size: 14px;">Plan</span>
                <span style="font-weight: 700; font-size: 16px;">${currentPlan.price}</span>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="opacity: 0.9; font-size: 14px;">Credits per month</span>
                <span style="font-weight: 600; font-size: 14px;">${currentPlan.credits}</span>
              </div>
            </div>

            <!-- Payment Form -->
            <div style="background: ${cardBg}; border-radius: 8px; padding: 16px; color: ${textColor}; flex: 1; display: flex; flex-direction: column;">
              <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 6px; font-weight: 600; color: ${labelColor}; font-size: 14px;">Email</label>
                <input type="email" placeholder="your@email.com" 
                       style="
                         width: 100%; 
                         padding: 10px 12px; 
                         border: 2px solid ${inputBorder}; 
                         border-radius: 6px; 
                         font-size: 14px;
                         background: ${inputBg};
                         color: ${textColor};
                         transition: border-color 0.2s;
                         box-sizing: border-box;
                       " 
                       onfocus="this.style.borderColor='${inputFocus}'"
                       onblur="this.style.borderColor='${inputBorder}'" />
              </div>

              <div style="margin-bottom: 12px;">
                <label style="display: block; margin-bottom: 6px; font-weight: 600; color: ${labelColor}; font-size: 14px;">Card Information</label>
                <input type="text" placeholder="1234 1234 1234 1234" 
                       style="
                         width: 100%; 
                         padding: 10px 12px; 
                         border: 2px solid ${inputBorder}; 
                         border-radius: 6px; 
                         font-size: 14px;
                         background: ${inputBg};
                         color: ${textColor};
                         margin-bottom: 8px;
                         transition: border-color 0.2s;
                         box-sizing: border-box;
                       " 
                       onfocus="this.style.borderColor='${inputFocus}'"
                       onblur="this.style.borderColor='${inputBorder}'" />
                <div style="display: flex; gap: 8px;">
                  <input type="text" placeholder="MM/YY" 
                         style="
                           flex: 1; 
                           padding: 10px 12px; 
                           border: 2px solid ${inputBorder}; 
                           border-radius: 6px; 
                           font-size: 14px;
                           background: ${inputBg};
                           color: ${textColor};
                           transition: border-color 0.2s;
                           box-sizing: border-box;
                         " 
                         onfocus="this.style.borderColor='${inputFocus}'"
                         onblur="this.style.borderColor='${inputBorder}'" />
                  <input type="text" placeholder="CVC" 
                         style="
                           flex: 1; 
                           padding: 10px 12px; 
                           border: 2px solid ${inputBorder}; 
                           border-radius: 6px; 
                           font-size: 14px;
                           background: ${inputBg};
                           color: ${textColor};
                           transition: border-color 0.2s;
                           box-sizing: border-box;
                         " 
                         onfocus="this.style.borderColor='${inputFocus}'"
                         onblur="this.style.borderColor='${inputBorder}'" />
                </div>
              </div>

              <div style="margin-bottom: 16px;">
                <label style="display: block; margin-bottom: 6px; font-weight: 600; color: ${labelColor}; font-size: 14px;">Cardholder Name</label>
                <input type="text" placeholder="Full name on card" 
                       style="
                         width: 100%; 
                         padding: 10px 12px; 
                         border: 2px solid ${inputBorder}; 
                         border-radius: 6px; 
                         font-size: 14px;
                         background: ${inputBg};
                         color: ${textColor};
                         transition: border-color 0.2s;
                         box-sizing: border-box;
                       " 
                       onfocus="this.style.borderColor='${inputFocus}'"
                       onblur="this.style.borderColor='${inputBorder}'" />
              </div>

              <button onclick="handleMockPayment()" 
                      style="
                        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
                        color: white; 
                        padding: 12px 20px; 
                        border: none; 
                        border-radius: 8px; 
                        cursor: pointer; 
                        width: 100%; 
                        font-weight: 600;
                        font-size: 14px;
                        transition: transform 0.2s, box-shadow 0.2s;
                        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
                        flex-shrink: 0;
                      " 
                      onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(22, 163, 74, 0.4)'"
                      onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(22, 163, 74, 0.3)'">
                Subscribe for ${currentPlan.price}
              </button>

              <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                margin-top: 12px;
                color: ${isDark ? '#9ca3af' : '#6b7280'};
                font-size: 12px;
                flex-shrink: 0;
              ">
                <div style="
                  width: 14px;
                  height: 14px;
                  background: linear-gradient(135deg, #635bff 0%, #00d4ff 100%);
                  border-radius: 2px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  color: white;
                  font-size: 8px;
                  font-weight: bold;
                ">S</div>
                <span>Secured by Stripe</span>
              </div>
            </div>
          </div>
        </div>

        <style>
          @keyframes float {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            33% { transform: translate(30px, -30px) rotate(120deg); }
            66% { transform: translate(-20px, 20px) rotate(240deg); }
          }
        </style>
      `;
    }
  }, [currentPlan, theme]);

  const handleMockPayment = () => {
    toast({
      title: "Payment Successful!",
      description: "Your subscription has been activated. Redirecting to success page...",
    });
    setTimeout(() => {
      window.location.href = `/dashboard/pricing/success?plan=${planId}&email=user@example.com`;
    }, 2000);
  };

  // Make handleMockPayment available globally for the mock form
  useEffect(() => {
    (window as any).handleMockPayment = handleMockPayment;
  }, []);

  return <div id="checkout-form" />;
};

const CheckoutForm = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const { theme, toggleTheme } = useTheme();
  const [planId, setPlanId] = useState<string>('creator');
  const [isLoading, setIsLoading] = useState(false);

  // Get plan from URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const plan = urlParams.get('plan');
    if (plan && (plan === 'creator' || plan === 'pro')) {
      setPlanId(plan);
    }
  }, []);

  // Mock Stripe promise
  const stripePromise = loadStripe("pk_test_51SAaoRRpPDjqChm1swlR6XPBgET4MWb6npOo8EghMHHVmSqkA02hxYtY1tv18PE3rk4EHodCXrYn7oofLFxzHxZi00yr53GoWp");

  const fetchClientSecret = useCallback(async () => {
    // Prevent multiple simultaneous calls
    if (isLoading) {
      return 'mock_client_secret';
    }
    
    setIsLoading(true);
    
    try {
      // For now, always return mock client secret to prevent API calls
      // This prevents the infinite loop and 401 errors
      return 'mock_client_secret';
    } finally {
      setIsLoading(false);
    }
    
    /* 
    // Real implementation - uncomment when authentication is working
    try {
      const authToken = localStorage.getItem('access_token');
      if (!authToken) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${getBackendUrl()}/api/credits/checkout`, {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          plan_id: planId,
          plan_type: 'subscription'
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to create checkout session`);
      }

      const data = await response.json();
      return data.client_secret || 'mock_client_secret';
    } catch (error) {
      console.error('Error creating checkout session:', error);
      toast({
        title: "Using Mock Checkout",
        description: "Authentication issue detected. Using mock checkout for demo.",
        variant: "default"
      });
      return 'mock_client_secret';
    }
    */
  }, [planId, toast, isLoading]);

  const options = { fetchClientSecret };

  return (
    <div className="h-screen overflow-hidden bg-background">
      <div className="h-full flex flex-col">
        {/* Compact Header */}
        <div className="flex-shrink-0 p-4">
          <div className="flex items-center justify-between mb-3">
            <Link href="/dashboard/pricing" className="inline-flex items-center text-sm group text-muted-foreground hover:text-foreground">
              <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
              Back to Pricing
            </Link>
            
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg transition-all text-muted-foreground hover:text-foreground bg-muted/50 hover:bg-muted border border-border"
            >
              {theme === 'dark' ? (
                <>
                  <Sun className="w-3 h-3" />
                  Light
                </>
              ) : (
                <>
                  <Moon className="w-3 h-3" />
                  Dark
                </>
              )}
            </button>
          </div>
          
          {/* Compact Demo Notice */}
          <div className="rounded-lg p-2 mb-3 bg-amber-50 dark:bg-amber-900/50 border border-amber-200 dark:border-amber-700">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-amber-400 rounded-full"></div>
              <span className="font-medium text-sm text-amber-800 dark:text-amber-200">Demo Mode</span>
            </div>
          </div>
          
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-1 text-foreground">
              Complete Your Subscription
            </h1>
            <p className="text-sm text-muted-foreground">
              Secure checkout powered by Stripe
            </p>
          </div>
        </div>

        {/* Main Content - Takes remaining height */}
        <div className="flex-1 px-4 pb-4">
          <div className="h-full grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Order Summary */}
          <div className="order-2 xl:order-1 flex flex-col">
            <Card className="border-0 shadow-xl backdrop-blur-sm flex-1 flex flex-col bg-card/90 border border-border/50">
              <CardHeader className="pb-3 flex-shrink-0">
                <CardTitle className="text-xl font-bold flex items-center gap-2 text-card-foreground">
                  <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-500 dark:from-blue-400 dark:to-purple-400 rounded-lg flex items-center justify-center shadow-sm">
                    <span className="text-white font-bold text-xs">✓</span>
                  </div>
                  Order Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col space-y-4">
                {/* Plan Details */}
                <div className="rounded-xl p-4 border flex-shrink-0 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/30 dark:to-purple-900/30 border-blue-100 dark:border-blue-800/50 dark:bg-gradient-to-r dark:from-slate-800/50 dark:to-slate-700/50">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-bold text-foreground">
                        {planId === 'creator' ? 'Creator Plan' : 'Pro Plan'}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {planId === 'creator' ? '2,000 credits per month' : '6,000 credits per month'}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-green-600 dark:text-green-400">
                        {planId === 'creator' ? '$19.00' : '$49.00'}
                      </div>
                      <div className="text-xs text-muted-foreground">per month</div>
                    </div>
                  </div>
                  
                  {/* Features */}
                  <div className="space-y-2">
                    <h4 className="font-semibold text-sm text-foreground">What's included:</h4>
                    <div className="space-y-1">
                      {planId === 'creator' ? (
                        <>
                          <div className="flex items-center gap-2 text-xs">
                            <div className="w-3 h-3 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center">
                              <div className="w-1.5 h-1.5 bg-green-500 dark:bg-green-400 rounded-full"></div>
                            </div>
                            <span className="text-foreground">High quality generation</span>
                          </div>
                          <div className="flex items-center gap-2 text-xs">
                            <div className="w-3 h-3 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center">
                              <div className="w-1.5 h-1.5 bg-green-500 dark:bg-green-400 rounded-full"></div>
                            </div>
                            <span className="text-foreground">Priority processing</span>
                          </div>
                          <div className="flex items-center gap-2 text-xs">
                            <div className="w-3 h-3 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center">
                              <div className="w-1.5 h-1.5 bg-green-500 dark:bg-green-400 rounded-full"></div>
                            </div>
                            <span className="text-foreground">No watermarks</span>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="flex items-center gap-2 text-xs">
                            <div className="w-3 h-3 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center">
                              <div className="w-1.5 h-1.5 bg-green-500 dark:bg-green-400 rounded-full"></div>
                            </div>
                            <span className="text-foreground">Ultra high quality</span>
                          </div>
                          <div className="flex items-center gap-2 text-xs">
                            <div className="w-3 h-3 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center">
                              <div className="w-1.5 h-1.5 bg-green-500 dark:bg-green-400 rounded-full"></div>
                            </div>
                            <span className="text-foreground">Highest priority processing</span>
                          </div>
                          <div className="flex items-center gap-2 text-xs">
                            <div className="w-3 h-3 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center">
                              <div className="w-1.5 h-1.5 bg-green-500 dark:bg-green-400 rounded-full"></div>
                            </div>
                            <span className="text-foreground">API access</span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Total */}
                <div className="rounded-xl p-4 flex-shrink-0 bg-muted/50 dark:bg-slate-800/60 border border-border/30 dark:border-slate-700/50">
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-semibold text-foreground">Total</span>
                    <div className="text-right">
                      <div className="text-xl font-bold text-foreground">
                        {planId === 'creator' ? '$19.00' : '$49.00'}
                      </div>
                      <div className="text-xs text-muted-foreground">per month</div>
                    </div>
                  </div>
                </div>

                {/* Security Badge */}
                <div className="flex items-center justify-center gap-2 text-xs rounded-lg p-2 flex-shrink-0 text-muted-foreground bg-muted/30 dark:bg-slate-800/40 border border-border/20 dark:border-slate-700/30">
                  <div className="w-4 h-4 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-green-500 dark:bg-green-400 rounded-full"></div>
                  </div>
                  <span className="text-foreground">256-bit SSL encryption</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Checkout Form */}
          <div className="order-1 xl:order-2 flex flex-col">
            {isLoading ? (
              <Card className="border-0 shadow-xl backdrop-blur-sm flex-1 flex flex-col bg-card/80">
                <CardContent className="flex-1 flex items-center justify-center p-6">
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                    <p className="text-sm text-muted-foreground">Loading checkout...</p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div id="checkout" className="flex-1">
                <EmbeddedCheckoutProvider
                  stripe={stripePromise}
                  options={options}
                >
                  <EmbeddedCheckout planId={planId} />
                </EmbeddedCheckoutProvider>
              </div>
            )}
          </div>
        </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutForm;
