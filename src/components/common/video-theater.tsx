"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { X, Maximize2, ExternalLink } from "lucide-react";

interface VideoTheaterProps {
  isOpen: boolean;
  onClose: () => void;
  videoSrc: string;
  title: string;
  description: string;
}

export function VideoTheater({ isOpen, onClose, videoSrc, title, description }: VideoTheaterProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleFullscreen = () => {
    const videoElement = document.querySelector('video');
    if (videoElement) {
      if (!document.fullscreenElement) {
        videoElement.requestFullscreen();
        setIsFullscreen(true);
      } else {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl w-full h-[80vh] p-0 bg-black">
        <DialogHeader className="absolute top-4 left-4 right-4 z-10 flex flex-row items-center justify-between">
          <div>
            <DialogTitle className="text-white text-xl">{title}</DialogTitle>
            <p className="text-gray-300 text-sm">{description}</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant="secondary"
              onClick={handleFullscreen}
              className="bg-white/20 hover:bg-white/30 text-white border-white/30"
            >
              {isFullscreen ? <X className="w-4 h-4 mr-2" /> : <Maximize2 className="w-4 h-4 mr-2" />}
              {isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={onClose}
              className="bg-white/20 hover:bg-white/30 text-white border-white/30"
            >
              <X className="w-4 h-4 mr-2" />
              Close
            </Button>
          </div>
        </DialogHeader>

        <div className="relative w-full h-full flex items-center justify-center">
          <video
            className="w-full h-full object-contain"
            controls
            autoPlay
            muted
            loop
          >
            <source src={videoSrc} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      </DialogContent>
    </Dialog>
  );
}


