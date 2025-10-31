"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { X, Mail } from "lucide-react";

interface SelectionOption {
  id: string;
  name: string;
  description: string;
  icon: string;
  gradient: string;
  preview?: string;
  cost?: number;
  available?: boolean;
  comingSoonText?: string;
  onNewsletterSignup?: (email: string) => void;
}

interface SelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  subtitle: string;
  options: SelectionOption[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  showCost?: boolean;
  costConversionRate?: number;
}

export function SelectionModal({
  isOpen,
  onClose,
  title,
  subtitle,
  options,
  selectedId,
  onSelect,
  showCost = false,
  costConversionRate = 1
}: SelectionModalProps) {
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

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {options.map((option) => (
                 <div
                   key={option.id}
                   className={`p-8 rounded-2xl border-2 cursor-pointer transition-all duration-300 relative ${
                     selectedId === option.id
                       ? "border-muted-foreground bg-muted/50 shadow-xl"
                       : "border-border hover:border-muted-foreground/50 hover:bg-muted/50"
                   }`}
                   onClick={() => option.available !== false && onSelect(option.id)}
                 >
                   <div className="space-y-6">
                     <div className={`w-full h-64 bg-gradient-to-br ${option.gradient} rounded-xl flex items-center justify-center relative ${option.available === false ? 'opacity-60' : ''}`}>
                       <span className="text-8xl">{option.icon}</span>

                       {/* Coming Soon Overlay - only on the gradient area */}
                       {option.available === false && (
                         <div className="absolute inset-0 bg-black/30 rounded-xl flex items-center justify-center z-10">
                           <div className="text-center">
                             <h4 className="text-white font-bold text-lg drop-shadow-lg">Coming Soon</h4>
                           </div>
                         </div>
                       )}
                     </div>

                     <div className={`space-y-4 ${option.available === false ? 'opacity-60' : ''}`}>
                       <h3 className="font-bold text-2xl">{option.name}</h3>
                       <p className="text-muted-foreground text-lg">{option.description}</p>
                     </div>

                     {option.available === false ? (
                       <div className="mt-6 p-4 bg-muted/50 rounded-xl">
                         <div className="text-center space-y-4">
                           <div className="space-y-2">
                             <p className="text-sm text-muted-foreground font-medium">{option.comingSoonText}</p>
                           </div>
                           {option.onNewsletterSignup && (
                             <Button
                               size="sm"
                               onClick={(e) => {
                                 e.stopPropagation();
                                 option.onNewsletterSignup!("");
                               }}
                               className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white border-0"
                             >
                               <Mail className="w-4 h-4 mr-2" />
                               Notify Me
                             </Button>
                           )}
                         </div>
                       </div>
                     ) : null}

                     {showCost && option.cost && (
                       <div className="mt-6 rounded-xl bg-secondary/50 px-6 py-3 text-lg font-bold">
                         <span className="text-muted-foreground">{option.cost * costConversionRate} credits</span>
                       </div>
                     )}
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
