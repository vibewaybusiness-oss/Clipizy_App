"use client";

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useEmailSubscription } from '@/hooks/users/use-email-subscription';
import { Mail, Check, Loader2 } from 'lucide-react';

interface EmailSubscriptionProps {
  placeholder?: string;
  buttonText?: string;
  source?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'inline' | 'minimal';
}

export function EmailSubscription({
  placeholder = "Enter your email",
  buttonText = "Subscribe",
  source = "website",
  className = "",
  size = "md",
  variant = "default"
}: EmailSubscriptionProps) {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const { subscribe, isLoading } = useEmailSubscription();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email.trim() || !email.includes('@')) {
      return;
    }

    const success = await subscribe(email.trim(), source);
    if (success) {
      setEmail('');
      setIsSubmitted(true);
      setTimeout(() => setIsSubmitted(false), 3000);
    }
  };

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  const inputSizeClasses = {
    sm: 'h-8 px-3',
    md: 'h-10 px-4',
    lg: 'h-12 px-4'
  };

  const buttonSizeClasses = {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4',
    lg: 'h-12 px-6 text-lg'
  };

  if (variant === 'minimal') {
    return (
      <form onSubmit={handleSubmit} className={`flex gap-2 ${className}`}>
        <Input
          type="email"
          placeholder={placeholder}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isLoading}
          className={`${inputSizeClasses[size]} ${sizeClasses[size]}`}
          required
        />
        <Button
          type="submit"
          disabled={isLoading || !email.trim()}
          className={`${buttonSizeClasses[size]} btn-gradient`}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : isSubmitted ? (
            <Check className="w-4 h-4" />
          ) : (
            buttonText
          )}
        </Button>
      </form>
    );
  }

  if (variant === 'inline') {
    return (
      <div className={`flex flex-col sm:flex-row gap-3 ${className}`}>
        <Input
          type="email"
          placeholder={placeholder}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={isLoading}
          className={`${inputSizeClasses[size]} ${sizeClasses[size]} flex-1`}
          required
        />
        <Button
          onClick={handleSubmit}
          disabled={isLoading || !email.trim()}
          className={`${buttonSizeClasses[size]} btn-gradient whitespace-nowrap`}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : isSubmitted ? (
            <Check className="w-4 h-4" />
          ) : (
            buttonText
          )}
        </Button>
      </div>
    );
  }

  // Default variant
  return (
    <div className={`space-y-4 ${className}`}>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex gap-2">
          <Input
            type="email"
            placeholder={placeholder}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
            className={`${inputSizeClasses[size]} ${sizeClasses[size]} flex-1`}
            required
          />
          <Button
            type="submit"
            disabled={isLoading || !email.trim()}
            className={`${buttonSizeClasses[size]} btn-gradient`}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isSubmitted ? (
              <Check className="w-4 h-4" />
            ) : (
              <>
                <Mail className="w-4 h-4 mr-2" />
                {buttonText}
              </>
            )}
          </Button>
        </div>
      </form>
      
      {isSubmitted && (
        <p className="text-sm text-green-600 dark:text-green-400 flex items-center">
          <Check className="w-4 h-4 mr-2" />
          Successfully subscribed! Check your email for confirmation.
        </p>
      )}
    </div>
  );
}
