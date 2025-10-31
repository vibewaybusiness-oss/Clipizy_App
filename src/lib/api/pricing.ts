import { BaseApiClient } from './base';
import { z } from "zod";
import { PricingConfig } from "@/contexts/pricing-context";
import { getBackendUrl } from '@/lib/config';
import { API_PATHS } from './config';

export interface PriceResult {
  usd: number;
  credits: number;
}

export interface CreditsBalance {
  current_balance: number;
  total_earned: number;
  total_spent: number;
  recent_transactions: CreditsTransaction[];
}

export interface CreditsTransaction {
  id: string;
  user_id: string;
  transaction_type: 'earned' | 'spent' | 'purchased' | 'refunded' | 'bonus' | 'admin_adjustment';
  amount: number;
  balance_after: number;
  description?: string;
  reference_id?: string;
  reference_type?: string;
  created_at: string;
}

export interface CreditsSpendRequest {
  amount: number;
  description: string;
  reference_id?: string;
  reference_type?: string;
}

export interface CreditsPurchaseRequest {
  amount_dollars: number;
  payment_method_id?: string;
}

export interface PaymentIntentResponse {
  client_secret: string;
  payment_intent_id: string;
  amount_cents: number;
  credits_purchased: number;
  status: string;
}

export class PricingService extends BaseApiClient {
  private static instance: PricingService;
  private config: PricingConfig | null = null;
  private configPromise: Promise<PricingConfig> | null = null;

  constructor() {
    super(getBackendUrl());
  }

  public static getInstance(): PricingService {
    if (!PricingService.instance) {
      PricingService.instance = new PricingService();
    }
    return PricingService.instance;
  }

  // PRICING CONFIGURATION
  setConfig(config: PricingConfig) {
    this.config = config;
  }

  async getConfig(): Promise<PricingConfig> {
    if (this.config) {
      return this.config;
    }

    if (this.configPromise) {
      return this.configPromise;
    }

    this.configPromise = this.fetchConfig();
    try {
      return await this.configPromise;
    } catch (error) {
      console.warn('Using fallback pricing config due to API error');
      return this.getFallbackConfig();
    }
  }

  private getFallbackConfig(): PricingConfig {
    return {
      credits_rate: 20,
      music_generator: {
        "stable-audio": {
          price: 0.5,
          description: "Generate a music track based on the description."
        },
        "clipizy-model": {
          price: 1.0,
          description: "Generate a music track based on the description."
        }
      },
      image_generator: {
        "clipizy-model": {
          minute_rate: 0.10,
          unit_rate: 0.50,
          min: 3,
          max: null,
          description: "Generate an image based on the description."
        }
      },
      looped_animation_generator: {
        "clipizy-model": {
          minute_rate: 0.11,
          unit_rate: 1,
          min: 3,
          max: null,
          description: "Generate a looping animation based on the description."
        }
      },
      recurring_scenes_generator: {
        "clipizy-model": {
          minute_rate: 0.15,
          unit_rate: 1.5,
          min: 5,
          max: null,
          description: "Generate recurring scenes that repeat throughout the video."
        }
      },
      video_generator: {
        "clipizy-model": {
          "video-duration": 5,
          minute_rate: 1.0,
          min: 5,
          max: null,
          description: "Generate a video based on the description."
        }
      }
    };
  }

  private async fetchConfig(): Promise<PricingConfig> {
    try {
      const config = await this.get<PricingConfig>('/api/credits/pricing/config');
      this.config = config;
      return config;
    } catch (error) {
      console.warn('Error fetching pricing config, using fallback:', error);
      const fallbackConfig = this.getFallbackConfig();
      this.config = fallbackConfig;
      return fallbackConfig;
    }
  }

  // CREDITS MANAGEMENT
  async getBalance(): Promise<CreditsBalance> {
    try {
      return await this.get<CreditsBalance>(API_PATHS.CREDITS.BALANCE);
    } catch (error) {
      console.error('Error fetching credits balance:', error);
      throw error;
    }
  }

