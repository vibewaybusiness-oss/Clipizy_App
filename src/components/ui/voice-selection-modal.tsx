"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

interface VoiceOption {
  id: string;
  name: string;
  description: string;
  icon: string;
  gradient: string;
  preview?: string;
  available?: boolean;
  comingSoonText?: string;
  onNewsletterSignup?: (email: string) => void;
}

interface VoiceSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle: string;
  options: VoiceOption[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function VoiceSelectionModal({
  isOpen,
  onClose,
  title,
  subtitle,
  options,
  selectedId,
  onSelect
}: VoiceSelectionModalProps) {
  const [email, setEmail] = useState("");
  const [showEmailInput, setShowEmailInput] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleNewsletterSignup = (optionId: string) => {
    if (email.trim()) {
      const option = options.find(opt => opt.id === optionId);
      if (option?.onNewsletterSignup) {
        option.onNewsletterSignup(email);
        setEmail("");
        setShowEmailInput(null);
      }
    }
  };

  return (
    <div className="fixed inset-0 z-[70] bg-black/80 backdrop-blur-sm" onClick={onClose}>
      <div className="flex items-center justify-center min-h-screen p-4">
        <div
          className="bg-background rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="p-8">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h2 className="text-3xl font-bold">{title}</h2>
                <p className="text-muted-foreground mt-2">{subtitle}</p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-10 w-10"
              >
                <X className="h-6 w-6" />
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {options.map((option) => (
                 <div
                   key={option.id}
                   className={`p-6 rounded-2xl border-2 cursor-pointer transition-all duration-300 relative ${
                     selectedId === option.id
                       ? "border-primary bg-primary/5 shadow-xl"
                       : "border-border hover:border-primary/50 hover:bg-muted/50"
                   }`}
                   onClick={() => option.available !== false && onSelect(option.id)}
                 >
                   <div className="space-y-4">
                     <div className={`w-full h-32 bg-gradient-to-br ${option.gradient} rounded-xl flex items-center justify-center relative ${option.available === false ? 'opacity-60' : ''}`}>
                       <span className="text-4xl">{option.icon}</span>

                       {/* Coming Soon Overlay - only on the gradient area */}
                       {option.available === false && (
                         <div className="absolute inset-0 bg-black/30 rounded-xl flex items-center justify-center z-10">
                           <div className="text-center">
                             <h4 className="text-white font-bold text-base drop-shadow-lg">Coming Soon</h4>
                           </div>
                         </div>
                       )}
                     </div>

                     <div className={`space-y-2 ${option.available === false ? 'opacity-60' : ''}`}>
                       <h3 className="font-bold text-lg">{option.name}</h3>
                       <p className="text-muted-foreground text-sm">{option.description}</p>
                     </div>

                     {option.available === false ? (
                       <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                         <div className="text-center space-y-3">
                           <div className="space-y-1">
                             <p className="text-xs text-muted-foreground font-medium">{option.comingSoonText}</p>
                           </div>
                           {option.onNewsletterSignup && (
                             <Button
                               size="sm"
                               onClick={(e) => {
                                 e.stopPropagation();
                                 option.onNewsletterSignup!("");
                               }}
                               className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white border-0 h-6 px-2 text-xs"
                             >
                               Notify Me
                             </Button>
                           )}
                         </div>
                       </div>
                     ) : option.preview ? (
                       <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                         <p className="text-xs text-muted-foreground mb-1 font-medium">Preview:</p>
                         <p className="text-sm italic">"{option.preview}"</p>
                       </div>
                     ) : null}
                   </div>
                 </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
