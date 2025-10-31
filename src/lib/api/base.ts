/**
 * Base API Client with consistent patterns for all services
 */
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: Response,
    public errorData?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export abstract class BaseApiClient {
  protected baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  protected getAuthHeaders(): HeadersInit {
    // First try localStorage, then fallback to environment variable
    const localStorageToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    const envToken = process.env.NEXT_PUBLIC_AUTH_TOKEN;
    const token = localStorageToken || envToken;
    
    const headers: HeadersInit = {};

    console.log('🔐 === AUTH HEADERS DEBUG ===');
    console.log('🔐 Auth headers check:', {
      hasLocalStorageToken: !!localStorageToken,
      hasEnvToken: !!envToken,
      hasToken: !!token,
      tokenLength: token ? token.length : 0,
      isExpired: token ? this.isTokenExpired(token) : false,
      tokenPreview: token ? token.substring(0, 20) + '...' : 'null',
      tokenSource: localStorageToken ? 'localStorage' : envToken ? 'environment' : 'none'
    });

    if (token) {
      // Check if token is expired
      if (this.isTokenExpired(token)) {
        console.log('❌ Token is expired, redirecting to login');
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          window.location.href = '/auth/login';
        }
        console.log('🔐 === AUTH HEADERS DEBUG END (EXPIRED) ===');
        return headers;
      }
      headers['Authorization'] = `Bearer ${token}`;
      console.log('✅ Authorization header set successfully');
      console.log('🔐 Authorization header value:', `Bearer ${token.substring(0, 20)}...`);
    } else {
      console.log('❌ No token found in localStorage or environment variables');
    }

    console.log('🔐 Final headers:', headers);
    console.log('🔐 === AUTH HEADERS DEBUG END ===');
    return headers;
  }

  private isTokenExpired(token: string): boolean {
    try {
      // Check if it's a JWT token (has 3 parts separated by dots)
      if (token.split('.').length === 3) {
        // JWT token - decode the payload (second part)
        const payload = JSON.parse(atob(token.split('.')[1]));
        const exp = payload.exp * 1000; // Convert to milliseconds
        return Date.now() >= exp;
      } else {
        // Legacy simple base64-encoded JSON object
        const payload = JSON.parse(atob(token));
        const exp = payload.exp * 1000; // Convert to milliseconds
        return Date.now() >= exp;
      }
    } catch {
      return true; // If we can't parse the token, consider it expired
    }
  }

  protected async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Set appropriate Content-Type based on request body
    const headers: HeadersInit = {
      ...this.getAuthHeaders(),
      ...options.headers,
    };
    
    // Only set Content-Type if not already set and body is not FormData
    if (!(headers as any)['Content-Type'] && !(options.body instanceof FormData)) {
      (headers as any)['Content-Type'] = 'application/json';
    }
    
    console.log('🌐 === API REQUEST DEBUG ===');
    console.log('🌐 API Request:', {
      url,
      method: options.method || 'GET',
      bodyType: options.body ? options.body.constructor.name : 'undefined',
      bodySize: options.body instanceof FormData ? '[FormData]' : 
                (typeof options.body === 'string' ? options.body.length + ' chars' : 
                (options.body ? '[Object]' : 'undefined'))
    });
    
    // Let the backend handle authentication instead of blocking requests here
    
    let response: Response;
    try {
      console.log('🌐 Making fetch request...');
      response = await fetch(url, {
        ...options,
        headers,
      });
      console.log('🌐 Fetch response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries())
      });
      
      // Log response body for debugging (but don't consume it yet)
      if (!response.ok) {
        console.error('❌ Response not OK:', {
          status: response.status,
          statusText: response.statusText,
          url: response.url
        });
      }
    } catch (error) {
      // Handle network errors (connection refused, timeout, etc.)
      console.error('❌ === NETWORK ERROR DEBUG ===');
      console.error('❌ Network error during fetch:', error);
      console.error('❌ Error type:', typeof error);
      console.error('❌ Error name:', error.name);
      console.error('❌ Error message:', error.message);
      console.error('❌ Request URL:', url);
      console.error('❌ Request options:', { ...options, headers });
      console.error('❌ === NETWORK ERROR DEBUG END ===');
      
      // For music-clip endpoints, surface the error but do not throw to keep UI usable
      if (endpoint.includes('/music-clip/')) {
        throw new ApiError(
          `Network error: ${error instanceof Error ? error.message : 'Unknown network error'}`,
          0
        );
      }
      
      // Check if we're on the music-clip page and return a mock response
      const isClientSide = typeof window !== 'undefined';
      if (isClientSide) {
        const currentPath = window.location.pathname;
        const urlParams = new URLSearchParams(window.location.search);
        const projectId = urlParams.get('projectId');
        
        if (currentPath.includes('/music-clip') && projectId) {
          console.log('Network error on music-clip page - using fallback data for visualization');
          return { success: false, error: 'Network error' } as T;
        }
      }
      
      // For other cases, throw a more descriptive error
      throw new ApiError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown network error'}`,
        0
      );
    }

    // If we get a 401/403, try to refresh the token
    if ((response.status === 401 || response.status === 403) && this.shouldRefreshToken()) {
      const refreshed = await this.refreshToken();
      if (refreshed) {
        // Retry the request with the new token
        const newHeaders: HeadersInit = {
          ...this.getAuthHeaders(),
          ...options.headers,
        };
        
        if (!(newHeaders as any)['Content-Type'] && !(options.body instanceof FormData)) {
          (newHeaders as any)['Content-Type'] = 'application/json';
        }
        
        try {
          response = await fetch(url, {
            ...options,
            headers: newHeaders,
          });
        } catch (error) {
          // Handle network errors during retry
          console.warn('Network error during retry fetch:', error);
          console.warn('Retry request URL:', url);
          console.warn('Retry request options:', { ...options, headers: newHeaders });
          
          if (endpoint.includes('/music-clip/')) {
            throw new ApiError(
              `Network error during retry: ${error instanceof Error ? error.message : 'Unknown network error'}`,
              0
            );
          }
          
          // Check if we're on the music-clip page and return a mock response
          const isClientSide = typeof window !== 'undefined';
          if (isClientSide) {
            const currentPath = window.location.pathname;
            const urlParams = new URLSearchParams(window.location.search);
            const projectId = urlParams.get('projectId');
            
            if (currentPath.includes('/music-clip') && projectId) {
              console.log('Network error during retry on music-clip page - returning mock response');
              return { success: false, error: 'Network error' } as T;
            }
          }
          
          // For other cases, throw a more descriptive error
          throw new ApiError(
            `Network error during retry: ${error instanceof Error ? error.message : 'Unknown network error'}`,
            0
          );
        }
      }
    }

    if (!response.ok) {
      // Handle 402 errors first, before consuming the response body
      if (response.status === 402) {
        let errorData = null;
        try {
          const responseText = await response.text();
          errorData = JSON.parse(responseText);
        } catch (parseError) {
          console.warn('Failed to parse 402 error response:', parseError);
        }
        throw new ApiError('Payment Required', response.status, response, errorData);
      }

      let errorMessage = `Request failed: ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If JSON parsing fails, use the default error message
      }
      
      // Handle authentication errors
      if (response.status === 401 || response.status === 403) {
        console.log('Authentication error detected:', response.status, 'URL:', response.url);
        console.log('Current path:', typeof window !== 'undefined' ? window.location.pathname : 'server-side');
        
        // Clear invalid token
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          
          // Don't redirect if we're on the music-clip page with a projectId
          const currentPath = window.location.pathname;
          const urlParams = new URLSearchParams(window.location.search);
          const projectId = urlParams.get('projectId');
          
          console.log('Client-side auth error - currentPath:', currentPath, 'projectId:', projectId);
          
          if (currentPath.includes('/music-clip') && projectId) {
            console.log('Authentication error on music-clip page - not redirecting to login');
            // Just log the error but don't redirect or throw
            throw new ApiError('Authentication required', response.status, response);
          }
          
          console.log('Redirecting to login page');
          // Redirect to login page for other pages
          window.location.href = '/auth/login';
        }
      }
      
      // Only throw the error if we're not on the music-clip page
      if (response.status !== 401 && response.status !== 403) {
        throw new ApiError(errorMessage, response.status, response);
      } else {
        // For auth errors, check if we're on the music-clip page (client-side) or in auto-save route (server-side)
        const isClientSide = typeof window !== 'undefined';
        const isServerSide = !isClientSide;
        
        let shouldReturnMockResponse = false;
        
        if (isClientSide) {
          // Client-side: check URL
          const currentPath = window.location.pathname;
          const urlParams = new URLSearchParams(window.location.search);
          const projectId = urlParams.get('projectId');
          
          if (currentPath.includes('/music-clip') && projectId) {
            shouldReturnMockResponse = true;
          }
        } else if (isServerSide) {
          // Server-side: check if we're in the auto-save route by looking at the stack trace
          const stack = new Error().stack || '';
          if (stack.includes('auto-save') || stack.includes('music-clip')) {
            shouldReturnMockResponse = true;
          }
        }
        
        if (shouldReturnMockResponse) {
          console.log('Returning mock response for auth error on music-clip page/route');
          console.log('Stack trace:', new Error().stack);
          return { success: false, error: 'Authentication error' } as T;
        }
        
        throw new ApiError(errorMessage, response.status, response);
      }
    }

    return response.json();
  }

  private shouldRefreshToken(): boolean {
    return typeof window !== 'undefined' && !!localStorage.getItem('refresh_token');
  }

  private async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) return false;

      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        return true;
      } else {
        // Refresh token is invalid, clear everything
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        return false;
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  }

  public async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  private safeStringify(obj: any): string {
    try {
      const seen = new WeakSet();
      return JSON.stringify(obj, (key, value) => {
        if (typeof value === 'object' && value !== null) {
          if (seen.has(value)) {
            return '[Circular]';
          }
          seen.add(value);
        }
        return value;
      });
    } catch (e) {
      console.error('JSON stringify error:', e);
      throw new Error('Failed to serialize request body');
    }
  }

  public async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? (data instanceof FormData ? data : this.safeStringify(data)) : undefined,
    });
  }

  protected async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? (data instanceof FormData ? data : this.safeStringify(data)) : undefined,
    });
  }

  protected async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? (data instanceof FormData ? data : this.safeStringify(data)) : undefined,
    });
  }

  protected async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  protected async uploadFile<T>(
    endpoint: string, 
    file: File, 
    additionalData?: Record<string, any>
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    const headers: HeadersInit = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return this.request<T>(endpoint, {
      method: 'POST',
      headers,
      body: formData,
    });
  }
}
