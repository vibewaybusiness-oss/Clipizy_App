"use client";

import { useState } from 'react';
import { PromptConfig } from '@/components/calendar/PromptConfig';
import type { GeminiPrompt } from '@/types/domains';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import {
  Settings,
  Bot,
  Save,
  Download,
  Upload,
  RefreshCw
} from 'lucide-react';

export default function ContentCalendarSettingsPage() {
  const [prompts, setPrompts] = useState<GeminiPrompt[]>([]);
  const [settings, setSettings] = useState({
    prefix: 'Generate a blog post for the following scene: ',
    suffix: '',
    geminiApiKey: '',
    autoGenerate: false,
    defaultAuthor: {
      name: 'clipizy Team',
      email: 'content@clipizy.com'
    },
    publishingSchedule: {
      days: ['tuesday', 'friday'],
      time: '10:00',
      timezone: 'UTC'
    }
  });

  const handleSavePrompt = (prompt: GeminiPrompt) => {
    setPrompts(prev => {
      const existing = prev.find(p => p.id === prompt.id);
      if (existing) {
        return prev.map(p => p.id === prompt.id ? prompt : p);
      }
      return [...prev, prompt];
    });
  };

  const handleDeletePrompt = (id: string) => {
    setPrompts(prev => prev.filter(p => p.id !== id));
  };

  const handleUpdateSettings = (newSettings: { prefix: string; suffix: string }) => {
    setSettings(prev => ({
      ...prev,
      prefix: newSettings.prefix,
      suffix: newSettings.suffix
    }));
  };

  const handleSaveSettings = () => {
    // localStorage removed - backend storage only
    // TODO: Implement backend API call to save settings
    console.log('Settings to save:', { settings, prompts });
  };

  const handleExportSettings = () => {
    const data = {
      settings,
      prompts,
      exportedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'content-calendar-settings.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImportSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        if (data.settings) setSettings(data.settings);
        if (data.prompts) setPrompts(data.prompts);
      } catch (error) {
        console.error('Failed to import settings:', error);
        alert('Failed to import settings. Please check the file format.');
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="p-6 space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Content Calendar Settings</h1>
          <p className="text-muted-foreground">Configure your content generation and publishing settings</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleExportSettings}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" onClick={() => document.getElementById('import-settings')?.click()}>
            <Upload className="w-4 h-4 mr-2" />
            Import
          </Button>
          <input
            id="import-settings"
            type="file"
            accept=".json"
            onChange={handleImportSettings}
            className="hidden"
          />
          <Button onClick={handleSaveSettings}>
            <Save className="w-4 h-4 mr-2" />
            Save Settings
          </Button>
        </div>
      </div>

      {/* GEMINI API SETTINGS */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-5 h-5" />
            Gemini API Configuration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="geminiApiKey">Gemini API Key</Label>
            <Input
              id="geminiApiKey"
              type="password"
              value={settings.geminiApiKey}
              onChange={(e) => setSettings(prev => ({ ...prev, geminiApiKey: e.target.value }))}
              placeholder="Enter your Gemini API key"
            />
            <p className="text-sm text-muted-foreground mt-1">
              Get your API key from the <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Google AI Studio</a>
            </p>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="autoGenerate">Auto-Generate Content</Label>
              <p className="text-sm text-muted-foreground">Automatically generate content for scheduled posts</p>
            </div>
            <Switch
              id="autoGenerate"
              checked={settings.autoGenerate}
              onCheckedChange={(checked) => setSettings(prev => ({ ...prev, autoGenerate: checked }))}
            />
          </div>
        </CardContent>
      </Card>

      {/* PUBLISHING SCHEDULE */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Publishing Schedule
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="publishingDays">Publishing Days</Label>
              <div className="flex gap-2 mt-2">
                {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map((day) => (
                  <Button
                    key={day}
                    size="sm"
                    variant={settings.publishingSchedule.days.includes(day) ? 'default' : 'outline'}
                    onClick={() => {
                      const newDays = settings.publishingSchedule.days.includes(day)
                        ? settings.publishingSchedule.days.filter(d => d !== day)
                        : [...settings.publishingSchedule.days, day];
                      setSettings(prev => ({
                        ...prev,
                        publishingSchedule: { ...prev.publishingSchedule, days: newDays }
                      }));
                    }}
                  >
                    {day.charAt(0).toUpperCase() + day.slice(1, 3)}
                  </Button>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="publishingTime">Publishing Time</Label>
              <Input
                id="publishingTime"
                type="time"
                value={settings.publishingSchedule.time}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  publishingSchedule: { ...prev.publishingSchedule, time: e.target.value }
                }))}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="timezone">Timezone</Label>
            <select
              id="timezone"
              value={settings.publishingSchedule.timezone}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                publishingSchedule: { ...prev.publishingSchedule, timezone: e.target.value }
              }))}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="UTC">UTC</option>
              <option value="America/New_York">Eastern Time</option>
              <option value="America/Chicago">Central Time</option>
              <option value="America/Denver">Mountain Time</option>
              <option value="America/Los_Angeles">Pacific Time</option>
              <option value="Europe/London">London</option>
              <option value="Europe/Paris">Paris</option>
              <option value="Asia/Tokyo">Tokyo</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* DEFAULT AUTHOR */}
      <Card>
        <CardHeader>
          <CardTitle>Default Author Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="authorName">Author Name</Label>
              <Input
                id="authorName"
                value={settings.defaultAuthor.name}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  defaultAuthor: { ...prev.defaultAuthor, name: e.target.value }
                }))}
              />
            </div>
            <div>
              <Label htmlFor="authorEmail">Author Email</Label>
              <Input
                id="authorEmail"
                type="email"
                value={settings.defaultAuthor.email}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  defaultAuthor: { ...prev.defaultAuthor, email: e.target.value }
                }))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* PROMPT CONFIGURATION */}
      <PromptConfig
        prompts={prompts}
        onSavePrompt={handleSavePrompt}
        onDeletePrompt={handleDeletePrompt}
        onUpdateSettings={handleUpdateSettings}
        settings={{ prefix: settings.prefix, suffix: settings.suffix }}
      />
    </div>
  );
}
