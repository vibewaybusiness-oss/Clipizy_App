"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Youtube,
  Instagram,
  Music,
  Settings,
  Plus,
  Trash2,
  ExternalLink,
  BarChart3,
  Calendar,
  Play
} from 'lucide-react';

interface SocialAccount {
  id: string;
  platform: string;
  account_name: string;
  connected: boolean;
  created_at: string;
}

interface Platform {
  id: string;
  name: string;
  description: string;
  features: string[];
}

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  config: any;
  schedule: any;
}

export default function SocialMediaManager() {
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('accounts');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load connected accounts
      const accountsResponse = await fetch('/api/social-media/accounts', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    });
      const accountsData = await accountsResponse.json();
      setAccounts(accountsData.accounts || []);

      // Load supported platforms
      const platformsResponse = await fetch('/api/social-media/platforms', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    });
      const platformsData = await platformsResponse.json();
      setPlatforms(platformsData.platforms || []);

      // Load workflow templates
      const templatesResponse = await fetch('/api/automation/templates', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
      },
    });
      const templatesData = await templatesResponse.json();
      setTemplates(templatesData.templates || []);

    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectAccount = async (platform: string) => {
    try {
      // In a real implementation, this would redirect to OAuth flow
      const mockAuthData = {
        access_token: `mock_token_${platform}_${Date.now()}`,
        refresh_token: `mock_refresh_${platform}_${Date.now()}`,
        expires_in: 3600
      };

      const response = await fetch(`/api/social-media/connect/${platform}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(mockAuthData)
      });

      if (response.ok) {
        await loadData();
      }
    } catch (error) {
      console.error('Failed to connect account:', error);
    }
  };

  const disconnectAccount = async (accountId: string) => {
    try {
      const response = await fetch(`/api/social-media/accounts/${accountId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        await loadData();
      }
    } catch (error) {
      console.error('Failed to disconnect account:', error);
    }
  };

  const createWorkflow = async (templateId: string) => {
    try {
      const response = await fetch(`/api/automation/templates/${templateId}/create`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          enable_scheduling: true,
          customizations: {}
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Workflow created:', result);
      }
    } catch (error) {
      console.error('Failed to create workflow:', error);
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'youtube': return <Youtube className="h-5 w-5" />;
      case 'instagram': return <Instagram className="h-5 w-5" />;
      case 'tiktok': return <Music className="h-5 w-5" />;
      default: return <Settings className="h-5 w-5" />;
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'youtube': return 'bg-red-500';
      case 'instagram': return 'bg-pink-500';
      case 'tiktok': return 'bg-black';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Social Media Manager</h1>
          <p className="text-gray-600">Connect accounts and automate content publishing</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="accounts">Connected Accounts</TabsTrigger>
          <TabsTrigger value="platforms">Available Platforms</TabsTrigger>
          <TabsTrigger value="automation">Automation</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="accounts" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {accounts.map((account) => (
              <Card key={account.id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`p-2 rounded-full ${getPlatformColor(account.platform)} text-white`}>
                        {getPlatformIcon(account.platform)}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{account.account_name}</CardTitle>
                        <CardDescription className="capitalize">{account.platform}</CardDescription>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Connected
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Analytics
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => disconnectAccount(account.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="platforms" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {platforms.map((platform) => {
              const isConnected = accounts.some(acc => acc.platform === platform.id);
              return (
                <Card key={platform.id} className="relative">
                  <CardHeader>
                    <div className="flex items-center space-x-3">
                      <div className={`p-3 rounded-full ${getPlatformColor(platform.id)} text-white`}>
                        {getPlatformIcon(platform.id)}
                      </div>
                      <div>
                        <CardTitle className="text-xl">{platform.name}</CardTitle>
                        <CardDescription>{platform.description}</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-1">
                        {platform.features.map((feature) => (
                          <Badge key={feature} variant="outline" className="text-xs">
                            {feature.replace('_', ' ')}
                          </Badge>
                        ))}
                      </div>
                      <Button
                        className="w-full"
                        onClick={() => connectAccount(platform.id)}
                        disabled={isConnected}
                      >
                        {isConnected ? 'Connected' : 'Connect Account'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="automation" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {templates.map((template) => (
              <Card key={template.id} className="relative">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className="p-3 rounded-full bg-blue-100 text-blue-600">
                      <Calendar className="h-6 w-6" />
                    </div>
                    <div>
                      <CardTitle className="text-xl">{template.name}</CardTitle>
                      <CardDescription>{template.description}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="text-sm text-gray-600">
                      <p><strong>Schedule:</strong> {template.schedule.type}</p>
                      <p><strong>Platforms:</strong> {template.config.publish_platforms?.join(', ') || 'None'}</p>
                    </div>
                    <Button
                      className="w-full"
                      onClick={() => createWorkflow(template.id)}
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Create Workflow
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Workflows</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0</div>
                <p className="text-xs text-gray-600">+0 from last month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Videos Published</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0</div>
                <p className="text-xs text-gray-600">+0 from last month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0%</div>
                <p className="text-xs text-gray-600">No data available</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Active Accounts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{accounts.length}</div>
                <p className="text-xs text-gray-600">Connected platforms</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
