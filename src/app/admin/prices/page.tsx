"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/ui/use-toast";
import { 
  DollarSign, 
  Copy,
  CheckCircle,
  RefreshCw
} from "lucide-react";

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

export default function PricesPage() {
  const [prices, setPrices] = useState<StripePrice[]>([]);
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchStripeData = async () => {
    setLoading(true);
    try {
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

      setPrices(mockPrices);

      toast({
        title: "Data Loaded",
        description: "Prices loaded successfully",
      });

    } catch (error) {
      console.error('Error fetching prices:', error);
      toast({
        title: "Error",
        description: "Failed to fetch prices",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
      toast({
        title: "Copied",
        description: "ID copied to clipboard",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to copy to clipboard",
        variant: "destructive"
      });
    }
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString();
  };

  const formatAmount = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount / 100);
  };

  useEffect(() => {
    fetchStripeData();
  }, []);

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Stripe Prices</h1>
          <p className="text-muted-foreground">Manage your pricing configurations</p>
        </div>
        <Button onClick={fetchStripeData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh Data
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Prices ({prices.length})
          </CardTitle>
          <CardDescription>Pricing configurations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {prices.map((price) => (
              <div key={price.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">
                        {formatAmount(price.unit_amount, price.currency)}
                      </h3>
                      {price.recurring && (
                        <Badge variant="outline">
                          {price.recurring.interval}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Product: {price.product}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={price.active ? "default" : "secondary"}>
                        {price.active ? "Active" : "Inactive"}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        Created: {formatDate(price.created)}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(price.id, price.id)}
                    >
                      {copiedId === price.id ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {price.id}
                    </code>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
