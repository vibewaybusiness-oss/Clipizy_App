export interface ProfileSettings {
  name: string;
  email: string;
  bio: string;
  website: string;
  location: string;
}

export interface NotificationSettings {
  emailNotifications: boolean;
  pushNotifications: boolean;
  marketingEmails: boolean;
  weeklyDigest: boolean;
  projectUpdates: boolean;
}

export interface PrivacySettings {
  profileVisibility: "public" | "private";
  showEmail: boolean;
  allowComments: boolean;
  dataSharing: boolean;
  analyticsTracking: boolean;
  marketingEmails: boolean;
  profileDiscovery: boolean;
  activityVisibility: "public" | "followers" | "private";
}

export interface SecuritySettings {
  twoFactorEnabled: boolean;
  loginNotifications: boolean;
  sessionTimeout: number;
  apiAccess: boolean;
  dataExport: boolean;
  accountDeletion: boolean;
}

export interface PreferencesSettings {
  theme: "light" | "dark" | "system";
  language: string;
  timezone: string;
  autoSave: boolean;
  highQuality: boolean;
}

export interface BillingSettings {
  plan: string;
  payment_methods: any[];
  billing_address: any;
  next_billing_date: string | null;
  subscription_status: string;
}

export interface UserSettings {
  profile: ProfileSettings;
  notifications: NotificationSettings;
  privacy: PrivacySettings;
  security: SecuritySettings;
  preferences: PreferencesSettings;
  billing: BillingSettings;
  updated_at?: string;
}

export interface CreditsBalance {
  current_balance: number;
  total_earned: number;
  total_spent: number;
}

export interface CreditsTransaction {
  id: string;
  amount: number;
  type: "earned" | "spent" | "purchased";
  description: string;
  created_at: string;
  balance_after: number;
}

export interface Payment {
  id: string;
  amount_cents: number;
  status: string;
  description: string;
  created_at: string;
  credits_purchased: number;
}
