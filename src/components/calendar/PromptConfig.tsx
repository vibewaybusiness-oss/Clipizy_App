"use client";

import React from 'react';
import { GeminiPrompt } from '@/types/domains/calendar';

interface PromptConfigProps {
  prompts: GeminiPrompt[];
  onSavePrompt: (prompt: GeminiPrompt) => void;
  onDeletePrompt: (id: string) => void;
  onUpdateSettings: (newSettings: { prefix: string; suffix: string }) => void;
  settings: {
    prefix: string;
    suffix: string;
  };
}

export function PromptConfig({
  prompts,
  onSavePrompt,
  onDeletePrompt,
  onUpdateSettings,
  settings
}: PromptConfigProps) {
  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold mb-4">Prompt Configuration</h2>
      <p className="text-muted-foreground">Prompt configuration component coming soon...</p>
      <p className="text-sm text-muted-foreground mt-2">
        Prompts: {prompts.length}, Prefix: {settings.prefix}, Suffix: {settings.suffix}
      </p>
    </div>
  );
}
