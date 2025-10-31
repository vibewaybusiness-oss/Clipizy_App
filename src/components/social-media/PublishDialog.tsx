"use client";

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Youtube,
  Instagram,
  Music,
  Upload,
  Settings,
  Calendar,
  Hash
} from 'lucide-react';

interface PublishDialogProps {
  exportId: string;
  exportTitle?: string;
  children: React.ReactNode;
}

interface Platform {
  id: string;
  name: string;
  connected: boolean;
}

interface PublishOptions {
  title: string;
  description: string;
  tags: string[];
  privacy: 'public' | 'unlisted' | 'private';
  thumbnail_url?: string;
  schedule_time?: string;
}

export default function PublishDialog({ exportId, exportTitle, children }: PublishDialogProps) {
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [publishOptions, setPublishOptions] = useState<PublishOptions>({
    title: exportTitle || '',
    description: '',
    tags: [],
    privacy: 'public'
  });
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    loadPlatforms();
  }, []);

  const loadPlatforms = async () => {
    try {
      const response = await fetch('/api/v1/integrations/social-media/accounts', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    });
      const data = await response.json();

      const platformData = data.accounts.map((account: any) => ({
        id: account.platform,
        name: account.platform.charAt(0).toUpperCase() + account.platform.slice(1),
        connected: account.connected
      }));

      setPlatforms(platformData);
    } catch (error) {
      console.error('Failed to load platforms:', error);
    }
  };

  const handlePlatformToggle = (platformId: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !publishOptions.tags.includes(tagInput.trim())) {
      setPublishOptions(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setPublishOptions(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  const handlePublish = async () => {
    if (selectedPlatforms.length === 0) {
      alert('Please select at least one platform');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/v1/integrations/social-media/${exportId}/publish`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          platforms: selectedPlatforms,
          publish_options: publishOptions
        })
      });

      const result = await response.json();

      if (result.success) {
        alert('Video published successfully!');
        setOpen(false);
      } else {
        alert(`Failed to publish: ${result.error}`);
      }
    } catch (error) {
      console.error('Failed to publish:', error);
      alert('Failed to publish video');
    } finally {
      setLoading(false);
    }
  };

  const getPlatformIcon = (platformId: string) => {
    switch (platformId) {
      case 'youtube': return <Youtube className="h-5 w-5" />;
      case 'instagram': return <Instagram className="h-5 w-5" />;
      case 'tiktok': return <Music className="h-5 w-5" />;
      default: return <Settings className="h-5 w-5" />;
    }
  };

  const getPlatformColor = (platformId: string) => {
    switch (platformId) {
      case 'youtube': return 'bg-red-500';
      case 'instagram': return 'bg-pink-500';
      case 'tiktok': return 'bg-black';
      default: return 'bg-gray-500';
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Publish Video</DialogTitle>
          <DialogDescription>
            Select platforms and configure publishing options for your video.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Platform Selection */}
          <div className="space-y-3">
            <Label className="text-base font-medium">Select Platforms</Label>
            <div className="grid gap-3 md:grid-cols-3">
              {platforms.map((platform) => (
                <Card
                  key={platform.id}
                  className={`cursor-pointer transition-all ${
                    selectedPlatforms.includes(platform.id)
                      ? 'ring-2 ring-blue-500 bg-blue-50'
                      : 'hover:bg-gray-50'
                  } ${!platform.connected ? 'opacity-50' : ''}`}
                  onClick={() => platform.connected && handlePlatformToggle(platform.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-full ${getPlatformColor(platform.id)} text-white`}>
                        {getPlatformIcon(platform.id)}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium">{platform.name}</p>
                        <p className="text-sm text-gray-500">
                          {platform.connected ? 'Connected' : 'Not connected'}
                        </p>
                      </div>
                      <Checkbox
                        checked={selectedPlatforms.includes(platform.id)}
                        disabled={!platform.connected}
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Publishing Options */}
          <div className="space-y-4">
            <Label className="text-base font-medium">Publishing Options</Label>

            <div className="space-y-3">
              <div>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={publishOptions.title}
                  onChange={(e) => setPublishOptions(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Enter video title"
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={publishOptions.description}
                  onChange={(e) => setPublishOptions(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Enter video description"
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="privacy">Privacy</Label>
                <select
                  id="privacy"
                  value={publishOptions.privacy}
                  onChange={(e) => setPublishOptions(prev => ({ ...prev, privacy: e.target.value as any }))}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="public">Public</option>
                  <option value="unlisted">Unlisted</option>
                  <option value="private">Private</option>
                </select>
              </div>

              <div>
                <Label>Tags</Label>
                <div className="space-y-2">
                  <div className="flex space-x-2">
                    <Input
                      value={tagInput}
                      onChange={(e) => setTagInput(e.target.value)}
                      placeholder="Add a tag"
                      onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                    />
                    <Button onClick={handleAddTag} size="sm">
                      <Hash className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {publishOptions.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="flex items-center space-x-1">
                        <span>{tag}</span>
                        <button
                          onClick={() => handleRemoveTag(tag)}
                          className="ml-1 hover:text-red-500"
                        >
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handlePublish}
              disabled={loading || selectedPlatforms.length === 0}
              className="flex items-center space-x-2"
            >
              <Upload className="h-4 w-4" />
              <span>{loading ? 'Publishing...' : 'Publish Video'}</span>
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
