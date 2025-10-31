// AUTH DOMAIN HOOKS
import { useState, useCallback } from 'react';
import { authService } from '@/lib/api/services';
import type { LoginRequest, RegisterRequest, User } from '@/types/domains';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  const signIn = useCallback(async (credentials: LoginRequest): Promise<boolean> => {
    try {
      setLoading(true);
      const response = await authService.login(credentials);
      
      localStorage.setItem('access_token', response.access_token);
      setUser(response.user);
      
      return true;
    } catch (error) {
      console.error('Sign in error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const signUp = useCallback(async (userData: RegisterRequest): Promise<boolean> => {
    try {
      setLoading(true);
      const response = await authService.register(userData);
      
      localStorage.setItem('access_token', response.access_token);
      setUser(response.user);
      
      return true;
    } catch (error) {
      console.error('Sign up error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const signOut = useCallback(async (): Promise<void> => {
    localStorage.removeItem('access_token');
    setUser(null);
  }, []);

  const updateProfile = useCallback(async (updates: Partial<User>): Promise<void> => {
    try {
      const updatedUser = await authService.updateProfile(updates);
      setUser(updatedUser);
    } catch (error) {
      console.error('Update profile error:', error);
      throw error;
    }
  }, []);

  return {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.is_admin || false,
    signIn,
    signUp,
    signOut,
    updateProfile,
  };
}
