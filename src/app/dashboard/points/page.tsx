"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Coins,
  Plus,
  History,
  ArrowRight,
  Search,
  CreditCard
} from "lucide-react";
import { useCredits } from "@/hooks/business/use-credits";
import Link from "next/link";
import { ClipizyLoading } from "@/components/ui/clipizy-loading";

export default function CreditsPage() {
  const { balance, transactions, loading } = useCredits();
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredTransactions, setFilteredTransactions] = useState(transactions);

  useEffect(() => {
    let filtered = transactions;

    if (searchTerm) {
      filtered = filtered.filter(transaction =>
        transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.reference_id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredTransactions(filtered);
  }, [transactions, searchTerm]);



  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="flex items-center justify-center h-64">
          <ClipizyLoading message="Loading credits..." size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Credits Management</h1>
          <p className="text-muted-foreground text-lg">
            Manage your credits balance and purchase more credits
          </p>
        </div>
        <Button asChild>
          <Link href="/pricing">
            <ArrowRight className="w-4 h-4 mr-2" />
            View Subscriptions
          </Link>
        </Button>
      </div>

      {/* POINTS BALANCE CARD */}
      <Card className="bg-gradient-to-r from-primary/10 to-purple-500/10 border-primary/20">
        <CardContent className="p-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="p-4 bg-primary/20 rounded-full">
                <Coins className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground">Current Balance</h2>
                <div className="text-4xl font-bold text-primary mt-2">
                  {balance?.current_balance?.toLocaleString() || 0}
                </div>
                <div className="text-muted-foreground">Credits Available</div>
              </div>
            </div>

            <div className="text-right space-y-2">
              <div className="flex items-center space-x-4 text-sm">
                <div>
                  <div className="text-muted-foreground">Total Earned</div>
                  <div className="font-semibold">{balance?.total_earned?.toLocaleString() || 0}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Total Spent</div>
                  <div className="font-semibold">{balance?.total_spent?.toLocaleString() || 0}</div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
        {/* TRANSACTION HISTORY */}
        <div className="space-y-6 flex flex-col h-full">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Recent Transactions</h2>
            <Button variant="outline" asChild>
              <Link href="/dashboard/credits/history">
                <History className="w-4 h-4 mr-2" />
                View All
              </Link>
            </Button>
          </div>

          {/* SEARCH */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search transactions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* TRANSACTIONS LIST */}
          <Card className="bg-card border border-border flex-1">
            <CardContent className="p-6 h-full">
              {filteredTransactions.length === 0 ? (
                <div className="text-center py-12 h-full flex flex-col items-center justify-center">
                  <Coins className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-foreground mb-2">No transactions yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Your transaction history will appear here
                  </p>
                </div>
              ) : (
                <div className="space-y-3 h-full overflow-y-auto">
                  {filteredTransactions.slice(0, 10).map((transaction) => {
                    const isPositive = transaction.amount > 0;
                    const typeColors = {
                      earned: "text-green-600",
                      purchased: "text-blue-600",
                      spent: "text-red-600",
                      refunded: "text-yellow-600",
                      bonus: "text-purple-600",
                      admin_adjustment: "text-gray-600"
                    };

                    return (
                      <div
                        key={transaction.id}
                        className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center space-x-3">
                          <div className={`w-2 h-2 rounded-full ${
                            isPositive ? 'bg-green-500' : 'bg-red-500'
                          }`} />
                          <div>
                            <div className="font-medium text-sm">{transaction.description || "Credits Transaction"}</div>
                            <div className="text-xs text-muted-foreground">
                              {new Date(transaction.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`font-semibold text-sm ${
                            isPositive ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {isPositive ? '+' : ''}{transaction.amount.toLocaleString()}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Balance: {transaction.balance_after.toLocaleString()}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* PURCHASE POINTS */}
        <div className="space-y-8">
          <div>
            <h2 className="text-2xl font-semibold mb-6">Purchase Credits</h2>

            {/* SINGLE PURCHASE BUTTON */}
            <Card className="bg-gradient-to-r from-primary/10 to-purple-500/10 border-primary/20">
              <CardContent className="p-8 text-center">
                <div className="mb-6">
                  <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Coins className="w-8 h-8 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Need More Credits?</h3>
                  <p className="text-muted-foreground mb-6">
                    Choose from our point packages or purchase a custom amount.
                    All purchases include bonus credits and priority processing.
                  </p>
                </div>

                <Button size="lg" className="w-full" asChild>
                  <Link href="/dashboard/credits/purchase">
                    <Plus className="w-5 h-5 mr-2" />
                    Purchase Credits
                  </Link>
                </Button>

                <div className="mt-4 text-sm text-muted-foreground">
                  Starting from $10 • 100 credits per $1
                </div>
              </CardContent>
            </Card>
        </div>

        <div className="space-y-8">
            {/* HELPFUL LINKS */}
            <Card className="bg-card border border-border">
              <CardHeader>
                <CardTitle className="text-lg">Helpful Links</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="ghost" className="w-full justify-start" asChild>
                  <Link href="/pricing">
                    <ArrowRight className="w-4 h-4 mr-2" />
                    View Subscription Plans
                  </Link>
                </Button>
                <Button variant="ghost" className="w-full justify-start" asChild>
                  <Link href="/dashboard/settings/billing">
                    <CreditCard className="w-4 h-4 mr-2" />
                    Billing Settings
                  </Link>
                </Button>
                <Button variant="ghost" className="w-full justify-start" asChild>
                  <Link href="/dashboard/credits/history">
                    <History className="w-4 h-4 mr-2" />
                    Transaction History
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
