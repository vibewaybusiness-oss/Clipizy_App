"use client";

import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/ui/use-toast";
import { Coins, User, Plus, Search } from "lucide-react";

interface UserCreditsInfo {
  user_email: string;
  user_id: string;
  balance_info: {
    current_balance: number;
    total_earned: number;
    total_spent: number;
  };
}

export default function AdminCreditsAdjustment() {
  const [userId, setUserId] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [userInfo, setUserInfo] = useState<UserCreditsInfo | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const { toast } = useToast();

  const searchUser = async () => {
    if (!userId.trim()) {
      toast({
        title: "Error",
        description: "Please enter a user ID",
        variant: "destructive",
      });
      return;
    }

    setSearchLoading(true);
    try {
      const response = await fetch(`/api/v1/admin/users/${userId.trim()}/credits`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error("User not found");
        }
        throw new Error("Failed to fetch user information");
      }

      const data = await response.json();
      setUserInfo(data);
      
      toast({
        title: "User Found",
        description: `Found user: ${data.user_email}`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to search user",
        variant: "destructive",
      });
      setUserInfo(null);
    } finally {
      setSearchLoading(false);
    }
  };

  const addCredits = async () => {
    if (!userId.trim() || !amount.trim()) {
      toast({
        title: "Error",
        description: "Please enter both user ID and amount",
        variant: "destructive",
      });
      return;
    }

    const creditsAmount = parseInt(amount);
    if (isNaN(creditsAmount) || creditsAmount <= 0) {
      toast({
        title: "Error",
        description: "Please enter a valid positive number for credits",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/v1/admin/credits/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId.trim(),
          amount: creditsAmount,
          description: description.trim() || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to add credits");
      }

      const data = await response.json();
      
      toast({
        title: "Success",
        description: data.message,
      });

      // Refresh user info
      if (userInfo) {
        await searchUser();
      }

      // Clear form
      setAmount("");
      setDescription("");
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add credits",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Coins className="w-5 h-5" />
          Admin Credits Adjustment
        </CardTitle>
        <CardDescription>
          Add credits to a specific user account by entering their user ID
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* User Search Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4" />
            <Label htmlFor="userId">User ID</Label>
          </div>
          <div className="flex gap-2">
            <Input
              id="userId"
              placeholder="Enter user ID (UUID)"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="flex-1"
            />
            <Button 
              onClick={searchUser} 
              disabled={searchLoading || !userId.trim()}
              variant="outline"
            >
              <Search className={`w-4 h-4 ${searchLoading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        {/* User Info Display */}
        {userInfo && (
          <div className="p-4 bg-muted rounded-lg space-y-2">
            <h4 className="font-semibold">User Information</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Email:</span>
                <p className="font-medium">{userInfo.user_email}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Current Balance:</span>
                <p className="font-medium text-green-600">{userInfo.balance_info.current_balance} credits</p>
              </div>
              <div>
                <span className="text-muted-foreground">Total Earned:</span>
                <p className="font-medium">{userInfo.balance_info.total_earned} credits</p>
              </div>
            </div>
          </div>
        )}

        {/* Credits Addition Section */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            <Label htmlFor="amount">Credits to Add</Label>
          </div>
          <Input
            id="amount"
            type="number"
            placeholder="Enter number of credits to add"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            min="1"
          />
        </div>

        {/* Description Section */}
        <div className="space-y-4">
          <Label htmlFor="description">Description (Optional)</Label>
          <Textarea
            id="description"
            placeholder="Enter a description for this credit adjustment..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
          />
        </div>

        {/* Action Button */}
        <Button 
          onClick={addCredits} 
          disabled={loading || !userId.trim() || !amount.trim()}
          className="w-full"
        >
          {loading ? "Adding Credits..." : "Add Credits"}
        </Button>
      </CardContent>
    </Card>
  );
}


