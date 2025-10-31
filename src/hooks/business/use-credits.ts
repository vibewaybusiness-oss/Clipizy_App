import { useState, useEffect, useCallback } from 'react';
import { pricingService, CreditsBalance, CreditsTransaction, CreditsSpendRequest, CreditsPurchaseRequest, PaymentIntentResponse } from '@/lib/api/pricing';
import { useToast } from '@/hooks/ui/use-toast';

export function useCredits() {
  const [balance, setBalance] = useState<CreditsBalance | null>(null);
  const [transactions, setTransactions] = useState<CreditsTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchBalance = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await pricingService.getBalance();
      setBalance(data);
    } catch (err: any) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch credits balance';
      setError(errorMessage);
      console.error('Error fetching credits balance:', err);
      
      // If it's an authentication error, redirect to login
      if (err?.status === 401 || err?.status === 403) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/auth/login';
        }
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchTransactions = useCallback(async (limit: number = 50) => {
    try {
      setError(null);
      
      const data = await pricingService.getTransactions(limit);
      setTransactions(data);
    } catch (err: any) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch transactions';
      setError(errorMessage);
      console.error('Error fetching transactions:', err);
      
      // If it's an authentication error, redirect to login
      if (err?.status === 401 || err?.status === 403) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/auth/login';
        }
      }
    }
  }, []);

  const spendCredits = useCallback(async (spendRequest: CreditsSpendRequest) => {
    try {
      setError(null);
      const result = await pricingService.spendCredits(spendRequest);

      // Refresh balance after spending
      await fetchBalance();

      toast({
        title: "Credits Spent",
        description: `Successfully spent ${spendRequest.amount} credits`,
      });

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to spend credits';
      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "Spend Failed",
        description: errorMessage,
      });
      throw err;
    }
  }, [fetchBalance, toast]);

  const purchaseCredits = useCallback(async (purchaseRequest: CreditsPurchaseRequest): Promise<PaymentIntentResponse> => {
    try {
      setError(null);
      const result = await pricingService.purchaseCredits(purchaseRequest);

      toast({
        title: "Payment Intent Created",
        description: "Please complete the payment to add credits to your account",
      });

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create payment intent';
      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "Purchase Failed",
        description: errorMessage,
      });
      throw err;
    }
  }, [toast]);

  const canAfford = useCallback(async (amount: number) => {
    try {
      const result = await pricingService.canAfford(amount);
      return result;
    } catch (err) {
      console.error('Error checking affordability:', err);
      return { can_afford: false, amount_requested: amount, current_balance: 0 };
    }
  }, []);

  // Load initial data
  useEffect(() => {
    fetchBalance();
    fetchTransactions();
  }, [fetchBalance, fetchTransactions]);

  return {
    balance,
    transactions,
    loading,
    error,
    fetchBalance,
    fetchTransactions,
    spendCredits,
    purchaseCredits,
    canAfford,
  };
}
