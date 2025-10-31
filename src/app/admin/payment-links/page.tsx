"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/ui/use-toast";
import { 
  Link, 
  Copy,
  CheckCircle,
  RefreshCw,
  ExternalLink
} from "lucide-react";

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

export default function PaymentLinksPage() {
  const [paymentLinks, setPaymentLinks] = useState<StripePaymentLink[]>([]);
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchStripeData = async () => {
    setLoading(true);
    try {
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

      setPaymentLinks(mockPaymentLinks);

      toast({
        title: "Data Loaded",
        description: "Payment links loaded successfully",
      });

    } catch (error) {
      console.error('Error fetching payment links:', error);
      toast({
        title: "Error",
        description: "Failed to fetch payment links",
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
        description: "Link copied to clipboard",
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

  useEffect(() => {
    fetchStripeData();
  }, []);

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Payment Links</h1>
          <p className="text-muted-foreground">Manage your shareable payment links</p>
        </div>
        <Button onClick={fetchStripeData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh Data
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Link className="h-5 w-5" />
            Payment Links ({paymentLinks.length})
          </CardTitle>
          <CardDescription>Shareable payment links</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {paymentLinks.map((link) => (
              <div key={link.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">Payment Link</h3>
                    <p className="text-sm text-muted-foreground">
                      {link.line_items.length} item(s)
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant={link.active ? "default" : "secondary"}>
                        {link.active ? "Active" : "Inactive"}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        Created: {formatDate(link.created)}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => window.open(link.url, '_blank')}
                    >
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(link.url, link.id)}
                    >
                      {copiedId === link.id ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </Button>
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {link.id}
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
