import { BaseApiClient } from './base';
import { API_BASE_URL, API_PATHS } from './config';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

class AuthService extends BaseApiClient {
  constructor() {
    super(API_BASE_URL);
  }

  public async login(credentials: LoginRequest): Promise<LoginResponse> {
    return this.post<LoginResponse>(API_PATHS.AUTH.LOGIN, credentials);
  }

  public async register(userData: RegisterRequest): Promise<LoginResponse> {
    return this.post<LoginResponse>(API_PATHS.AUTH.REGISTER, userData);
  }

  private async refreshAuthToken(): Promise<boolean> {
    try {
      const response = await this.post<{ access_token: string }>(API_PATHS.AUTH.REFRESH);
      return !!response.access_token;
    } catch (error) {
      return false;
    }
  }

  public async logout(): Promise<void> {
    return this.post<void>(API_PATHS.AUTH.LOGOUT);
  }

  public async getProfile(): Promise<User> {
    return this.get<User>(API_PATHS.AUTH.PROFILE);
  }

  public async updateProfile(updates: Partial<User>): Promise<User> {
    return this.put<User>(API_PATHS.AUTH.PROFILE, updates);
  }

  public async googleLogin(): Promise<{ url: string }> {
    return this.get<{ url: string }>(API_PATHS.AUTH.GOOGLE_LOGIN);
  }

  public async googleCallback(code: string): Promise<LoginResponse> {
    return this.post<LoginResponse>(API_PATHS.AUTH.GOOGLE_CALLBACK, { code });
  }

  public async onboard(): Promise<{
    user_id: string;
    email: string;
    credits_balance: number;
    onboarded: boolean;
    s3_directory_created: boolean;
    needed_onboarding: boolean;
  }> {
    return this.post('/api/auth/onboard');
  }

  public async setupOnboarding(): Promise<{
    storage_created: boolean;
    user_id: string;
    email: string;
  }> {
    return this.post('/api/auth/onboarding/setup');
  }
}

export const authService = new AuthService();
