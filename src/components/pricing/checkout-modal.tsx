"use client";

import React, { memo, useEffect, useRef } from 'react';
import { ModalWrapper } from '@/components/ui/modal-wrapper';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { X, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { type PricingPlan } from '@/lib/pricing-utils';

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  plan: PricingPlan | null;
  isLoading?: boolean;
  error?: string | null;
  onConfirm?: () => void;
}

export const CheckoutModal = memo(function CheckoutModal({
  isOpen,
  onClose,
  plan,
  isLoading = false,
  error = null,
  onConfirm
}: CheckoutModalProps) {
  const checkoutRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && plan && checkoutRef.current) {
      // Render mock checkout form
      const checkoutElement = checkoutRef.current;
      checkoutElement.innerHTML = `
        <div class="space-y-6">
          <!-- Plan Summary -->
          <div class="bg-muted/50 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-semibold">${plan.name}</h3>
              <Badge variant="secondary">${plan.price}</Badge>
            </div>
            <p class="text-sm text-muted-foreground">${plan.credits}</p>
          </div>

          <!-- Payment Form -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-2">Email</label>
              <input 
                type="email" 
                placeholder="your@email.com"
                class="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-2">Card Information</label>
              <div class="space-y-2">
                <input 
                  type="text" 
                  placeholder="1234 5678 9012 3456"
                  class="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <div class="grid grid-cols-2 gap-2">
                  <input 
                    type="text" 
                    placeholder="MM/YY"
                    class="px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <input 
                    type="text" 
                    placeholder="CVC"
                    class="px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Security Notice -->
          <div class="flex items-center gap-2 text-sm text-muted-foreground">
            <CheckCircle className="w-4 h-4 text-green-500" />
            <span>Your payment information is secure and encrypted</span>
          </div>
        </div>
      `;
    }
  }, [isOpen, plan]);

  if (!plan) return null;

  return (
    <ModalWrapper
      isOpen={isOpen}
      onClose={onClose}
      title="Complete Your Purchase"
      description={`Subscribe to ${plan.name} and start creating amazing content`}
      maxWidth="max-w-2xl"
    >
      <div className="space-y-6">
        {/* Error Display */}
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-sm text-red-700">{error}</span>
          </div>
        )}

        {/* Checkout Form */}
        <div ref={checkoutRef} className="min-h-[300px]" />

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-4 border-t">
          <Button variant="outline" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          
          <Button 
            onClick={onConfirm}
            disabled={isLoading}
            className="min-w-[120px]"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              `Subscribe for ${plan.price}`
            )}
          </Button>
        </div>
      </div>
    </ModalWrapper>
  );
});
