"use client";

import { Button } from "@/components/ui/button";
import { FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { X, Menu, ChevronLeft } from "lucide-react";
import { UseFormReturn } from "react-hook-form";
import { VideoTypeCard } from "./VideoTypeCard";
import { useState } from "react";

export interface SelectionOption {
  id: string;
  name: string;
  description: string;
  icon: string;
  gradient: string;
  preview?: string;
  cardStyle?: string;
  isSelected?: boolean;
}

interface SelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description: string;
  options: SelectionOption[];
  selectedValue: string;
  onSelect: (value: string, label?: string) => void;
  maxWidth?: string;
  gridCols?: string;
  showSidebar?: boolean;
  form?: UseFormReturn<any>;
  sidebarContent?: React.ReactNode;
  cardDesign?: boolean;
  collapsibleSidebar?: boolean;
}

export function SelectionModal({
  isOpen,
  onClose,
  title,
  description,
  options,
  selectedValue,
  onSelect,
  maxWidth = "max-w-4xl",
  gridCols = "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
  showSidebar = false,
  form,
  sidebarContent,
  cardDesign = false,
  collapsibleSidebar = false
}: SelectionModalProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [hoveredCardId, setHoveredCardId] = useState<string | null>(null);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[70] bg-black/80 backdrop-blur-sm" onClick={onClose}>
      <div className="flex items-center justify-center min-h-screen p-4">
        <div
          className={`bg-background rounded-2xl ${maxWidth} w-full h-[90vh] flex flex-col`}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex-shrink-0 p-8 pb-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold">{title}</h2>
                <p className="text-muted-foreground mt-2">{description}</p>
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
          </div>

          <div className={`flex-1 flex ${showSidebar && (!collapsibleSidebar || isSidebarOpen) ? 'gap-8' : ''} px-8 pb-8 min-h-0`}>
            <div className={`${showSidebar ? (collapsibleSidebar && !isSidebarOpen ? 'w-full overflow-y-auto' : 'flex-1 overflow-y-auto') : 'w-full overflow-y-auto'} scrollbar-thin scrollbar-thumb-muted-foreground/20 scrollbar-track-transparent`}>
              <div className="flex items-center justify-between mb-6">
                <div className="flex-1" />
                {showSidebar && collapsibleSidebar && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                    className="flex items-center space-x-2"
                  >
                    <Menu className="w-4 h-4" />
                    <span>Settings</span>
                  </Button>
                )}
              </div>
              <div className={`grid ${showSidebar && collapsibleSidebar && !isSidebarOpen ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5' : gridCols} gap-6 pb-4`}>
                {options.map((option) => {
                  const isHovered = !cardDesign && hoveredCardId === option.id;
                  const isOtherHovered = !cardDesign && hoveredCardId !== null && hoveredCardId !== option.id;
                  
                  return cardDesign ? (
                    <VideoTypeCard
                      key={option.id}
                      id={option.id}
                      name={option.name}
                      description={option.description}
                      icon={option.icon}
                      gradient={option.gradient}
                      isSelected={selectedValue === option.id || (option.isSelected ?? false)}
                      hoveredCardId={hoveredCardId}
                      onHover={setHoveredCardId}
                      onClick={() => {
                        onSelect(option.id, option.name);
                        if (!showSidebar) {
                          onClose();
                        }
                      }}
                    />
                  ) : (
                    <div
                      key={option.id}
                      className={`p-6 rounded-2xl border-2 cursor-pointer transition-all duration-300 ${
                        selectedValue === option.id || option.isSelected
                          ? "border-primary bg-primary/5"
                          : isHovered
                          ? "border-primary/50"
                          : isOtherHovered
                          ? "border-border opacity-60"
                          : "border-border hover:border-primary/50"
                      }`}
                      onClick={() => {
                        onSelect(option.id, option.name);
                        if (!showSidebar) {
                          onClose();
                        }
                      }}
                      onMouseEnter={() => setHoveredCardId(option.id)}
                      onMouseLeave={() => setHoveredCardId(null)}
                    >
                      <div className="space-y-4">
                        <div className="relative">
                          <div className={`w-full h-32 bg-gradient-to-br ${option.gradient} rounded-xl flex items-center justify-center`}>
                            <span className="text-4xl">{option.icon}</span>
                          </div>
                          <div className="absolute inset-0 bg-black/0 hover:bg-black/10 transition-colors rounded-xl"></div>
                        </div>

                        <div className="space-y-3">
                          <h3 className="font-bold text-xl">{option.name}</h3>
                          <p className="text-muted-foreground">{option.description}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {showSidebar && (
              <div className={`${collapsibleSidebar ? (isSidebarOpen ? 'w-80' : 'w-0') : 'w-80'} flex-shrink-0 transition-all duration-300 overflow-hidden`}>
                <div className="h-full flex flex-col border rounded-2xl bg-muted/30">
                  <div className="flex-1 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">Settings</h3>
                      {collapsibleSidebar && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setIsSidebarOpen(false)}
                          className="h-8 w-8 p-0"
                        >
                          <ChevronLeft className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                    {sidebarContent}
                  </div>
                  <div className="flex-shrink-0 p-6 pt-0">
                    <div className="flex space-x-3">
                      <Button
                        variant="outline"
                        onClick={onClose}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={() => {
                          const selected = options.find(o => o.id === selectedValue);
                          onSelect(selectedValue, selected?.name);
                          onClose();
                        }}
                        className="flex-1 btn-ai-gradient text-white"
                        disabled={!selectedValue}
                      >
                        Confirm
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

