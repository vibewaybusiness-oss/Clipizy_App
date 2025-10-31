import { useState } from 'react';
import { useToast } from '@/hooks/ui/use-toast';

interface SubscriptionResponse {
  success: boolean;
  message?: string;
  error?: string;
  subscriber?: {
    email: string;
    subscribed_at: string;
  };
}

export function useEmailSubscription() {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const subscribe = async (email: string, source: string = 'website'): Promise<boolean> => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/v1/integrations/email/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, source }),
      });

      const data: SubscriptionResponse = await response.json();

      if (response.ok && data.success) {
        toast({
          title: 'Successfully Subscribed!',
          description: data.message || 'You will receive product updates and feature announcements.',
        });
        return true;
      } else {
        toast({
          title: 'Subscription Failed',
          description: data.error || 'Something went wrong. Please try again.',
          variant: 'destructive',
        });
        return false;
      }
    } catch (error) {
      console.error('Subscription error:', error);
      toast({
        title: 'Network Error',
        description: 'Unable to connect. Please check your internet connection and try again.',
        variant: 'destructive',
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const unsubscribe = async (email: string): Promise<boolean> => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/v1/integrations/email/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data: SubscriptionResponse = await response.json();

      if (response.ok && data.success) {
        toast({
          title: 'Successfully Unsubscribed',
          description: data.message || 'You will no longer receive product updates.',
        });
        return true;
      } else {
        toast({
          title: 'Unsubscribe Failed',
          description: data.error || 'Something went wrong. Please try again.',
          variant: 'destructive',
        });
        return false;
      }
    } catch (error) {
      console.error('Unsubscribe error:', error);
      toast({
        title: 'Network Error',
        description: 'Unable to connect. Please check your internet connection and try again.',
        variant: 'destructive',
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    subscribe,
    unsubscribe,
    isLoading,
  };
}
