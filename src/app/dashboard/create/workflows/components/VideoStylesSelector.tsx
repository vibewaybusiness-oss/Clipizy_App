"use client";

import React from "react";
import { SelectionModal } from "./SelectionModal";

interface VideoStylesSelectorProps {
  selectedStyles: string[];
  onStylesChange: (styles: string[]) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function VideoStylesSelector({
  selectedStyles,
  onStylesChange,
  isOpen,
  onClose
}: VideoStylesSelectorProps) {

  const videoStyles = [
    {
      id: "none",
      name: "None",
      description: "No video style",
      icon: "🚫",
      gradient: "from-gray-500/20 to-slate-500/20"
    },
    {
      id: "manga",
      name: "Manga",
      description: "Detailed black and white manga illustration style, with bold linework, expressive faces, screen-tone shading, and dynamic panel-like composition",
      icon: "📖",
      gradient: "from-gray-500/20 to-slate-500/20"
    },
    {
      id: "studio ghibli",
      name: "Studio Ghibli",
      description: "Whimsical and dreamy Studio Ghibli style, soft watercolor textures, lush backgrounds, warm lighting, and expressive characters with big eyes",
      icon: "🎭",
      gradient: "from-green-500/20 to-emerald-500/20"
    },
    {
      id: "modern art",
      name: "Modern Art",
      description: "Bold modern art style, geometric abstraction, vivid contrasting colors, and experimental composition inspired by Picasso and Kandinsky",
      icon: "🎨",
      gradient: "from-purple-500/20 to-pink-500/20"
    },
    {
      id: "cyberpunk",
      name: "Cyberpunk",
      description: "Neon-drenched cyberpunk style, futuristic cityscape, glowing holograms, gritty urban details, and cinematic lighting with a dark futuristic mood",
      icon: "🌃",
      gradient: "from-cyan-500/20 to-blue-500/20"
    },
    {
      id: "watercolor",
      name: "Watercolor",
      description: "Soft watercolor painting style, flowing brushstrokes, light pastel tones, and organic textures with a handmade look",
      icon: "🎨",
      gradient: "from-pink-500/20 to-rose-500/20"
    },
    {
      id: "pixel art",
      name: "Pixel Art",
      description: "Retro pixel art style, low-resolution 8-bit aesthetic, vibrant colors, simple geometric shading, and nostalgic video game vibe",
      icon: "🕹️",
      gradient: "from-orange-500/20 to-red-500/20"
    },
    {
      id: "oil painting",
      name: "Oil Painting",
      description: "Rich oil painting style, textured brushstrokes, dramatic lighting, and classical art composition reminiscent of the Renaissance",
      icon: "🖼️",
      gradient: "from-amber-500/20 to-yellow-500/20"
    },
    {
      id: "anime",
      name: "Anime",
      description: "Vibrant anime style, clean cel-shading, big expressive eyes, exaggerated emotions, and colorful cinematic backgrounds",
      icon: "🎌",
      gradient: "from-indigo-500/20 to-purple-500/20"
    },
    {
      id: "futurism",
      name: "Futurism",
      description: "Futuristic art style, sleek minimalism, metallic textures, glowing accents, and visionary sci-fi design",
      icon: "🚀",
      gradient: "from-slate-500/20 to-gray-500/20"
    },
    {
      id: "surrealism",
      name: "Surrealism",
      description: "Surrealist style, dreamlike imagery, impossible shapes, symbolic objects, and melting or morphing landscapes inspired by Salvador Dalí",
      icon: "🌙",
      gradient: "from-violet-500/20 to-purple-500/20"
    },
    {
      id: "impressionist",
      name: "Impressionist",
      description: "Impressionist style, loose visible brushstrokes, vibrant light effects, soft pastel colors, and a focus on atmosphere over detail inspired by Monet",
      icon: "🌅",
      gradient: "from-yellow-500/20 to-orange-500/20"
    },
    {
      id: "baroque",
      name: "Baroque",
      description: "Dramatic baroque style, rich contrasts of light and shadow (chiaroscuro), ornate detail, and theatrical grandeur inspired by Caravaggio",
      icon: "🏛️",
      gradient: "from-amber-500/20 to-orange-500/20"
    },
    {
      id: "minimalist",
      name: "Minimalist",
      description: "Minimalist style, clean simple shapes, flat muted colors, lots of negative space, and elegant reduction of details",
      icon: "⚪",
      gradient: "from-gray-500/20 to-slate-500/20"
    },
    {
      id: "pop art",
      name: "Pop Art",
      description: "Bold pop art style, comic-book inspired outlines, vibrant flat colors, and playful mass-culture references inspired by Andy Warhol and Roy Lichtenstein",
      icon: "💥",
      gradient: "from-red-500/20 to-pink-500/20"
    },
    {
      id: "steampunk",
      name: "Steampunk",
      description: "Retro-futuristic steampunk style, Victorian-inspired machinery, brass gears, steam vents, and intricate mechanical detail",
      icon: "⚙️",
      gradient: "from-amber-500/20 to-yellow-500/20"
    },
    {
      id: "fantasy illustration",
      name: "Fantasy Illustration",
      description: "Epic fantasy illustration style, dramatic lighting, painterly textures, ornate costumes, and cinematic compositions reminiscent of book covers",
      icon: "🐉",
      gradient: "from-emerald-500/20 to-teal-500/20"
    },
    {
      id: "art deco",
      name: "Art Deco",
      description: "Glamorous art deco style, geometric symmetry, metallic accents, bold patterns, and a luxurious 1920s aesthetic",
      icon: "💎",
      gradient: "from-rose-500/20 to-pink-500/20"
    },
    {
      id: "graffiti",
      name: "Graffiti",
      description: "Vibrant graffiti style, spray-paint textures, bold outlines, neon colors, and urban wall-art energy inspired by Banksy and street murals",
      icon: "🎨",
      gradient: "from-lime-500/20 to-green-500/20"
    },
    {
      id: "concept art",
      name: "Concept Art",
      description: "Cinematic concept art style, highly detailed environment design, atmospheric lighting, and epic scale used for movie or game previsualization",
      icon: "🎬",
      gradient: "from-blue-500/20 to-indigo-500/20"
    },
    {
      id: "dark fantasy / gothic",
      name: "Dark Fantasy / Gothic",
      description: "Dark gothic fantasy style, moody lighting, gothic architecture, ornate dark armor, and a grim haunting atmosphere",
      icon: "🦇",
      gradient: "from-gray-500/20 to-slate-500/20"
    },
    {
      id: "retro 80s",
      name: "Retro 80s",
      description: "Synthwave retro 80s style, neon gridlines, vaporwave colors (purple, pink, cyan), and futuristic nostalgia",
      icon: "💿",
      gradient: "from-purple-500/20 to-pink-500/20"
    },
    {
      id: "cubism",
      name: "Cubism",
      description: "Cubist style, fragmented geometric forms, multiple perspectives, and abstract arrangement inspired by Picasso",
      icon: "🔷",
      gradient: "from-blue-500/20 to-cyan-500/20"
    },
    {
      id: "rococo",
      name: "Rococo",
      description: "Ornate rococo style, pastel colors, elegant swirling decorations, light playful mood, and aristocratic atmosphere",
      icon: "🌸",
      gradient: "from-pink-500/20 to-rose-500/20"
    },
    {
      id: "ink wash (sumi-e)",
      name: "Ink Wash (Sumi-e)",
      description: "Traditional Japanese sumi-e style, black ink wash brushstrokes, minimalist composition, and natural organic flow",
      icon: "🖋️",
      gradient: "from-gray-500/20 to-slate-500/20"
    },
    {
      id: "photorealistic",
      name: "Photorealistic",
      description: "Hyper-detailed photorealistic style, cinematic lens effects, realistic textures, and lifelike rendering",
      icon: "📸",
      gradient: "from-slate-500/20 to-gray-500/20"
    },
    {
      id: "pixel neon cyberwave",
      name: "Pixel Neon Cyberwave",
      description: "Retro-futuristic pixel neon style, vaporwave colors, glowing lights, pixelated rendering, and nostalgic digital vibe",
      icon: "🌊",
      gradient: "from-cyan-500/20 to-purple-500/20"
    }
  ];

  const handleStyleSelect = (styleId: string, styleName?: string) => {
    if (styleId === "none") {
      onStylesChange([]);
      onClose();
      return;
    }
    
    const newStyles = selectedStyles.includes(styleId)
      ? selectedStyles.filter(s => s !== styleId)
      : [...selectedStyles, styleId];
    
    onStylesChange(newStyles);
  };

  if (!isOpen) {
    return null;
  }

  return (
    <SelectionModal
      isOpen={isOpen}
      onClose={onClose}
      title="Choose Video Styles"
      description="Select one or more visual styles for your video. You can select multiple styles by clicking them."
      options={videoStyles.map(style => ({
        ...style,
        isSelected: selectedStyles.includes(style.id)
      }))}
      selectedValue={selectedStyles[0] || ""}
      onSelect={handleStyleSelect}
      gridCols="grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
      maxWidth="max-w-6xl"
      cardDesign={true}
    />
  );
}

