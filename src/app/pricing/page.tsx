"use client";

import React, { useState, useCallback, useMemo, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/ui/use-toast";
import { useAuth } from "@/contexts/auth-context";
import { useTheme } from "@/contexts/ThemeContext";
import { usePricing } from "@/hooks/business/use-pricing";
import { PricingCard } from "@/components/pricing/pricing-card";
import { CheckoutModal } from "@/components/pricing/checkout-modal";
import { PRICING_PLANS, PLAN_COMPARISON } from "@/lib/pricing-utils";
import {
  Check,
  Star,
  Zap,
  Crown,
  ArrowRight,
  Coins,
  Video,
  Download,
  Users,
  Clock,
  Shield,
  Headphones,
  Sparkles,
  Loader2,
  Moon,
  Sun,
  ArrowLeft,
  Plus,
  TrendingUp,
  CheckCircle
} from "lucide-react";
import Link from "next/link";

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
      name: 'Tier 1: Creator Plan',
      price: '$25.00/month',
      credits: '1,500 credits'
    },
    pro: {
      name: 'Tier 2: Pro Plan',
      price: '$59.00/month',
      credits: '5,000 credits'
    },
    business: {
      name: 'Tier 3: Business Plan',
      price: '$119.00/month',
      credits: '12,500 credits'
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

const creditsPackages = [
  {
    id: "starter",
    name: "Starter Pack",
    credits: 1000,
    price: 10,
    bonus: 0,
    popular: false,
    description: "Perfect for trying out clipizy",
    features: ["1,000 credits", "Basic video generation", "Standard quality"],
    color: "border-gray-200"
  },
  {
    id: "creator",
    name: "Creator Pack",
    credits: 5000,
    price: 40,
    bonus: 1000,
    popular: true,
    description: "Most popular choice for creators",
    features: ["5,000 credits", "1,000 bonus credits", "High quality generation", "Priority processing"],
    color: "border-blue-200"
  },
  {
    id: "pro",
    name: "Pro Pack",
    credits: 15000,
    price: 100,
    bonus: 5000,
    popular: false,
    description: "For professional content creators",
    features: ["15,000 credits", "5,000 bonus credits", "Ultra high quality", "Priority processing", "Advanced features"],
    color: "border-purple-200"
  }
];

const subscriptionPlans = [
  {
    id: "free",
    name: "Free Tier",
    price: 0,
    period: "forever",
    description: "Perfect for trying out clipizy",
    features: [
      "60 Credits Included",
      "720p Max",
      "500 MB Cloud Storage",
      "Community Support"
    ],
    limitations: [
      "Limited storage",
      "Basic music analysis"
    ],
    color: "border-gray-200",
    buttonText: "Current Plan",
    buttonVariant: "outline" as const,
    popular: false
  },
  {
    id: "creator",
    name: "Tier 1: Creator",
    price: 25,
    period: "month",
    description: "Perfect for content creators and influencers",
    features: [
      "1,500 Credits Included",
      "1080p Full HD (No Watermark)",
      "10 GB Cloud Storage",
      "Video Automation Access (Scheduling Only)",
      "Commercial Licensing",
      "Email Support (Standard SLA)"
    ],
    limitations: [],
    color: "border-blue-200",
    buttonText: "Upgrade to Creator",
    buttonVariant: "default" as const,
    popular: true
  },
  {
    id: "pro",
    name: "Tier 2: Pro",
    price: 59,
    period: "month",
    description: "For professional creators and agencies",
    features: [
      "5,000 Credits Included",
      "1080p Full HD",
      "50 GB Cloud Storage",
      "Video Automation Access (Auto-Upload Included)",
      "1 Upload/Day Automated",
      "Email Support (Standard SLA)"
    ],
    limitations: [],
    color: "border-purple-200",
    buttonText: "Upgrade to Pro",
    buttonVariant: "default" as const,
    popular: false
  },
  {
    id: "business",
    name: "Tier 3: Business",
    price: 119,
    period: "month",
    description: "For large teams and organizations",
    features: [
      "12,500 Credits Included",
      "1080p Full HD",
      "150 GB Cloud Storage",
      "Premium Model LLM",
      "Video Automation Access (Advanced Queue Management)",
      "5 Uploads/Day Automated",
      "Priority Queue Access",
      "Priority Email Support"
    ],
    limitations: [],
    color: "border-amber-200",
    buttonText: "Upgrade to Business",
    buttonVariant: "default" as const,
    popular: false
  }
];


const features = [
  {
    category: "Credits & Pricing",
    items: [
      { name: "Monthly Credits Included", free: "60 Credits", creator: "1,500 Credits", pro: "5,000 Credits", business: "12,500 Credits" },
      { name: "Additional Credit Purchase", free: true, creator: true, pro: true, business: true },
      { name: "Annual Discount", free: "N/A", creator: "12% Off", pro: "12% Off", business: "12% Off" }
    ]
  },
  {
    category: "Export & Quality",
    items: [
      { name: "Export Resolution", free: "720p Max", creator: "1080p Full HD (No Watermark)", pro: "1080p Full HD", business: "1080p Full HD" },
      { name: "Watermark", free: false, creator: true, pro: true, business: true },
      { name: "Project Cloud Storage", free: "500 MB", creator: "10 GB", pro: "50 GB", business: "150 GB" }
    ]
  },
  {
    category: "AI & Analysis",
    items: [
      { name: "Video Script/Prompt LLM", free: "Regular Model", creator: "Regular Model", pro: "Regular Model", business: "Premium Model" },
      { name: "Music Analysis", free: "Basic BPM & Key", creator: "Full Advanced Analysis", pro: "Full Advanced Analysis", business: "Full Advanced Analysis" }
    ]
  },
  {
    category: "Automation & Processing",
    items: [
      { name: "Video Automation Access", free: false, creator: "Scheduling Only", pro: "Auto-Upload Included", business: "Advanced Queue Management" },
      { name: "Generation Automation", free: "N/A", creator: "N/A", pro: "1 Upload/Day", business: "5 Uploads/Day" },
      { name: "Priority Processing Queue", free: false, creator: false, pro: false, business: "Priority Queue Access" }
    ]
  },
  {
    category: "Analytics & Support",
    items: [
      { name: "Analytics & Stats", free: "Basic Views Count", creator: "Commercial Licensing", pro: "Commercial Licensing", business: "Commercial Licensing" },
      { name: "Support", free: "Community", creator: "Email Support (Standard SLA)", pro: "Email Support (Standard SLA)", business: "Priority Email Support" }
    ]
  }
];

export default function PricingPage() {
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "yearly">("monthly");
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [showCheckout, setShowCheckout] = useState(false);
  const [checkoutPlan, setCheckoutPlan] = useState<string>('creator');
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const { toast } = useToast();

  const handlePlanSelect = (planId: string) => {
    if (planId === 'creator' || planId === 'pro' || planId === 'business') {
      setCheckoutPlan(planId);
      setShowCheckout(true);
    } else {
      setSelectedPlan(planId);
      console.log("Selected plan:", planId);
    }
  };

  const handleCreditsPurchase = async (packageId: string) => {
    const pkg = creditsPackages.find(p => p.id === packageId);
    if (!pkg) return;

    try {
      setIsProcessing(true);
      setSelectedPackage(packageId);

      // Mock purchase - in real app, this would create Stripe checkout
      toast({
        title: "Purchase Initiated",
        description: `Starting purchase of ${pkg.name} for $${pkg.price}`,
      });

      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      toast({
        title: "Purchase Successful!",
        description: `You've received ${(pkg.credits + pkg.bonus).toLocaleString()} credits`,
      });

    } catch (error) {
      console.error('Purchase error:', error);
      toast({
        title: "Purchase Failed",
        description: "Failed to process purchase. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
      setSelectedPackage(null);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* HERO SECTION */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 animated-bg"></div>
        <div className="absolute inset-0 hero-gradient"></div>
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-accent/10"></div>
        <video
          className="absolute inset-0 w-full h-full object-cover opacity-15"
          autoPlay
          loop
          muted
          onLoadedMetadata={(e) => {
            e.currentTarget.currentTime = 9;
          }}
          onError={(e) => {
            e.currentTarget.style.display = 'none';
          }}
        >
          <source src="/media/hero_section.mp4" type="video/mp4" />
        </video>

        <div className="relative container-custom">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
              Choose Your
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600">
                {" "}Creative
              </span>
              <br />
              Journey
            </h1>

            {/* BILLING TOGGLE */}
            <div className="flex items-center justify-center space-x-4 mb-12">
              <span className={`text-sm font-medium ${billingPeriod === "monthly" ? "text-foreground" : "text-muted-foreground"}`}>
                Monthly
              </span>
                <button
                  onClick={() => setBillingPeriod(billingPeriod === "monthly" ? "yearly" : "monthly")}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                    billingPeriod === "yearly" ? "bg-green-500" : "bg-gray-200"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      billingPeriod === "yearly" ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              <span className={`text-sm font-medium ${billingPeriod === "yearly" ? "text-foreground" : "text-muted-foreground"}`}>
                Yearly
                <Badge className="ml-2 bg-green-500 text-white">Save 20%</Badge>
              </span>
            </div>
          </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {subscriptionPlans.map((plan) => (
            <Card
              key={plan.id}
              className={`relative ${plan.color} ${plan.popular ? 'ring-2 ring-primary scale-105' : ''} transition-all duration-200 hover:shadow-lg`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-primary text-primary-foreground px-4 py-1">
                    <Star className="w-3 h-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center pb-4">
                <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                <CardDescription className="text-sm">{plan.description}</CardDescription>
                  <div className="mt-4">
                    <div className="text-4xl font-bold">
                      {typeof plan.price === "number" ? (
                        billingPeriod === "yearly" ? (
                          <>
                            ${Math.round(plan.price * 0.8)}
                            <span className="text-lg text-muted-foreground line-through ml-2">
                              ${plan.price}
                            </span>
                          </>
                        ) : (
                          `$${plan.price}`
                        )
                      ) : (
                        plan.price
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {typeof plan.price === "number" ? (
                        billingPeriod === "yearly" ? "per month" : `per ${plan.period}`
                      ) : (
                        plan.period
                      )}
                    </div>
                  </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <ul className="space-y-3">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                  {plan.id === "free" && (
                    <li className="flex items-start space-x-2">
                      <span className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0 flex items-center justify-center">✕</span>
                      <span className="text-sm text-muted-foreground">Watermark on exports</span>
                    </li>
                  )}
                </ul>

                {plan.limitations.length > 0 && (
                  <div className="pt-4 border-t">
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Limitations:</h4>
                    <ul className="space-y-1">
                      {plan.limitations.map((limitation, index) => (
                        <li key={index} className="text-xs text-muted-foreground">
                          • {limitation}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <Button
                  className="w-full mt-6"
                  variant={plan.buttonVariant}
                  onClick={() => handlePlanSelect(plan.id)}
                >
                  {plan.buttonText}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
        </div>
      </section>

      {/* CREDITS PACKAGES */}
      <div className="bg-muted/50 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Or Buy Credits as You Go
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Need more credits? Purchase them individually without a subscription.
              Perfect for occasional users or when you need extra credits.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {creditsPackages.map((pkg) => (
                <Card
                  key={pkg.id}
                  className={`relative cursor-pointer transition-all duration-200 hover:shadow-lg ${
                    pkg.popular ? 'ring-2 ring-primary' : ''
                  } ${pkg.color}`}
                >
                  {pkg.popular && (
                    <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                      <Badge className="bg-primary text-primary-foreground">
                        <Star className="w-3 h-3 mr-1" />
                        Most Popular
                      </Badge>
                    </div>
                  )}

                  <CardContent className="p-6 text-center">
                    <h3 className="text-xl font-semibold mb-2">{pkg.name}</h3>
                    <p className="text-muted-foreground mb-4">{pkg.description}</p>

                    <div className="mb-4">
                      <div className="text-3xl font-bold">${pkg.price}</div>
                      <div className="text-sm text-muted-foreground">
                        {(pkg.credits + pkg.bonus).toLocaleString()} credits
                        {pkg.bonus > 0 && (
                          <span className="text-green-500 ml-1">
                            (+{pkg.bonus.toLocaleString()} bonus)
                          </span>
                        )}
                      </div>
                    </div>

                    <ul className="space-y-2 mb-6 text-sm">
                      {pkg.features.map((feature, index) => (
                        <li key={index} className="flex items-center justify-center">
                          <Check className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>

                    <Button
                      size="lg"
                      className="w-full"
                      onClick={() => handleCreditsPurchase(pkg.id)}
                      disabled={isProcessing && selectedPackage === pkg.id}
                    >
                      {isProcessing && selectedPackage === pkg.id ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Plus className="w-4 h-4 mr-2" />
                      )}
                      Purchase
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* STRIPE SECURITY BADGE */}
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground bg-muted/30 rounded-lg p-4 border border-border/20">
              <div className="w-4 h-4 bg-green-100 dark:bg-green-900/50 rounded-full flex items-center justify-center">
                <div className="w-1.5 h-1.5 bg-green-500 dark:bg-green-400 rounded-full"></div>
              </div>
              <span className="text-foreground">Secured by Stripe • SSL Encrypted</span>
            </div>
          </div>
        </div>
      </div>

      {/* FEATURE COMPARISON */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-foreground mb-4">
            Feature Comparison
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Compare all features across our different plans to find the perfect fit for your needs.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b">
                <th className="text-left p-4 font-medium">Features</th>
                <th className="text-center p-4 font-medium">Free Tier</th>
                <th className="text-center p-4 font-medium">Tier 1: Creator</th>
                <th className="text-center p-4 font-medium">Tier 2: Pro</th>
                <th className="text-center p-4 font-medium">Tier 3: Business</th>
              </tr>
            </thead>
            <tbody>
              {features.map((category, categoryIndex) => (
                <React.Fragment key={categoryIndex}>
                  <tr className="bg-muted/50">
                    <td colSpan={5} className="p-4 font-medium text-foreground">
                      {category.category}
                    </td>
                  </tr>
                  {category.items.map((item, itemIndex) => (
                    <tr key={itemIndex} className="border-b hover:bg-muted/25">
                      <td className="p-4 text-sm">{item.name}</td>
                      <td className="p-4 text-center">
                        {typeof item.free === 'boolean' ? (
                          item.free ? (
                            <Check className="w-4 h-4 text-green-500 mx-auto" />
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )
                        ) : (
                          <span className="text-sm font-medium">{item.free}</span>
                        )}
                      </td>
                      <td className="p-4 text-center">
                        {typeof item.creator === 'boolean' ? (
                          item.creator ? (
                            <Check className="w-4 h-4 text-green-500 mx-auto" />
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )
                        ) : (
                          <span className="text-sm font-medium">{item.creator}</span>
                        )}
                      </td>
                      <td className="p-4 text-center">
                        {typeof item.pro === 'boolean' ? (
                          item.pro ? (
                            <Check className="w-4 h-4 text-green-500 mx-auto" />
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )
                        ) : (
                          <span className="text-sm font-medium">{item.pro}</span>
                        )}
                      </td>
                      <td className="p-4 text-center">
                        {typeof item.business === 'boolean' ? (
                          item.business ? (
                            <Check className="w-4 h-4 text-green-500 mx-auto" />
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )
                        ) : (
                          <span className="text-sm font-medium">{item.business}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>


      {/* CTA SECTION */}
      <div className="relative overflow-hidden">
        {/* Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-purple-500/5 to-accent/5"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-background"></div>
        
        {/* Animated Background Elements */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-primary/10 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-purple-500/10 rounded-full blur-xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-accent/10 rounded-full blur-lg animate-pulse delay-500"></div>
        
        <div className="relative container mx-auto px-4 py-16 sm:py-20">
          <div className="text-center max-w-4xl mx-auto">
            {/* Main Heading */}
            <div className="mb-6">
              <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight">
                Ready to Start
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600 block sm:inline">
                  {" "}Creating?
                </span>
              </h2>
            </div>
            
            {/* Description */}
            <p className="text-lg sm:text-xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed">
              Join thousands of creators who are already using clipizy to create
              <span className="text-foreground font-semibold"> amazing AI-generated music videos</span>.
            </p>
            
            {/* Stats or Social Proof */}
            <div className="flex flex-wrap justify-center items-center gap-8 mb-12 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>10,000+ Active Creators</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-300"></div>
                <span>1M+ Videos Generated</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse delay-700"></div>
                <span>4.9/5 Rating</span>
              </div>
            </div>
            
            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center">
              <Button 
                size="lg" 
                className="h-14 px-8 text-lg font-semibold bg-gradient-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105" 
                asChild
              >
                <Link href="/pricing">
                  <Coins className="w-6 h-6 mr-3" />
                  Buy Credits Now
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Link>
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="h-14 px-8 text-lg font-semibold border-2 border-primary/20 hover:border-primary/40 hover:bg-primary/5 transition-all duration-300 transform hover:scale-105" 
                asChild
              >
                <Link href="/dashboard">
                  <Video className="w-6 h-6 mr-3" />
                  Start Free Trial
                  <Sparkles className="w-5 h-5 ml-2" />
                </Link>
              </Button>
            </div>
            
            {/* Trust Indicators */}
            <div className="mt-12 pt-8 border-t border-border/20">
              <p className="text-sm text-muted-foreground mb-4">Trusted by creators worldwide</p>
              <div className="flex flex-wrap justify-center items-center gap-6 opacity-60">
                <div className="flex items-center gap-2 text-xs">
                  <Shield className="w-4 h-4" />
                  <span>SSL Secured</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <CheckCircle className="w-4 h-4" />
                  <span>No Setup Required</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <Clock className="w-4 h-4" />
                  <span>Instant Results</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
