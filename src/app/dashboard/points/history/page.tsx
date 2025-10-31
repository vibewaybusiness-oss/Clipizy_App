"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  History,
  Search,
  Filter,
  Download,
  ArrowLeft,
  Coins,
  CreditCard,
  Gift,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock
} from "lucide-react";
import { useCredits } from "@/hooks/business/use-credits";
import { ClipizyLoading } from "@/components/ui/clipizy-loading";
import Link from "next/link";

const transactionTypes = {
  earned: { label: "Earned", color: "bg-green-100 text-green-800", icon: Gift },
  spent: { label: "Spent", color: "bg-red-100 text-red-800", icon: Coins },
  purchased: { label: "Purchased", color: "bg-blue-100 text-blue-800", icon: CreditCard },
  refunded: { label: "Refunded", color: "bg-yellow-100 text-yellow-800", icon: ArrowLeft },
  bonus: { label: "Bonus", color: "bg-purple-100 text-purple-800", icon: Gift },
  admin_adjustment: { label: "Admin", color: "bg-gray-100 text-gray-800", icon: AlertCircle }
};

export default function TransactionHistoryPage() {
  const { transactions, loading, fetchTransactions } = useCredits();
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [filteredTransactions, setFilteredTransactions] = useState(transactions);

  useEffect(() => {
    fetchTransactions(100);
  }, [fetchTransactions]);

  useEffect(() => {
    let filtered = transactions;

    if (searchTerm) {
      filtered = filtered.filter(transaction =>
        transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.reference_id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (filterType !== "all") {
      filtered = filtered.filter(transaction => transaction.transaction_type === filterType);
    }

    setFilteredTransactions(filtered);
  }, [transactions, searchTerm, filterType]);

  const exportTransactions = () => {
    const csvContent = [
      ["Date", "Type", "Description", "Amount", "Balance After", "Reference"],
      ...filteredTransactions.map(t => [
        new Date(t.created_at).toLocaleDateString(),
        transactionTypes[t.transaction_type as keyof typeof transactionTypes]?.label || t.transaction_type,
        t.description || "",
        t.amount.toString(),
        t.balance_after.toString(),
        t.reference_id || ""
      ])
    ].map(row => row.join(",")).join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `credits-transactions-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="p-8 space-y-6">
        <div className="flex items-center justify-center h-64">
          <ClipizyLoading message="Loading transaction history..." size="lg" />
        </div>
      </div>
    );
  }

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
            <h1 className="text-3xl font-bold text-foreground mb-2">Transaction History</h1>
            <p className="text-muted-foreground text-lg">
              Complete history of all your credits transactions
            </p>
          </div>
        </div>
        <Button onClick={exportTransactions} variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {/* FILTERS */}
      <Card className="bg-card border border-border">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  placeholder="Search transactions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-2 border border-border rounded-md bg-background text-foreground"
              >
                <option value="all">All Types</option>
                {Object.entries(transactionTypes).map(([key, type]) => (
                  <option key={key} value={key}>{type.label}</option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* TRANSACTIONS LIST */}
      <Card className="bg-card border border-border">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <History className="w-5 h-5" />
            <span>All Transactions</span>
            <Badge variant="secondary">{filteredTransactions.length}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredTransactions.length === 0 ? (
            <div className="text-center py-12">
              <History className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No transactions found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || filterType !== "all"
                  ? "Try adjusting your search or filter criteria"
                  : "You haven't made any transactions yet"
                }
              </p>
              {!searchTerm && filterType === "all" && (
                <Button asChild>
                  <Link href="/dashboard/credits">
                    Purchase Credits
                  </Link>
                </Button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredTransactions.map((transaction) => {
                const typeInfo = transactionTypes[transaction.transaction_type as keyof typeof transactionTypes];
                const TypeIcon = typeInfo?.icon || Coins;
                const isPositive = transaction.amount > 0;

                return (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-6 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <div className={`p-3 rounded-full ${
                        isPositive ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                      }`}>
                        <TypeIcon className="w-5 h-5" />
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-semibold text-foreground">
                            {transaction.description || "Credits Transaction"}
                          </h3>
                          <Badge className={typeInfo?.color}>
                            {typeInfo?.label || transaction.transaction_type}
                          </Badge>
                        </div>

                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <span>
                            {new Date(transaction.created_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                          {transaction.reference_id && (
                            <span>Ref: {transaction.reference_id}</span>
                          )}
                          {transaction.reference_type && (
                            <span>• {transaction.reference_type}</span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className={`text-xl font-bold ${
                        isPositive ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {isPositive ? '+' : ''}{transaction.amount.toLocaleString()}
                      </div>
                      <div className="text-sm text-muted-foreground">
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

      {/* PAGINATION INFO */}
      {filteredTransactions.length > 0 && (
        <div className="text-center text-sm text-muted-foreground">
          Showing {filteredTransactions.length} of {transactions.length} transactions
        </div>
      )}
    </div>
  );
}
