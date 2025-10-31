"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/ui/use-toast";
import { 
  Users, 
  Copy,
  CheckCircle,
  RefreshCw
} from "lucide-react";

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

export default function CustomersPage() {
  const [customers, setCustomers] = useState<StripeCustomer[]>([]);
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchStripeData = async () => {
    setLoading(true);
    try {
      // Mock data - no customers yet
      const mockCustomers: StripeCustomer[] = [];

      setCustomers(mockCustomers);

      toast({
        title: "Data Loaded",
        description: "Customers loaded successfully",
      });

    } catch (error) {
      console.error('Error fetching customers:', error);
      toast({
        title: "Error",
        description: "Failed to fetch customers",
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

  useEffect(() => {
    fetchStripeData();
  }, []);

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Customers</h1>
          <p className="text-muted-foreground">Manage customer information and subscriptions</p>
        </div>
        <Button onClick={fetchStripeData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh Data
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Customers ({customers.length})
          </CardTitle>
          <CardDescription>Customer information and subscriptions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {customers.length === 0 ? (
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No customers yet</h3>
                <p className="text-muted-foreground">
                  Customers will appear here once they make purchases through your payment links.
                </p>
              </div>
            ) : (
              customers.map((customer) => (
                <div key={customer.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">{customer.name || customer.email}</h3>
                      <p className="text-sm text-muted-foreground">{customer.email}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs text-muted-foreground">
                          Created: {formatDate(customer.created)}
                        </span>
                        {customer.subscriptions?.data && customer.subscriptions.data.length > 0 && (
                          <Badge variant="default">
                            {customer.subscriptions.data.length} subscription(s)
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(customer.id, customer.id)}
                      >
                        {copiedId === customer.id ? (
                          <CheckCircle className="w-4 h-4" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </Button>
                      <code className="text-xs bg-muted px-2 py-1 rounded">
                        {customer.id}
                      </code>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
