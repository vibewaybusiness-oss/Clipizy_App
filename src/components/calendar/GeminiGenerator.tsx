"use client";

import React from 'react';

interface GeminiGeneratorProps {
  post: any;
  onGenerate: (content: string) => void;
  onSave: (post: any) => void;
  apiKey: string;
  onApiKeyChange: (key: string) => void;
}

export function GeminiGenerator({
  post,
  onGenerate,
  onSave,
  apiKey,
  onApiKeyChange
}: GeminiGeneratorProps) {
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Gemini Generator</h2>
      <p className="text-muted-foreground">Gemini generator component coming soon...</p>
    </div>
  );
}
