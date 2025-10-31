"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Coins,
  Plus,
  ArrowLeft,
  Loader2,
  Check,
  TrendingUp,
  Zap,
  Star
} from "lucide-react";
import { useCredits } from "@/hooks/business/use-credits";
import { useToast } from "@/hooks/ui/use-toast";
import { getBackendUrl } from "@/lib/config";
import Link from "next/link";

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

export default function PurchasePage() {
  const { balance, purchaseCredits } = useCredits();
  const { toast } = useToast();
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [customAmount, setCustomAmount] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const handlePurchase = async (packageId: string) => {
    const pkg = creditsPackages.find(p => p.id === packageId);
    if (!pkg) return;

    try {
      setIsProcessing(true);
      setSelectedPackage(packageId);

      // Create Stripe checkout session for credits purchase
      const response = await fetch(`${getBackendUrl()}/api/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ 
          plan_id: packageId,
          plan_type: 'credits'
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
      console.error('Purchase error:', error);
      toast({
        title: "Purchase Failed",
        description: error instanceof Error ? error.message : "Failed to create checkout session",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
      setSelectedPackage(null);
    }
  };

  const handleCustomPurchase = async () => {
    const amount = parseFloat(customAmount);
    if (isNaN(amount) || amount < 1 || amount > 1000) {
      toast({
        variant: "destructive",
        title: "Invalid Amount",
        description: "Please enter an amount between $1 and $1000",
      });
      return;
    }

    try {
      setIsProcessing(true);

      // Create Stripe checkout session for custom credits purchase
      const response = await fetch(`${getBackendUrl()}/api/payments/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ 
          plan_type: 'credits',
          custom_amount: amount
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

      setCustomAmount("");
    } catch (error) {
      console.error('Custom purchase error:', error);
      toast({
        title: "Purchase Failed",
        description: error instanceof Error ? error.message : "Failed to create checkout session",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="p-8 space-y-8">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/dashboard/credits">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Credits
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Purchase Credits</h1>
            <p className="text-muted-foreground text-lg">
              Choose a package or enter a custom amount to buy credits
            </p>
          </div>
        </div>
      </div>

      {/* CURRENT BALANCE */}
      <Card className="bg-gradient-to-r from-primary/10 to-purple-500/10 border-primary/20">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-primary/20 rounded-full">
                <Coins className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-foreground">Current Balance</h2>
                <div className="text-3xl font-bold text-primary">
                  {balance?.current_balance?.toLocaleString() || 0} Credits
                </div>
              </div>
            </div>
            <div className="text-right text-sm text-muted-foreground">
              <div>Total Earned: {balance?.total_earned?.toLocaleString() || 0}</div>
              <div>Total Spent: {balance?.total_spent?.toLocaleString() || 0}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* POINTS PACKAGES */}
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-semibold mb-6">Point Packages</h2>

            <div className="space-y-4">
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

                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold mb-2">{pkg.name}</h3>
                        <p className="text-muted-foreground mb-4">{pkg.description}</p>

                        <div className="flex items-center space-x-4 mb-4">
                          <div>
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
                        </div>

                        <ul className="space-y-2 mb-4">
                          {pkg.features.map((feature, index) => (
                            <li key={index} className="flex items-center text-sm">
                              <Check className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </div>

                      <Button
                        size="lg"
                        className="ml-4"
                        onClick={() => handlePurchase(pkg.id)}
                        disabled={isProcessing && selectedPackage === pkg.id}
                      >
                        {isProcessing && selectedPackage === pkg.id ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <Plus className="w-4 h-4 mr-2" />
                        )}
                        Purchase
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* CUSTOM AMOUNT & INFO */}
        <div className="space-y-6">
          {/* CUSTOM AMOUNT */}
          <Card className="bg-card border border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span>Custom Amount</span>
              </CardTitle>
              <CardDescription>
                Purchase any amount of credits (100 credits per $1)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="custom-amount">Amount ($)</Label>
                <Input
                  id="custom-amount"
                  type="number"
                  min="1"
                  max="1000"
                  step="0.01"
                  value={customAmount}
                  onChange={(e) => setCustomAmount(e.target.value)}
                  placeholder="Enter amount"
                  className="text-lg"
                />
              </div>

              {customAmount && (
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">You'll receive:</div>
                  <div className="text-2xl font-bold text-primary">
                    {Math.floor(parseFloat(customAmount) * 100).toLocaleString()} credits
                  </div>
                </div>
              )}

              <Button
                className="w-full"
                size="lg"
                onClick={handleCustomPurchase}
                disabled={isProcessing || !customAmount}
              >
                {isProcessing ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Zap className="w-4 h-4 mr-2" />
                )}
                Purchase Custom Amount
              </Button>
            </CardContent>
          </Card>

          {/* POINTS INFO */}
          <Card className="bg-card border border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Coins className="w-5 h-5" />
                <span>How Credits Work</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <div className="font-medium">Video Generation</div>
                    <div className="text-sm text-muted-foreground">50-500 credits per video depending on length and quality</div>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <div className="font-medium">Priority Processing</div>
                    <div className="text-sm text-muted-foreground">Faster generation times for Creator and Pro packages</div>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <div className="font-medium">Credits Never Expire</div>
                    <div className="text-sm text-muted-foreground">Purchased credits are yours forever</div>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
                  <div>
                    <div className="font-medium">Bonus Credits</div>
                    <div className="text-sm text-muted-foreground">Get extra credits with larger packages</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* PAYMENT METHODS */}
          <Card className="bg-card border border-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Check className="w-5 h-5" />
                <span>Secure Payment</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-sm">
                  <Check className="w-4 h-4 text-green-500" />
                  <span>Powered by Stripe</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Check className="w-4 h-4 text-green-500" />
                  <span>SSL Encrypted</span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Check className="w-4 h-4 text-green-500" />
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Check className="w-4 h-4 text-green-500" />
                  <span>Instant point delivery</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
