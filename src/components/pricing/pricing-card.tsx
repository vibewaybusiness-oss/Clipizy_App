"use client";

import React, { memo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { type PricingPlan } from '@/lib/pricing-utils';

interface PricingCardProps {
  plan: PricingPlan;
  isSelected?: boolean;
  isLoading?: boolean;
  onSelect?: (plan: PricingPlan) => void;
  onCheckout?: (plan: PricingPlan) => void;
  className?: string;
}

export const PricingCard = memo(function PricingCard({
  plan,
  isSelected = false,
  isLoading = false,
  onSelect,
  onCheckout,
  className
}: PricingCardProps) {
  const handleSelect = () => {
    onSelect?.(plan);
  };

  const handleCheckout = () => {
    onCheckout?.(plan);
  };

  return (
    <Card 
      className={cn(
        'relative transition-all duration-200 hover:shadow-lg',
        isSelected && 'ring-2 ring-primary shadow-lg',
        plan.popular && 'border-primary/20',
        className
      )}
    >
      {plan.popular && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <Badge className="bg-primary text-white px-3 py-1 text-sm font-medium">
            Most Popular
          </Badge>
        </div>
      )}
      
      <CardHeader className="text-center pb-4">
        <div className={cn(
          'w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 text-2xl',
          plan.color
        )}>
          {plan.icon}
        </div>
        
        <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
        <CardDescription className="text-lg font-semibold text-primary">
          {plan.price}
        </CardDescription>
        <p className="text-sm text-muted-foreground">
          {plan.credits}
        </p>
      </CardHeader>

      <CardContent className="space-y-6">
        <ul className="space-y-3">
          {plan.features.map((feature, index) => (
            <li key={index} className="flex items-start gap-3">
              <Check className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-muted-foreground">{feature}</span>
            </li>
          ))}
        </ul>

        <div className="space-y-2">
          <Button
            onClick={handleSelect}
            variant={isSelected ? "default" : "outline"}
            className="w-full"
            disabled={isLoading}
          >
            {isSelected ? 'Selected' : 'Select Plan'}
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
          
          {isSelected && (
            <Button
              onClick={handleCheckout}
              className="w-full bg-primary hover:bg-primary/90"
              disabled={isLoading}
            >
              {isLoading ? 'Processing...' : 'Start Checkout'}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
});
