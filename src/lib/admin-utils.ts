// =========================
// ADMIN UTILITIES
// =========================

export interface AdminStats {
  totalUsers: number;
  activeUsers: number;
  totalProjects: number;
  totalRevenue: number;
  conversionRate: number;
}

export interface StripeData {
  products: StripeProduct[];
  prices: StripePrice[];
  paymentLinks: StripePaymentLink[];
  customers: StripeCustomer[];
}

export interface StripeProduct {
  id: string;
  name: string;
  description: string;
  active: boolean;
  created: number;
  default_price?: string;
}

export interface StripePrice {
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

export interface StripePaymentLink {
  id: string;
  url: string;
  active: boolean;
  created: number;
  line_items: Array<{
    price: string;
    quantity: number;
  }>;
}

export interface StripeCustomer {
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

// =========================
// ADMIN DATA PROCESSING
// =========================

export function processStripeData(rawData: any): StripeData {
  return {
    products: rawData.products || [],
    prices: rawData.prices || [],
    paymentLinks: rawData.paymentLinks || [],
    customers: rawData.customers || []
  };
}

export function calculateAdminStats(data: StripeData): AdminStats {
  const totalUsers = data.customers.length;
  const activeUsers = data.customers.filter(customer => 
    customer.subscriptions?.data.some(sub => sub.status === 'active')
  ).length;
  
  return {
    totalUsers,
    activeUsers,
    totalProjects: 0, // This would come from your projects API
    totalRevenue: 0, // This would come from your revenue API
    conversionRate: totalUsers > 0 ? (activeUsers / totalUsers) * 100 : 0
  };
}

// =========================
// ADMIN VALIDATION
// =========================

export function validateAdminAccess(user: any): boolean {
  // Add your admin validation logic here
  return user?.role === 'admin' || user?.isAdmin === true;
}

export function validateStripeData(data: any): boolean {
  return data && typeof data === 'object' && 
         Array.isArray(data.products) && 
         Array.isArray(data.prices);
}

// =========================
// ADMIN CACHING
// =========================

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
const cache = new Map<string, { data: any; timestamp: number }>();

export function getCachedData(key: string): any | null {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  return null;
}

export function setCachedData(key: string, data: any): void {
  cache.set(key, {
    data,
    timestamp: Date.now()
  });
}

export function clearCache(key?: string): void {
  if (key) {
    cache.delete(key);
  } else {
    cache.clear();
  }
}

// =========================
// ADMIN API UTILITIES
// =========================

export async function fetchStripeData(): Promise<StripeData> {
  const cacheKey = 'stripe-data';
  const cached = getCachedData(cacheKey);
  
  if (cached) {
    return cached;
  }

  try {
    // Mock data - replace with actual API call
    const mockData = {
      products: [
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
      ],
      prices: [
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
      ],
      paymentLinks: [
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
      ],
      customers: []
    };

    const processedData = processStripeData(mockData);
    setCachedData(cacheKey, processedData);
    return processedData;
  } catch (error) {
    console.error('Error fetching Stripe data:', error);
    throw error;
  }
}

// =========================
// ADMIN FORMATTING
// =========================

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount / 100); // Stripe amounts are in cents
}

export function formatDate(timestamp: number): string {
  return new Date(timestamp * 1000).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function formatStatus(status: string): string {
  return status.charAt(0).toUpperCase() + status.slice(1);
}

// =========================
// ADMIN FILTERING
// =========================

export function filterStripeData(data: StripeData, filters: {
  search?: string;
  status?: string;
  type?: string;
}): StripeData {
  const { search, status, type } = filters;
  
  let filteredData = { ...data };

  if (search) {
    const searchLower = search.toLowerCase();
    filteredData.products = filteredData.products.filter(product =>
      product.name.toLowerCase().includes(searchLower) ||
      product.description.toLowerCase().includes(searchLower)
    );
  }

  if (status) {
    filteredData.products = filteredData.products.filter(product =>
      product.active === (status === 'active')
    );
  }

  return filteredData;
}
