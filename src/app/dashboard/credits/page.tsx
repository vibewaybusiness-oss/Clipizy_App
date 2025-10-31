"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Check,
  Coins,
  ArrowRight,
  ArrowLeft,
  Zap,
  Star,
  Crown,
  Sparkles,
  Video,
  Download,
  Users,
  Clock,
  Shield,
  Headphones
} from "lucide-react";
import Link from "next/link";

const creditsPackages = [
  {
    name: "Starter Pack",
    credits: 1000,
    price: 10,
    bonus: 0,
    description: "Perfect for trying out clipizy",
    popular: false,
    icon: Coins,
    color: "border-gray-200"
  },
  {
    name: "Creator Pack",
    credits: 5000,
    price: 40,
    bonus: 1000,
    description: "Most popular choice for creators",
    popular: true,
    icon: Zap,
    color: "border-blue-200"
  },
  {
    name: "Pro Pack",
    credits: 15000,
    price: 100,
    bonus: 5000,
    description: "For professional content creators",
    popular: false,
    icon: Crown,
    color: "border-purple-200"
  },
  {
    name: "Enterprise Pack",
    credits: 50000,
    price: 300,
    bonus: 20000,
    description: "For teams and agencies",
    popular: false,
    icon: Sparkles,
    color: "border-gold-200"
  }
];

const features = [
  {
    category: "Video Generation",
    items: [
      { name: "AI-powered video creation", starter: true, creator: true, pro: true, enterprise: true },
      { name: "Multiple visual styles", starter: true, creator: true, pro: true, enterprise: true },
      { name: "Custom music integration", starter: true, creator: true, pro: true, enterprise: true },
      { name: "4K video quality", starter: false, creator: false, pro: true, enterprise: true },
      { name: "Custom video styles", starter: false, creator: false, pro: true, enterprise: true }
    ]
  },
  {
    category: "Processing & Performance",
    items: [
      { name: "Standard processing", starter: true, creator: true, pro: true, enterprise: true },
      { name: "Priority processing", starter: false, creator: true, pro: true, enterprise: true },
      { name: "Instant processing", starter: false, creator: false, pro: false, enterprise: true },
      { name: "Batch processing", starter: false, creator: false, pro: true, enterprise: true }
    ]
  },
  {
    category: "Support & Resources",
    items: [
      { name: "Community support", starter: true, creator: true, pro: true, enterprise: true },
      { name: "Email support", starter: false, creator: true, pro: true, enterprise: true },
      { name: "Priority support", starter: false, creator: false, pro: true, enterprise: true },
      { name: "Dedicated support", starter: false, creator: false, pro: false, enterprise: true }
    ]
  }
];

export default function CreditsPage() {
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "yearly">("monthly");
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);

  const handlePurchase = (packageName: string) => {
    setSelectedPackage(packageName);
    // TODO: Implement actual purchase logic
    console.log(`Purchasing ${packageName}`);
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
                {" "}Credit
              </span>
              <br />
              Package
            </h1>
            <p className="text-base text-muted-foreground mb-4 max-w-2xl mx-auto">
              From starter packs to enterprise solutions, find the perfect credit package
              for your video generation needs. Credits never expire and can be used for any video generation.
            </p>

            {/* BILLING TOGGLE */}
            <div className="flex items-center justify-center space-x-4 mb-6">
              <span className={`text-sm font-medium ${billingPeriod === "monthly" ? "text-foreground" : "text-muted-foreground"}`}>
                One-time
              </span>
              <button
                onClick={() => setBillingPeriod(billingPeriod === "monthly" ? "yearly" : "monthly")}
                className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    billingPeriod === "yearly" ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
              <span className={`text-sm font-medium ${billingPeriod === "yearly" ? "text-foreground" : "text-muted-foreground"}`}>
                Bulk Discount
                <Badge className="ml-2 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Save 20%</Badge>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* CREDITS PACKAGES */}
      <div className="container mx-auto px-4 py-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 h-[calc(100vh-300px)] max-h-[600px]">
          {creditsPackages.map((pkg) => {
            const Icon = pkg.icon;
            return (
              <Card
                key={pkg.name}
                className={`relative ${pkg.color} ${pkg.popular ? 'ring-2 ring-primary scale-105' : ''} transition-all duration-200 hover:shadow-lg flex flex-col`}
              >
                {pkg.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground px-4 py-1">
                      <Star className="w-3 h-3 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-3">
                  <CardTitle className="text-xl font-bold">{pkg.name}</CardTitle>
                  <CardDescription className="text-xs">{pkg.description}</CardDescription>
                  <div className="mt-3">
                    <div className="text-3xl font-bold">${pkg.price}</div>
                    <div className="text-xs text-muted-foreground">
                      {(pkg.credits + pkg.bonus).toLocaleString()} credits
                      {pkg.bonus > 0 && (
                        <span className="text-green-500 ml-1">
                          (+{pkg.bonus.toLocaleString()} bonus)
                        </span>
                      )}
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-3 flex-1 flex flex-col">
                  <div className="flex-1">
                    <ul className="space-y-2">
                      <li className="flex items-start space-x-2">
                        <Check className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-xs">High-quality video generation</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Check className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-xs">Multiple visual styles</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Check className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-xs">Custom music integration</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Check className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-xs">Priority processing</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Check className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-xs">No watermarks</span>
                      </li>
                      <li className="flex items-start space-x-2">
                        <Check className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-xs">Download in multiple formats</span>
                      </li>
                    </ul>
                  </div>

                  <Button
                    className="w-full mt-4"
                    size="sm"
                    variant={pkg.popular ? "default" : "outline"}
                    onClick={() => handlePurchase(pkg.name)}
                  >
                    Purchase Credits
                    <ArrowRight className="w-3 h-3 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
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
            Compare all features across our different credit packages to find the perfect fit for your needs.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2 font-medium text-sm">Features</th>
                <th className="text-center p-2 font-medium text-sm">Starter</th>
                <th className="text-center p-2 font-medium text-sm">Creator</th>
                <th className="text-center p-2 font-medium text-sm">Pro</th>
                <th className="text-center p-2 font-medium text-sm">Enterprise</th>
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
                        {item.starter ? (
                          <Check className="w-3 h-3 text-green-500 mx-auto" />
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="p-2 text-center">
                        {item.creator ? (
                          <Check className="w-3 h-3 text-green-500 mx-auto" />
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="p-2 text-center">
                        {item.pro ? (
                          <Check className="w-3 h-3 text-green-500 mx-auto" />
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </td>
                      <td className="p-2 text-center">
                        {item.enterprise ? (
                          <Check className="w-3 h-3 text-green-500 mx-auto" />
                        ) : (
                          <span className="text-muted-foreground">—</span>
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
