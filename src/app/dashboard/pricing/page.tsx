"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import {
  Check,
  Star,
  Zap,
  Crown,
  ArrowRight,
  Video,
  Download,
  Users,
  Clock,
  Shield,
  Headphones,
  Sparkles,
  ArrowLeft,
  X
} from "lucide-react";
import Link from "next/link";
import { useToast } from "@/hooks/ui/use-toast";
import { getBackendUrl } from "@/lib/config";

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
      { name: "Analytics & Stats", free: "Basic Views Count", creator: "Commercial Licensing & Basic Views", pro: "Commercial Licensing & Basic Views", business: "Commercial Licensing & Basic Views" },
      { name: "Support", free: "Community", creator: "Email Support (Standard SLA)", pro: "Email Support (Standard SLA)", business: "Priority Email Support" }
    ]
  }
];

export default function DashboardPricingPage() {
  const { toast } = useToast();
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "yearly">("monthly");
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handlePlanSelect = async (planId: string) => {
    setSelectedPlan(planId);
    
    if (planId === "free") {
      // Free plan - no payment needed
      toast({
        title: "Free Plan Selected",
        description: "You're already on the free plan!",
      });
      return;
    }
    
    if (planId === "creator" || planId === "pro" || planId === "business") {
      // Redirect to embedded checkout
      setIsLoading(true);
      try {
        toast({
          title: "Redirecting to Checkout",
          description: `Redirecting to ${planId} plan checkout...`,
        });
        
        // Redirect to embedded checkout page
        window.location.href = `/dashboard/pricing/checkout?plan=${planId}`;
        
      } catch (error) {
        console.error('Error redirecting to checkout:', error);
        toast({
          title: "Error",
          description: error instanceof Error ? error.message : "Failed to redirect to checkout",
          variant: "destructive"
        });
      } finally {
        setIsLoading(false);
      }
    }
  };


  return (
    <div className="min-h-screen bg-background">
      {/* HEADER */}
      <div className="bg-gradient-to-br from-primary/10 via-background to-background">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard/settings?tab=subscription">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Settings
              </Link>
            </Button>
          </div>
          
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-3">
              Choose Your
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600">
                {" "}Creative
              </span>
              <br />
              Journey
            </h1>
            <p className="text-base text-muted-foreground mb-4 max-w-2xl mx-auto">
              From free exploration to professional creation, find the perfect plan
              for your video generation needs.
            </p>

            {/* BILLING TOGGLE */}
            <div className="flex items-center justify-center space-x-4 mb-6">
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
        </div>
      </div>

      {/* SUBSCRIPTION PLANS */}
      <div className="container mx-auto px-4 py-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 h-[calc(100vh-300px)] max-h-[600px]">
          {subscriptionPlans.map((plan) => (
            <Card
              key={plan.id}
              className={`relative ${plan.color} ${plan.popular ? 'ring-2 ring-primary scale-105' : ''} transition-all duration-200 hover:shadow-lg flex flex-col`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-primary text-primary-foreground px-4 py-1">
                    <Star className="w-3 h-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center pb-3">
                <CardTitle className="text-xl font-bold">{plan.name}</CardTitle>
                <CardDescription className="text-xs">{plan.description}</CardDescription>
                <div className="mt-3">
                  <div className="text-3xl font-bold">
                    {typeof plan.price === "number" ? (
                      billingPeriod === "yearly" ? (
                        <>
                          ${Math.round(plan.price * 0.8)}
                          <span className="text-sm text-muted-foreground line-through ml-1">
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
                  <div className="text-xs text-muted-foreground">
                    {typeof plan.price === "number" ? (
                      billingPeriod === "yearly" ? "per month" : `per ${plan.period}`
                    ) : (
                      plan.period
                    )}
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-3 flex-1 flex flex-col">
                <div className="flex-1">
                  <ul className="space-y-2">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <Check className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-xs">{feature}</span>
                      </li>
                    ))}
                    {plan.id === "free" && (
                      <li className="flex items-start space-x-2">
                        <X className="w-3 h-3 text-red-500 mt-0.5 flex-shrink-0" />
                        <span className="text-xs text-muted-foreground">Watermark on exports</span>
                      </li>
                    )}
                  </ul>

                  {plan.limitations.length > 0 && (
                    <div className="pt-3 border-t mt-3">
                      <h4 className="text-xs font-medium text-muted-foreground mb-1">Limitations:</h4>
                      <ul className="space-y-1">
                        {plan.limitations.map((limitation, index) => (
                          <li key={index} className="text-xs text-muted-foreground">
                            • {limitation}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                <Button
                  className="w-full mt-4"
                  size="sm"
                  variant={plan.buttonVariant}
                  disabled={isLoading || (plan.id === "free" && plan.buttonText === "Current Plan")}
                  onClick={() => handlePlanSelect(plan.id)}
                >
                  {isLoading && selectedPlan === plan.id ? (
                    <>
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-current mr-2"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      {plan.buttonText}
                      <ArrowRight className="w-3 h-3 ml-2" />
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* SPACER TO PUSH FEATURE COMPARISON LOWER */}
      <div className="h-16"></div>

      {/* FEATURE COMPARISON */}
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-foreground mb-2">
            Feature Comparison
          </h2>
          <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
            Compare all features across our different plans to find the perfect fit for your needs.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2 font-medium text-sm">Features</th>
                <th className="text-center p-2 font-medium text-sm">Free Tier</th>
                <th className="text-center p-2 font-medium text-sm">Tier 1: Creator</th>
                <th className="text-center p-2 font-medium text-sm">Tier 2: Pro</th>
                <th className="text-center p-2 font-medium text-sm">Tier 3: Business</th>
              </tr>
            </thead>
            <tbody>
              {features.map((category, categoryIndex) => (
                <React.Fragment key={categoryIndex}>
                  <tr className="bg-muted/50">
                    <td colSpan={5} className="p-2 font-medium text-foreground text-sm">
                      {category.category}
                    </td>
                  </tr>
                  {category.items.map((item, itemIndex) => (
                    <tr key={itemIndex} className="border-b hover:bg-muted/25">
                      <td className="p-2 text-xs">{item.name}</td>
                      <td className="p-2 text-center">
                        {typeof item.free === 'boolean' ? (
                          item.free ? (
                            <Check className="w-3 h-3 text-green-500 mx-auto" />
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )
                        ) : (
                          <span className="text-xs font-medium">{item.free}</span>
                        )}
                      </td>
                      <td className="p-2 text-center">
                        {typeof item.creator === 'boolean' ? (
                          item.creator ? (
                            <Check className="w-3 h-3 text-green-500 mx-auto" />
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )
                        ) : (
                          <span className="text-xs font-medium">{item.creator}</span>
                        )}
                      </td>
                      <td className="p-2 text-center">
                        {typeof item.pro === 'boolean' ? (
                          item.pro ? (
                            <Check className="w-3 h-3 text-green-500 mx-auto" />
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )
                        ) : (
                          <span className="text-xs font-medium">{item.pro}</span>
                        )}
                      </td>
                      <td className="p-2 text-center">
                        {typeof item.business === 'boolean' ? (
                          item.business ? (
                            <Check className="w-3 h-3 text-green-500 mx-auto" />
                          ) : (
                            <span className="text-muted-foreground">—</span>
                          )
                        ) : (
                          <span className="text-xs font-medium">{item.business}</span>
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
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-foreground mb-2">
            Ready to Start Creating?
          </h2>
          <p className="text-sm text-muted-foreground mb-4 max-w-2xl mx-auto">
            Join thousands of creators who are already using clipizy to create
            amazing AI-generated music videos.
          </p>
          <div className="flex justify-center">
            <Button variant="outline" asChild>
              <Link href="/dashboard/create">
                <Video className="w-4 h-4 mr-2" />
                Start Creating
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
