"use client";

import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Sparkles, User, X } from "lucide-react";
import { useToast } from "@/hooks/ui/use-toast";

interface ReferencePersonPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (description: string) => Promise<void>;
  isGenerating?: boolean;
  currentCredits?: number;
}

export function ReferencePersonPopup({
  isOpen,
  onClose,
  onGenerate,
  isGenerating = false,
  currentCredits = 0
}: ReferencePersonPopupProps) {
  const [description, setDescription] = useState("");
  const { toast } = useToast();

  const handleGenerate = async () => {
    if (!description.trim()) {
      toast({
        variant: "destructive",
        title: "Description Required",
        description: "Please provide a description of the person you want to generate.",
      });
      return;
    }

    if (description.trim().length < 10) {
      toast({
        variant: "destructive",
        title: "Description Too Short",
        description: "Please provide a more detailed description (at least 10 characters).",
      });
      return;
    }

    if (currentCredits < 2) {
      toast({
        variant: "destructive",
        title: "Insufficient Credits",
        description: "You need at least 2 credit to generate a reference person.",
      });
      return;
    }

    try {
      await onGenerate(description.trim());
      setDescription("");
      onClose();
    } catch (error) {
      console.error('Failed to generate reference person:', error);
      toast({
        variant: "destructive",
        title: "Generation Failed",
        description: "Failed to generate the reference person. Please try again.",
      });
    }
  };

  const handleClose = () => {
    setDescription("");
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary/30 to-primary/20 rounded-xl flex items-center justify-center shadow-lg border border-primary/25">
              <User className="w-5 h-5 text-primary" />
            </div>
            <span>Generate Reference Person</span>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">
              Person Description
            </label>
            <Textarea
              placeholder="Describe the person you want to include in your video (e.g., 'A young woman with long brown hair, wearing a red dress, standing in a garden')"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[100px] resize-none"
              maxLength={500}
            />
            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <span>Be specific about appearance, clothing, and setting</span>
              <span>{description.length}/500</span>
            </div>
          </div>

          <div className="p-3 bg-muted/20 rounded-lg border border-border/50">
            <div className="flex items-center space-x-2 mb-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-foreground">Generation Info</span>
            </div>
            <div className="space-y-1 text-xs text-muted-foreground">
              <p>• The generated person will match the style of your selected video settings</p>
              <p>• Generated image will be added to your reference images</p>
              <p>• Cost: <span className="font-semibold text-primary">2 credit</span></p>
            </div>
          </div>

           <div className="flex items-center space-x-2">
             <Button
               variant="outline"
               onClick={handleClose}
               disabled={isGenerating}
               className="flex-1"
             >
               Cancel
             </Button>
             <Button
               onClick={handleGenerate}
               disabled={isGenerating || !description.trim() || currentCredits < 2}
               className="btn-ai-gradient text-white flex items-center justify-center space-x-2 flex-1"
             >
               {isGenerating ? (
                 <>
                   <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                   <span>Generating...</span>
                 </>
               ) : (
                 <>
                   <Sparkles className="w-4 h-4" />
                   <span>Generate (2 credit)</span>
                 </>
               )}
             </Button>
           </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
