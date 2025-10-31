"use client";

import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlertTriangle, CreditCard, Plus } from "lucide-react";

interface InsufficientCreditsPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onAddCredits: () => void;
  onManageSubscription: () => void;
  musicGenerationPrice: number;
  videoGenerationPrice: number;
  currentBalance: number;
  shortfall: number;
}

export function InsufficientCreditsPopup({
  isOpen,
  onClose,
  onAddCredits,
  onManageSubscription,
  musicGenerationPrice,
  videoGenerationPrice,
  currentBalance,
  shortfall
}: InsufficientCreditsPopupProps) {
  const totalCost = musicGenerationPrice + videoGenerationPrice;
  const remainingAfterMusic = currentBalance - musicGenerationPrice;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            Insufficient Credits
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          <div className="text-sm text-muted-foreground">
            You won't have enough credits to generate a video after creating your music tracks.
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
              <span className="text-sm font-medium">Music Generation</span>
              <span className="text-sm font-semibold">{musicGenerationPrice} credits</span>
            </div>
            
            <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
              <span className="text-sm font-medium">Video Generation</span>
              <span className="text-sm font-semibold">{videoGenerationPrice} credits</span>
            </div>
            
            <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg border-2 border-primary/20">
              <span className="text-sm font-medium">Total Cost</span>
              <span className="text-sm font-bold text-primary">{totalCost} credits</span>
            </div>
            
            <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
              <span className="text-sm font-medium">Your Balance</span>
              <span className="text-sm font-semibold">{currentBalance} credits</span>
            </div>
            
            <div className="flex justify-between items-center p-3 bg-destructive/10 rounded-lg border border-destructive/20">
              <span className="text-sm font-medium text-destructive">Shortfall</span>
              <span className="text-sm font-bold text-destructive">{shortfall} credits</span>
            </div>
          </div>
          
          <div className="text-xs text-muted-foreground">
            After generating {musicGenerationPrice} credits worth of music, you'll have {remainingAfterMusic} credits remaining, 
            but you'll need {videoGenerationPrice} credits for video generation.
          </div>
          
          <div className="flex gap-2 pt-2">
            <Button 
              onClick={onAddCredits}
              className="flex-1"
              variant="default"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Credits
            </Button>
            <Button 
              onClick={onManageSubscription}
              variant="outline"
              className="flex-1"
            >
              <CreditCard className="w-4 h-4 mr-2" />
              Manage Subscription
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