  async getTransactions(limit: number = 50): Promise<CreditsTransaction[]> {
    try {
      return await this.get<CreditsTransaction[]>(`${API_PATHS.CREDITS.TRANSACTIONS}?limit=${limit}`);
    } catch (error) {
      console.error('Error fetching transactions:', error);
      throw error;
    }
  }

  async spendCredits(spendRequest: CreditsSpendRequest): Promise<{ message: string; transaction_id: string; new_balance: number }> {
    try {
      return await this.post<{ message: string; transaction_id: string; new_balance: number }>(API_PATHS.CREDITS.SPEND, spendRequest);
    } catch (error) {
      console.error('Error spending credits:', error);
      throw error;
    }
  }

  async purchaseCredits(purchaseRequest: CreditsPurchaseRequest): Promise<PaymentIntentResponse> {
    try {
      return await this.post<PaymentIntentResponse>(API_PATHS.CREDITS.PURCHASE, purchaseRequest);
    } catch (error) {
      console.error('Error purchasing credits:', error);
      throw error;
    }
  }

  async canAfford(amount: number): Promise<{ can_afford: boolean; amount_requested: number; current_balance: number }> {
    try {
      return await this.get<{ can_afford: boolean; amount_requested: number; current_balance: number }>(API_PATHS.CREDITS.CAN_AFFORD(amount));
    } catch (error) {
      console.error('Error checking affordability:', error);
      throw error;
    }
  }

  // PRICING CALCULATIONS - Call business APIs directly
  async calculateMusicPrice(numTracks: number, model: 'stable-audio' | 'clipizy-model' = 'stable-audio'): Promise<PriceResult> {
    return await this.get<PriceResult>(`${API_PATHS.CREDITS.PRICING.MUSIC}?num_tracks=${numTracks}`);
  }

  async calculateImagePrice(numUnits: number, totalMinutes: number, model: 'clipizy-model' = 'clipizy-model'): Promise<PriceResult> {
    return await this.get<PriceResult>(`${API_PATHS.CREDITS.PRICING.IMAGE}?num_units=${numUnits}&total_minutes=${totalMinutes}`);
  }

  async calculateLoopedAnimationPrice(numUnits: number, totalMinutes: number, model: 'clipizy-model' = 'clipizy-model'): Promise<PriceResult> {
    return await this.get<PriceResult>(`${API_PATHS.CREDITS.PRICING.LOOPED_ANIMATION}?num_units=${numUnits}&total_minutes=${totalMinutes}`);
  }

  async calculateRecurringScenesPrice(numUnits: number, totalMinutes: number, model: 'clipizy-model' = 'clipizy-model'): Promise<PriceResult> {
    return await this.get<PriceResult>(`${API_PATHS.CREDITS.PRICING.RECURRING_SCENES}?num_units=${numUnits}&total_minutes=${totalMinutes}`);
  }

  async calculateVideoPrice(durationMinutes: number, model: 'clipizy-model' = 'clipizy-model'): Promise<PriceResult> {
    return await this.get<PriceResult>(`${API_PATHS.CREDITS.PRICING.VIDEO}?duration_minutes=${durationMinutes}`);
  }

  async calculateBudget(settings: {
    videoType: string;
    trackCount: number;
    trackDurations: number[];
    reuse_content: boolean; // CHANGED: was useSameVideoForAll
    model?: string;
  }): Promise<{
    price: PriceResult;
    video_type: string;
    units?: number;
    scenes_info?: {
      total_scenes: number;
      videos_to_create: number;
      max_scenes_per_video: number;
      min_scenes_per_video: number;
      cost_per_scene: number;
    };
    reuse_video: boolean;
    total_minutes: number;
    longest_track_minutes: number;
  }> {
    const requestData = {
      video_type: settings.videoType,
      track_count: settings.trackCount,
      total_duration: settings.trackDurations.reduce((sum, duration) => sum + duration, 0),
      track_durations: settings.trackDurations,
      reuse_video: settings.reuse_content // CHANGED: was useSameVideoForAll
    };
    
    const response = await this.post<any>(API_PATHS.CREDITS.PRICING.CALCULATE_BUDGET, requestData);
    
    // Handle wrapped response format from backend
    if (response.data) {
      return response.data;
    } else {
      return response;
    }
  }

}

export const pricingService = PricingService.getInstance();
