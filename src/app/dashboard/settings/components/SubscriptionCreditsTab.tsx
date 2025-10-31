"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { 
  CreditCard, 
  Zap, 
  Crown, 
  Star, 
  CheckCircle,
  ExternalLink,
  Calendar,
  Users,
  Settings,
  TrendingUp,
  Clock,
  DollarSign,
  Shield,
  Sparkles,
  ArrowRight,
  Check,
  X
} from "lucide-react";
import { useAuth } from "@/contexts/auth-context";
import { useToast } from "@/hooks/ui/use-toast";
import { getBackendUrl } from "@/lib/config";

interface SubscriptionInfo {
  tier: 'free' | 'creator' | 'pro' | 'business';
  status: 'active' | 'cancelled' | 'past_due' | 'trialing';
  renewsAt: string | null;
  billingCycle: 'monthly' | 'yearly' | null;
  price: number;
  currency: string;
  creditsUsed: number;
  creditsTotal: number;
  videosGenerated: number;
  lastBillingDate: string | null;
  nextBillingDate: string | null;
}



const subscriptionTiers = {
  free: {
    name: 'Free Tier',
    icon: Star,
    color: 'bg-gray-500',
    description: 'Basic features with limited usage',
    credits: 60,
    features: ['60 Credits Included', '720p Max (Watermarked)', '1 GB Cloud Storage', 'Basic BPM & Key Analysis', 'Regular Model LLM', 'Basic Views Count Analytics', 'Community Support'],
    price: 0
  },
  creator: {
    name: 'Tier 1: Creator',
    icon: Zap,
    color: 'bg-blue-500',
    description: 'Perfect for content creators and influencers',
    credits: 1500,
    features: ['1,500 Credits Included', '1080p Full HD (No Watermark)', '50 GB Cloud Storage', 'Full Advanced Music Analysis', 'Regular Model LLM', 'Video Automation Access', 'Commercial Licensing', 'Email Support (Standard SLA)'],
    price: 25
  },
  pro: {
    name: 'Tier 2: Pro',
    icon: Crown,
    color: 'bg-purple-500',
    description: 'For professional creators and agencies',
    credits: 5000,
    features: ['5,000 Credits Included', '1080p Full HD', '250 GB Cloud Storage', 'Full Advanced Music Analysis', 'Regular Model LLM', 'Video Automation Access (Auto-Upload)', 'Full Social Media Stats & Potential Gains', 'Priority Email Support'],
    price: 59
  },
  business: {
    name: 'Tier 3: Business',
    icon: Settings,
    color: 'bg-amber-500',
    description: 'For large teams and organizations',
    credits: 12500,
    features: ['12,500 Credits Included', '1080p Full HD', '1 TB Cloud Storage', 'Full Advanced Music Analysis', 'Premium Model LLM', 'Video Automation Access (Advanced Queue)', 'Full Social Media Stats & Dedicated Reporting', 'Dedicated Account Manager/SLA'],
    price: 119
  }
};


