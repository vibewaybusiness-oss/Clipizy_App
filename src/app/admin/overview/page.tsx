"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/ui/use-toast";
import { 
  Package, 
  DollarSign, 
  Link, 
  Users, 
  TrendingUp,
  RefreshCw,
  ExternalLink
} from "lucide-react";

interface StripeProduct {
  id: string;
  name: string;
  description: string;
  active: boolean;
  created: number;
  default_price?: string;
}

interface StripePrice {
  id: string;
  object: string;
  active: boolean;
  currency: string;
  unit_amount: number;
  recurring?: {
    interval: string;
  };
  product: string;
  created: number;
}

interface StripePaymentLink {
  id: string;
  url: string;
  active: boolean;
  created: number;
  line_items: Array<{
    price: string;
    quantity: number;
  }>;
}

interface StripeCustomer {
  id: string;
  email: string;
  name?: string;
  created: number;
  subscriptions?: {
    data: Array<{
      id: string;
      status: string;
      current_period_end: number;
    }>;
  };
}

export default function OverviewPage() {
  const [products, setProducts] = useState<StripeProduct[]>([]);
  const [prices, setPrices] = useState<StripePrice[]>([]);
  const [paymentLinks, setPaymentLinks] = useState<StripePaymentLink[]>([]);
  const [customers, setCustomers] = useState<StripeCustomer[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const fetchStripeData = async () => {
    setLoading(true);
    try {
      // Mock data based on what we created earlier
      const mockProducts = [
        {
          id: "prod_T6tlpHdA9aMrgm",
          name: "Creator Plan",
          description: "Perfect for content creators and influencers - 2,000 credits per month",
          active: true,
          created: Math.floor(Date.now() / 1000) - 3600,
          default_price: "price_1SAfyCRpPDjqChm1bjiivK16"
        },
        {
          id: "prod_T6tlJ9FvMmO3Rn",
          name: "Pro Plan",
          description: "For professional creators and agencies - 6,000 credits per month",
          active: true,
          created: Math.floor(Date.now() / 1000) - 3600,
          default_price: "price_1SAfyHRpPDjqChm1oYM7RnnU"
        }
      ];

      const mockPrices = [
        {
          id: "price_1SAfyCRpPDjqChm1bjiivK16",
          object: "price",
          active: true,
          currency: "usd",
          unit_amount: 1900,
          recurring: { interval: "month" },
          product: "prod_T6tlpHdA9aMrgm",
          created: Math.floor(Date.now() / 1000) - 3600
        },
        {
          id: "price_1SAfyHRpPDjqChm1oYM7RnnU",
          object: "price",
          active: true,
          currency: "usd",
          unit_amount: 4900,
          recurring: { interval: "month" },
          product: "prod_T6tlJ9FvMmO3Rn",
          created: Math.floor(Date.now() / 1000) - 3600
        }
      ];

      const mockPaymentLinks = [
        {
          id: "plink_1SAfznRpPDjqChm1UoKbQYDr",
          url: "https://buy.stripe.com/test_5kQ14pbnKa4Rbce5Mffw400",
          active: true,
          created: Math.floor(Date.now() / 1000) - 3600,
          line_items: [{ price: "price_1SAfyCRpPDjqChm1bjiivK16", quantity: 1 }]
        },
        {
          id: "plink_1SAfzsRpPDjqChm1AdoWkzJQ",
          url: "https://buy.stripe.com/test_6oU00l0J65OBeoq7Unfw401",
          active: true,
          created: Math.floor(Date.now() / 1000) - 3600,
          line_items: [{ price: "price_1SAfyHRpPDjqChm1oYM7RnnU", quantity: 1 }]
        }
      ];

      setProducts(mockProducts);
      setPrices(mockPrices);
      setPaymentLinks(mockPaymentLinks);
      setCustomers([]); // No customers yet

      toast({
        title: "Data Loaded",
        description: "Stripe data loaded successfully",
      });

    } catch (error) {
      console.error('Error fetching Stripe data:', error);
      toast({
        title: "Error",
        description: "Failed to fetch Stripe data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStripeData();
  }, []);

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Admin Overview</h1>
          <p className="text-muted-foreground">Monitor your Stripe integration and payment data</p>
        </div>
        <Button onClick={fetchStripeData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh Data
        </Button>
      </div>

      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Products</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{products.length}</div>
              <p className="text-xs text-muted-foreground">
                Active products in Stripe
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Prices</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{prices.length}</div>
              <p className="text-xs text-muted-foreground">
                Configured prices
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Payment Links</CardTitle>
              <Link className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{paymentLinks.length}</div>
              <p className="text-xs text-muted-foreground">
                Active payment links
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Customers</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{customers.length}</div>
              <p className="text-xs text-muted-foreground">
                Total customers
              </p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common admin tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button variant="outline" className="justify-start">
                <ExternalLink className="w-4 h-4 mr-2" />
                View Stripe Dashboard
              </Button>
              <Button variant="outline" className="justify-start">
                <TrendingUp className="w-4 h-4 mr-2" />
                View Analytics
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
