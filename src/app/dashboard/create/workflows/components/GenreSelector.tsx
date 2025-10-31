"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Sparkles, X } from "lucide-react";

interface GenreSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectGenre: (genre: string, isInstrumental: boolean) => void;
  onGenerateRandom: (isInstrumental: boolean) => void;
  isInstrumental?: boolean;
  onInstrumentalChange?: (isInstrumental: boolean) => void;
}

const GENRES = [
  "Ambient",
  "Synthwave / Electronic",
  "Reggae / Dub / Ska",
  "Hip Hop / Rap",
  "Trap",
  "Lo-Fi / House",
  "Classical / Orchestral",
  "Rock / Metal / Punk",
  "Jazz / Blues",
  "World / Folk / Traditional",
  "Latin / Tango / Flamenco",
  "Pop / Indie / Folk",
  "Techno / EDM / Club",
  "World / Regional",
  "Cinematic / Trailer / Score",
  "Children / Playful",
  "Marches / Traditional Ensembles"
];

export function GenreSelector({ isOpen, onClose, onSelectGenre, onGenerateRandom, isInstrumental: externalIsInstrumental = false, onInstrumentalChange }: GenreSelectorProps) {
  const [isAnimating, setIsAnimating] = useState(false);
  const [isInstrumental, setIsInstrumental] = useState(externalIsInstrumental);
  const [isGenerating, setIsGenerating] = useState(false);
  const [loadingButton, setLoadingButton] = useState<string | null>(null);
  const [hoveredGenre, setHoveredGenre] = useState<string | null>(null);
  const modalRef = useRef<HTMLDivElement | null>(null);

  // Sync with external instrumental state
  useEffect(() => {
    setIsInstrumental(externalIsInstrumental);
  }, [externalIsInstrumental]);

  useEffect(() => {
    if (isOpen) {
      setIsAnimating(false); // Set to false immediately when popup opens
      setIsGenerating(false); // Reset generating state when popup opens
      setLoadingButton(null); // Reset loading button when popup opens
    }
  }, [isOpen]);

  // Handle escape key press
  useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscapeKey);
    }

    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  const handleGenreClick = async (genre: string) => {
    console.log('DEBUG: Genre selector - isInstrumental:', isInstrumental);
    setLoadingButton(genre);
    setIsGenerating(true);
    
    try {
      // Add random delay between 1-1.5 seconds
      const delay = Math.random() * 500 + 1000; // 1000-1500ms
      console.log(`🎵 Adding delay of ${delay}ms for genre: ${genre}`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      
      await onSelectGenre(genre, isInstrumental);
      onClose();
    } catch (error) {
      console.error('Error generating prompt:', error);
    } finally {
      setLoadingButton(null);
      setIsGenerating(false);
    }
  };

  const handleRandomGenerate = async () => {
    console.log('DEBUG: Random generate - isInstrumental:', isInstrumental);
    setLoadingButton('random');
    setIsGenerating(true);
    
    try {
      // Add random delay between 1-1.5 seconds
      const delay = Math.random() * 500 + 1000; // 1000-1500ms
      console.log(`🎵 Adding delay of ${delay}ms for random generation`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      // Pick a concrete random genre so the actual used value is returned
      const randomIndex = Math.floor(Math.random() * GENRES.length);
      const randomGenre = GENRES[randomIndex];
      await onSelectGenre(randomGenre, isInstrumental);
      onClose();
    } catch (error) {
      console.error('Error generating prompt:', error);
    } finally {
      setLoadingButton(null);
      setIsGenerating(false);
    }
  };


  console.log('🎨 GenreSelector rendering with isOpen:', isOpen);
  
  return (
    <div
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[9999] flex items-center justify-center p-4"
      onClick={onClose}
      style={{ pointerEvents: 'auto' }}
    >
      <div
        ref={modalRef}
        className="bg-card border border-border rounded-2xl  max-w-4xl w-full max-h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
        style={{ pointerEvents: 'auto' }}
      >
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-foreground">Select Music Genre</h2>
                <p className="text-sm text-muted-foreground">Choose a genre to generate a music description</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0 hover:bg-muted"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(80vh-88px)]">

          {/* Instrumental Checkbox */}
          <div className="mb-6">
            <div
              className="flex items-center space-x-4 p-3 rounded-lg border border-border bg-card hover:bg-muted/50 transition-colors duration-200 group cursor-pointer"
              onClick={() => {
                console.log('DEBUG: Checkbox clicked - current isInstrumental:', isInstrumental, 'new value:', !isInstrumental);
                const newValue = !isInstrumental;
                setIsInstrumental(newValue);
                onInstrumentalChange?.(newValue);
              }}
            >
              <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                isInstrumental
                  ? 'bg-muted-foreground border-muted-foreground'
                  : 'border-muted-foreground'
              }`}>
                {isInstrumental && (
                  <svg className="w-3 h-3 text-background" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div className="flex-1">
                <label className="text-sm font-medium text-foreground cursor-pointer">
                  Generate instrumental music (no lyrics)
                </label>
              </div>
            </div>
          </div>

          {/* Random Generate Button */}
          <div className="mb-6">
            <Button
              onClick={handleRandomGenerate}
              className="w-full h-12 text-base font-semibold btn-ai-gradient text-white flex items-center justify-center space-x-2"
              disabled={isGenerating}
            >
              {loadingButton === 'random' ? (
                <div className="w-5 h-5 animate-spin border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <Sparkles className="w-5 h-5" />
              )}
              <span>{loadingButton === 'random' ? 'Generating...' : 'Generate Random Genre'}</span>
            </Button>
          </div>

          {/* Genre Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {GENRES.map((genre, index) => {
              const isHovered = hoveredGenre === genre;
              const isOtherHovered = hoveredGenre !== null && hoveredGenre !== genre;
              
              return (
                <div
                  key={genre}
                  className="relative"
                  style={{
                    animationDelay: `${index * 50}ms`
                  }}
                >
                  <Button
                    variant="outline"
                    onClick={() => handleGenreClick(genre)}
                    disabled={isGenerating}
                    onMouseEnter={() => setHoveredGenre(genre)}
                    onMouseLeave={() => setHoveredGenre(null)}
                    className={`w-full h-12 text-sm font-medium transition-all duration-300 hover:bg-primary/5 hover:border-primary/30 hover:text-foreground disabled:opacity-50 disabled:cursor-not-allowed ${
                      isAnimating ? 'animate-fade-in-up' : ''
                    } ${
                      isOtherHovered ? 'opacity-60' : ''
                    }`}
                  >
                    {loadingButton === genre ? (
                      <div className="w-4 h-4 animate-spin border-2 border-muted-foreground border-t-transparent rounded-full" />
                    ) : (
                      <span className="truncate">{genre}</span>
                    )}
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