export default function SubscriptionCreditsTab() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [subscriptionInfo, setSubscriptionInfo] = useState<SubscriptionInfo>({
    tier: 'free',
    status: 'active',
    renewsAt: null,
    billingCycle: null,
    price: 0,
    currency: 'USD',
    creditsUsed: 3,
    creditsTotal: 10,
    videosGenerated: 2,
    lastBillingDate: null,
    nextBillingDate: null
  });

  useEffect(() => {
    loadSubscriptionData();

    const handleBeforeUnload = () => {
      saveToDatabase();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []); // Empty dependency array to run only once

  const loadSubscriptionData = async () => {
    setIsLoading(true);
    try {
      // localStorage removed - backend storage only

      // Try to load subscription info from backend
      try {
        const subscriptionResponse = await fetch(`${getBackendUrl()}/user-management/subscription`);
        if (subscriptionResponse.ok) {
          const subscriptionData = await subscriptionResponse.json();
          if (subscriptionData.success) {
            setSubscriptionInfo(subscriptionData.subscription);
            // localStorage removed - backend storage only
          }
        }
      } catch (apiError) {
        console.warn('Backend unavailable, using default subscription data:', apiError);
        
        // Use default subscription data when backend is unavailable
        const defaultSubscription: SubscriptionInfo = {
          tier: 'free',
          status: 'active',
          renewsAt: null,
          billingCycle: null,
          price: 0,
          currency: 'USD',
          creditsUsed: 15,
          creditsTotal: 60,
          videosGenerated: 2,
          lastBillingDate: null,
          nextBillingDate: null
        };
        
        setSubscriptionInfo(defaultSubscription);
        // localStorage removed - backend storage only
        
        toast({
          title: "Demo Mode",
          description: "Using demo subscription data - backend unavailable",
          variant: "default"
        });
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

  const saveToDatabase = async () => {
    try {
      await fetch(`${getBackendUrl()}/user-management/subscription`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(subscriptionInfo),
      });
    } catch (error) {
      console.warn('Backend unavailable, subscription data saved locally only:', error);
      // Data is already saved in localStorage, so this is not critical
    }
  };



  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case 'cancelled':
        return <Badge variant="secondary">Cancelled</Badge>;
      case 'past_due':
        return <Badge className="bg-red-100 text-red-800">Past Due</Badge>;
      case 'trialing':
        return <Badge className="bg-blue-100 text-blue-800">Trial</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  const currentTier = subscriptionTiers[subscriptionInfo.tier as keyof typeof subscriptionTiers];
  const TierIcon = currentTier.icon;

  const creditsPercentage = (subscriptionInfo.creditsUsed / subscriptionInfo.creditsTotal) * 100;

  return (
    <div className="space-y-6 h-full flex flex-col">
      {/* HEADER SECTION */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 p-4 sm:p-6 bg-gradient-to-r from-primary/5 to-purple-500/5 rounded-xl border border-primary/10">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="p-3 rounded-xl bg-primary/10">
            <CreditCard className="w-6 h-6 text-primary" />
          </div>
          <div className="flex-1">
            <h2 className="text-xl sm:text-2xl font-bold text-foreground">Subscription & Credits</h2>
            <p className="text-sm sm:text-base text-muted-foreground">Manage your subscription, billing, and usage</p>
          </div>
        </div>
        <div className="text-center sm:text-right w-full sm:w-auto">
          <div className="text-2xl sm:text-3xl font-bold text-primary">
            {subscriptionInfo.creditsTotal - subscriptionInfo.creditsUsed}
          </div>
          <div className="text-sm text-muted-foreground">Credits Remaining</div>
        </div>
      </div>

      {/* MAIN CONTENT GRID */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 sm:gap-6 flex-1">
        {/* LEFT COLUMN - SUBSCRIPTION INFO */}
        <div className="xl:col-span-2 space-y-4 sm:space-y-6">
          {/* CURRENT PLAN CARD */}
          <Card className="border-2 border-primary/20">
            <CardHeader className="pb-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${currentTier.color}`}>
                    <TierIcon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg sm:text-xl">{currentTier.name} Plan</CardTitle>
                    <CardDescription className="text-sm sm:text-base">{currentTier.description}</CardDescription>
                  </div>
                </div>
                <div className="text-left sm:text-right">
                  {getStatusBadge(subscriptionInfo.status)}
                  {subscriptionInfo.price > 0 && (
                    <div className="mt-2">
                      <div className="text-xl sm:text-2xl font-bold text-foreground">
                        ${subscriptionInfo.price}
                        <span className="text-sm font-normal text-muted-foreground">
                          /{subscriptionInfo.billingCycle === 'yearly' ? 'year' : 'month'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* PLAN FEATURES */}
              <div>
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Plan Features
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {currentTier.features.map((feature: string, index: number) => (
                    <div key={index} className="flex items-center gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-500 flex-shrink-0" />
                      <span className="break-words">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* ACTION BUTTONS */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Button 
                  className="flex-1 h-11 sm:h-12 text-sm sm:text-base font-medium bg-gradient-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90 text-white"
                  onClick={() => window.location.href = '/dashboard/pricing'}
                >
                  <Crown className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                  Upgrade Plan
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
                <Button 
                  variant="outline" 
                  className="flex-1 h-11 sm:h-12 text-sm sm:text-base font-medium border-primary/20 hover:bg-primary/5"
                  onClick={() => window.location.href = '/dashboard/credits'}
                >
                  <Zap className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                  Buy Credits
                  <ExternalLink className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* USAGE STATISTICS */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Usage Statistics
              </CardTitle>
              <CardDescription>
                Track your credits usage and activity this month
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* CREDITS USAGE */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Credits Used</span>
                  <span className="text-sm text-muted-foreground">
                    {subscriptionInfo.creditsUsed} / {subscriptionInfo.creditsTotal}
                  </span>
                </div>
                <Progress value={creditsPercentage} className="h-3" />
                <div className="flex justify-between text-sm text-muted-foreground">
                  <span>{Math.round(creditsPercentage)}% used</span>
                  <span>{subscriptionInfo.creditsTotal - subscriptionInfo.creditsUsed} remaining</span>
                </div>
              </div>

              {/* STATS GRID */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div className="p-3 sm:p-4 bg-muted/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="w-4 h-4 text-blue-500" />
                    <span className="text-sm font-medium">Videos Generated</span>
                  </div>
                  <div className="text-xl sm:text-2xl font-bold">{subscriptionInfo.videosGenerated}</div>
                  <div className="text-xs text-muted-foreground">This month</div>
                </div>
                <div className="p-3 sm:p-4 bg-muted/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-4 h-4 text-green-500" />
                    <span className="text-sm font-medium">Avg. per Video</span>
                  </div>
                  <div className="text-xl sm:text-2xl font-bold">
                    {subscriptionInfo.videosGenerated > 0 
                      ? Math.round(subscriptionInfo.creditsUsed / subscriptionInfo.videosGenerated)
                      : 0
                    }
                  </div>
                  <div className="text-xs text-muted-foreground">Credits</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* RIGHT COLUMN - BILLING & QUICK ACTIONS */}
        <div className="space-y-4 sm:space-y-6">
          {/* BILLING INFORMATION */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Billing Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  {getStatusBadge(subscriptionInfo.status)}
                </div>
                {subscriptionInfo.nextBillingDate && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Next Billing</span>
                    <span className="text-sm font-medium">{formatDate(subscriptionInfo.nextBillingDate)}</span>
                  </div>
                )}
                {subscriptionInfo.lastBillingDate && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Last Billing</span>
                    <span className="text-sm font-medium">{formatDate(subscriptionInfo.lastBillingDate)}</span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Billing Cycle</span>
                  <span className="text-sm font-medium">
                    {subscriptionInfo.billingCycle ? 
                      subscriptionInfo.billingCycle.charAt(0).toUpperCase() + subscriptionInfo.billingCycle.slice(1) 
                      : 'N/A'
                    }
                  </span>
                </div>
              </div>
              <Separator />
              <Button variant="outline" className="w-full" size="sm">
                <CreditCard className="w-4 h-4 mr-2" />
                Manage Billing
              </Button>
            </CardContent>
          </Card>

          {/* QUICK ACTIONS */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start" size="sm">
                <Shield className="w-4 h-4 mr-2" />
                Download Invoices
              </Button>
              <Button variant="outline" className="w-full justify-start" size="sm">
                <Calendar className="w-4 h-4 mr-2" />
                Billing History
              </Button>
              <Button variant="outline" className="w-full justify-start" size="sm">
                <Users className="w-4 h-4 mr-2" />
                Team Management
              </Button>
            </CardContent>
          </Card>

          {/* UPGRADE SUGGESTION */}
          {subscriptionInfo.tier === 'free' && (
            <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-purple-500/5">
              <CardHeader className="pb-3">
                <CardTitle className="text-base sm:text-lg flex items-center gap-2">
                  <Crown className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
                  Ready to Upgrade?
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Unlock more credits, premium features, and priority support.
                </p>
                <Button className="w-full h-10 sm:h-11 text-sm sm:text-base bg-gradient-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90">
                  View Plans
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
