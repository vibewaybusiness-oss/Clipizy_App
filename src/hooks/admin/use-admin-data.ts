import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from '@/contexts/auth-context';
import { useToast } from '@/hooks/ui/use-toast';
import { 
  fetchStripeData, 
  processStripeData, 
  calculateAdminStats,
  validateAdminAccess,
  clearCache,
  type StripeData,
  type AdminStats
} from '@/lib/admin-utils';

// =========================
// ADMIN DATA HOOK
// =========================

export interface UseAdminDataOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  onError?: (error: Error) => void;
}

export function useAdminData(options: UseAdminDataOptions = {}) {
  const { autoRefresh = false, refreshInterval = 300000, onError } = options; // 5 minutes default
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [data, setData] = useState<StripeData | null>(null);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Check admin access
  const hasAdminAccess = useMemo(() => {
    return validateAdminAccess(user);
  }, [user]);

  const fetchData = useCallback(async () => {
    if (!hasAdminAccess) {
      setError('Access denied: Admin privileges required');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const stripeData = await fetchStripeData();
      const adminStats = calculateAdminStats(stripeData);
      
      setData(stripeData);
      setStats(adminStats);
      setLastUpdated(new Date());
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch admin data';
      setError(errorMessage);
      onError?.(err instanceof Error ? err : new Error(errorMessage));
      
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  }, [hasAdminAccess, onError, toast]);

  const refreshData = useCallback(() => {
    clearCache('stripe-data');
    fetchData();
  }, [fetchData]);

  // Auto-refresh effect
  useEffect(() => {
    if (autoRefresh && hasAdminAccess) {
      const interval = setInterval(fetchData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, fetchData, hasAdminAccess]);

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    stats,
    loading,
    error,
    lastUpdated,
    hasAdminAccess,
    refreshData,
    fetchData
  };
}

// =========================
// ADMIN FILTERS HOOK
// =========================

export interface AdminFilters {
  search: string;
  status: string;
  type: string;
}

export function useAdminFilters(initialFilters: Partial<AdminFilters> = {}) {
  const [filters, setFilters] = useState<AdminFilters>({
    search: '',
    status: 'all',
    type: 'all',
    ...initialFilters
  });

  const updateFilter = useCallback((key: keyof AdminFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      search: '',
      status: 'all',
      type: 'all'
    });
  }, []);

  const hasActiveFilters = useMemo(() => {
    return filters.search !== '' || filters.status !== 'all' || filters.type !== 'all';
  }, [filters]);

  return {
    filters,
    updateFilter,
    clearFilters,
    hasActiveFilters
  };
}

// =========================
// ADMIN ACTIONS HOOK
// =========================

export function useAdminActions() {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const copyToClipboard = useCallback(async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copied",
        description: `${label} copied to clipboard`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to copy to clipboard",
        variant: "destructive"
      });
    }
  }, [toast]);

  const exportData = useCallback(async (data: any, filename: string) => {
    try {
      setIsLoading(true);
      
      const jsonString = JSON.stringify(data, null, 2);
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      if (typeof document !== 'undefined') {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
      
      URL.revokeObjectURL(url);
      
      toast({
        title: "Export Complete",
        description: `${filename} has been downloaded`,
      });
    } catch (error) {
      toast({
        title: "Export Failed",
        description: "Failed to export data",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  const deleteItem = useCallback(async (id: string, type: string) => {
    try {
      setIsLoading(true);
      
      // Mock delete - replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast({
        title: "Deleted",
        description: `${type} deleted successfully`,
      });
      
      return true;
    } catch (error) {
      toast({
        title: "Delete Failed",
        description: `Failed to delete ${type}`,
        variant: "destructive"
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  return {
    isLoading,
    copyToClipboard,
    exportData,
    deleteItem
  };
}

// =========================
// ADMIN STATS HOOK
// =========================

export function useAdminStats() {
  const { data, loading, error } = useAdminData();
  
  const stats = useMemo(() => {
    if (!data) return null;
    
    return {
      totalProducts: data.products.length,
      activeProducts: data.products.filter(p => p.active).length,
      totalPrices: data.prices.length,
      activePrices: data.prices.filter(p => p.active).length,
      totalPaymentLinks: data.paymentLinks.length,
      activePaymentLinks: data.paymentLinks.filter(p => p.active).length,
      totalCustomers: data.customers.length,
      activeCustomers: data.customers.filter(c => 
        c.subscriptions?.data.some(s => s.status === 'active')
      ).length
    };
  }, [data]);

  return {
    stats,
    loading,
    error
  };
}
