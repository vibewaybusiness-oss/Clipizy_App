"use client";

import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, AlertCircle, CreditCard, Crown, ArrowRight, Clock } from "lucide-react";

interface GenerationPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  estimatedTime?: string;
  creditsCost?: number;
  isGenerating?: boolean;
  hasEnoughCredits?: boolean;
  currentCredits?: number;
  onBuyCredits?: () => void;
  onUpgradeSubscription?: () => void;
  onContinueToReview?: () => void;
  onGoToMainMenu?: () => void;
  onFullControlMode?: () => void;
  onDirectToFinalMode?: () => void;
  generationCompleted?: boolean;
}

export function GenerationPopup({
  isOpen,
  onClose,
  onConfirm,
  estimatedTime = "5-10 minutes",
  creditsCost = 0,
  isGenerating = false,
  hasEnoughCredits = true,
  currentCredits = 0,
  onBuyCredits,
  onUpgradeSubscription,
  onContinueToReview,
  onGoToMainMenu,
  onFullControlMode,
  onDirectToFinalMode,
  generationCompleted = false
}: GenerationPopupProps) {
  // Auto-start functionality removed - now using explicit button choices

  const handleBuyCredits = () => {
    onBuyCredits?.();
    onClose();
  };

  const handleUpgradeSubscription = () => {
    onUpgradeSubscription?.();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/10 rounded-lg flex items-center justify-center">
              {hasEnoughCredits ? (
                <Clock className="w-4 h-4 text-primary" />
              ) : (
                <AlertCircle className="w-4 h-4 text-orange-500" />
              )}
            </div>
            <span>{hasEnoughCredits ? "Video Generation" : "Insufficient Credits"}</span>
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {hasEnoughCredits ? (
            <>
              {/* Simple Generation Started Message */}
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-gradient-to-br from-primary/10 to-primary/5 rounded-full flex items-center justify-center mx-auto">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-foreground">
                    Generation Started!
                  </h3>
                  <p className="text-sm text-muted-foreground mt-2">
                    Your video generation has started and will require subsequent steps validation. The project will be accessible in the projects area.
                  </p>
                </div>
              </div>

              {/* Simple Action Button */}
              <div className="pt-2">
                <Button
                  onClick={onContinueToReview}
                  className="w-full btn-ai-gradient text-white"
                >
                  <ArrowRight className="w-4 h-4 mr-2" />
                  Continue to Generation
                </Button>
              </div>
            </>
          ) : (
            <>
              {/* Insufficient Credits Message */}
              <div className="text-center space-y-3">
                <div className="w-16 h-16 bg-gradient-to-br from-orange-100 to-orange-50 dark:from-orange-900/20 dark:to-orange-800/10 rounded-full flex items-center justify-center mx-auto">
                  <AlertCircle className="w-8 h-8 text-orange-500" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-foreground">
                    Insufficient Credits
                  </h3>
                  <p className="text-sm text-muted-foreground mt-2">
                    You need {creditsCost} credits to generate this video, but you only have {currentCredits} credits.
                  </p>
                </div>
              </div>

              {/* Credit Information */}
              <div className="bg-muted/50 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">Required Credits</span>
                  <Badge variant="secondary" className="bg-orange-100 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400">
                    {creditsCost} credits
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">Your Balance</span>
                  <Badge variant="outline" className="text-muted-foreground">
                    {currentCredits} credits
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">Shortfall</span>
                  <Badge variant="destructive">
                    {creditsCost - currentCredits} credits
                  </Badge>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3 pt-2">
                <Button
                  onClick={handleBuyCredits}
                  className="w-full btn-ai-gradient text-white"
                >
                  <CreditCard className="w-4 h-4 mr-2" />
                  Buy Credits
                </Button>
                <Button
                  onClick={handleUpgradeSubscription}
                  variant="outline"
                  className="w-full"
                >
                  <Crown className="w-4 h-4 mr-2" />
                  Upgrade Subscription
                </Button>
                <Button
                  variant="ghost"
                  onClick={onClose}
                  className="w-full"
                >
                  Cancel
                </Button>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
