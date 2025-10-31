"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

interface User {
  id: string;
  email: string;
  name?: string;
  username?: string;
  avatar?: string;
  is_active?: boolean;
  is_admin?: boolean;
  created_at?: string;
  last_login?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  signIn: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signUp: (email: string, password: string, name?: string) => Promise<{ success: boolean; error?: string }>;
  signOut: () => Promise<void>;
  updateProfile: (updates: Partial<User>) => Promise<void>;
  loginWithGoogle: () => Promise<boolean>;
  loginWithGithub: () => Promise<boolean>;
  refreshAccessToken: () => Promise<boolean>;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

import { getBackendUrl } from '@/lib/config';

// Use Next.js API routes instead of direct backend calls
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Memoize setUser to ensure stable reference
  const setUser = useCallback((user: User | null) => {
    setUserState(user);
  }, []);

  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');
        
        // Only proceed if we have a token
        if (token) {
          let response: Response;
          try {
            response = await fetch(`${API_BASE_URL}/auth/me`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            });
          } catch (error) {
            console.error('Network error checking auth state:', error);
            // Clear invalid token on network error
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            setUserState(null);
            return;
          }
          
          if (response.ok) {
            const userData = await response.json();
            setUserState(userData);
            localStorage.setItem('user', JSON.stringify(userData));
            
            // Log user ID to console when user state is verified with server
            console.log('🔄 Auth State Verified (from server)');
            console.log('👤 User ID:', userData.id);
            console.log('📧 User Email:', userData.email);
            console.log('👨‍💼 User Name:', userData.name);
          } else if (response.status === 401 && refreshToken) {
            // Try to refresh the token
            console.log('🔄 Access token expired, attempting refresh...');
            try {
              const refreshSuccess = await refreshAccessToken();
              if (refreshSuccess) {
                // Retry the auth check with new token
                return checkAuthState();
              } else {
                // Refresh failed, clear everything
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                setUserState(null);
              }
            } catch (refreshError) {
              console.log('Token refresh failed, clearing auth state');
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
              localStorage.removeItem('user');
              setUserState(null);
            }
          } else {
            // Token is invalid and no refresh token, clear everything
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            setUserState(null);
          }
        } else {
          // No token, ensure user state is null
          setUserState(null);
        }
      }
    } catch (error) {
      console.error('Error checking auth state:', error);
      // On error, clear everything to be safe
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      }
      setUserState(null);
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    setLoading(true);
    try {
      console.log('🔐 Attempting login for:', email);
      console.log('📡 API Base URL:', API_BASE_URL);
      console.log('📡 Email provided:', !!email, 'Password provided:', !!password);
      
      const requestBody = { email, password };
      const requestBodyString = JSON.stringify(requestBody);
      console.log('📡 Request body string:', requestBodyString);
      console.log('📡 Request body length:', requestBodyString.length);
      
      let response: Response;
      try {
        const url = `${API_BASE_URL}/auth/login`;
        console.log('📡 Full request URL:', url);
        
        response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: requestBodyString,
        });
        console.log('📡 Login response status:', response.status);
      } catch (error) {
        console.error('Network error during sign in:', error);
        return { success: false, error: 'Network error: Unable to connect to authentication server' };
      }

      if (response.ok) {
        const data = await response.json();
        if (!data.access_token) {
          console.error('Login response missing access_token:', data);
          return { success: false, error: 'Server error: Invalid response format' };
        }
        
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }
        
        // Get user data
        let userResponse: Response;
        try {
          userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${data.access_token}`,
              'Content-Type': 'application/json',
            },
          });
        } catch (error) {
          console.error('Network error fetching user data:', error);
          return { success: false, error: 'Network error: Unable to fetch user data' };
        }
        
        if (userResponse.ok) {
          const userData = await userResponse.json();
          setUser(userData);
          localStorage.setItem('user', JSON.stringify(userData));
          
          console.log('🔐 Login Successful!');
          console.log('👤 User ID:', userData.id);
          console.log('📧 User Email:', userData.email);
          console.log('👨‍💼 User Name:', userData.name);
          
          return { success: true };
        } else {
          const errorText = await userResponse.text();
          console.error('Failed to fetch user data. Status:', userResponse.status, 'Response:', errorText);
          let errorData;
          try {
            errorData = JSON.parse(errorText);
          } catch {
            errorData = { detail: 'Failed to fetch user data' };
          }
          return { success: false, error: errorData.detail || 'Failed to fetch user data' };
        }
      } else {
        const errorText = await response.text();
        console.error('Login failed. Status:', response.status, 'Response:', errorText);
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { detail: 'Invalid email or password' };
        }
        return { success: false, error: errorData.detail || errorData.message || 'Invalid email or password' };
      }
    } catch (error) {
      console.error('Sign in error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'An unexpected error occurred' };
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (email: string, password: string, name?: string): Promise<{ success: boolean; error?: string }> => {
    setLoading(true);
    try {
      let response: Response;
      try {
        response = await fetch(`${API_BASE_URL}/auth/register`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password, name }),
        });
      } catch (error) {
        console.error('Network error during sign up:', error);
        return { success: false, error: 'Network error: Unable to connect to authentication server' };
      }

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Log user ID to console after successful signup
        console.log('📝 Signup Successful!');
        console.log('👤 User ID:', userData.id);
        console.log('📧 User Email:', userData.email);
        console.log('👨‍💼 User Name:', userData.name);
        
        return { success: true };
      } else {
        // Handle error response
        const errorData = await response.json().catch(() => ({ detail: 'Registration failed' }));
        return { success: false, error: errorData.detail || 'Registration failed' };
      }
    } catch (error) {
      console.error('Sign up error:', error);
      return { success: false, error: 'An unexpected error occurred during registration' };
    } finally {
      setLoading(false);
    }
  };

  const refreshAccessToken = async (): Promise<boolean> => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        if (data.refresh_token) {
          localStorage.setItem('refresh_token', data.refresh_token);
        }
        return true;
      } else {
        // Refresh token is invalid, clear everything
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        setUserState(null);
        return false;
      }
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  };

  const signOut = async () => {
    setLoading(true);
    try {
      setUser(null);

      // Remove from localStorage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('user');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    } catch (error) {
      console.error('Sign out error:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (updates: Partial<User>) => {
    if (!user) return;

    try {
      const updatedUser = { ...user, ...updates };
      setUserState(updatedUser);

      // Update localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('user', JSON.stringify(updatedUser));
      }
    } catch (error) {
      console.error('Update profile error:', error);
    }
  };

  const loginWithGoogle = async (): Promise<boolean> => {
    try {
      setLoading(true);
      
      let response: Response;
      try {
        response = await fetch(`${API_BASE_URL}/auth/google`);
      } catch (error) {
        console.error('Failed to fetch Google OAuth URL - network error or invalid URL');
        throw new Error('Network error: Unable to connect to authentication server');
      }
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.data?.auth_url) {
        window.location.href = result.data.auth_url;
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Google login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const loginWithGithub = async (): Promise<boolean> => {
    try {
      setLoading(true);
      
      let response: Response;
      try {
        response = await fetch(`${API_BASE_URL}/auth/github`);
      } catch (error) {
        console.error('Failed to fetch GitHub OAuth URL - network error or invalid URL');
        throw new Error('Network error: Unable to connect to authentication server');
      }
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.data?.auth_url) {
        window.location.href = result.data.auth_url;
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('GitHub login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: !!(user && user.is_admin),
    signIn,
    signUp,
    signOut,
    updateProfile,
    loginWithGoogle,
    loginWithGithub,
    refreshAccessToken,
    setUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
