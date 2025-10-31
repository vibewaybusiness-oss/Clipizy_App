"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { 
  Instagram, 
  Youtube, 
  Video,
  Link as LinkIcon,
  Unlink,
  Share2,
  Tag,
  Hash
} from "lucide-react";
import { useToast } from "@/hooks/ui/use-toast";
import { getBackendUrl } from "@/lib/config";

interface SocialAccount {
  id: string;
  platform: string;
  username: string;
  displayName: string;
  avatar: string;
  isConnected: boolean;
  connectedAt?: string;
}

interface SocialSettings {
  autoTagClipizi: boolean;
  includeWatermark: boolean;
  autoPost: {
    youtube: boolean;
    instagram: boolean;
    tiktok: boolean;
  };
  postDelay: number; // minutes
  includeHashtags: boolean;
  customHashtags: string;
  tagFriends: boolean;
  crossPost: boolean;
}

const socialPlatforms = [
  { id: 'youtube', name: 'YouTube', icon: Youtube, color: 'bg-red-500' },
  { id: 'instagram', name: 'Instagram', icon: Instagram, color: 'bg-gradient-to-r from-purple-500 to-pink-500' },
  { id: 'tiktok', name: 'TikTok', icon: Video, color: 'bg-black' },
];

export default function SocialMediaTab() {
  const { toast } = useToast();
  const [socialAccounts, setSocialAccounts] = useState<SocialAccount[]>([]);
  const [socialSettings, setSocialSettings] = useState<SocialSettings>({
    autoTagClipizi: true,
    includeWatermark: true,
    autoPost: {
      youtube: false,
      instagram: false,
      tiktok: false
    },
    postDelay: 5,
    includeHashtags: true,
    customHashtags: "#music #clipizy #ai",
    tagFriends: false,
    crossPost: false
  });

  useEffect(() => {
    loadSocialData();

    // Add beforeunload event to save to database
    const handleBeforeUnload = () => {
      saveToDatabase();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []); // Empty dependency array to run only once

  const loadSocialData = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Load connected social accounts
      const accountsResponse = await fetch(`${getBackendUrl()}/api/social-media/accounts`, { headers });
      if (accountsResponse.ok) {
        const accountsData = await accountsResponse.json();
        setSocialAccounts(accountsData.accounts || []);
      }

      // Load social settings from backend
      const settingsResponse = await fetch(`${getBackendUrl()}/api/auth/social-settings`, { headers });
      if (settingsResponse.ok) {
        const settingsData = await settingsResponse.json();
        if (settingsData.success && settingsData.settings) {
          setSocialSettings(settingsData.settings);
          // localStorage removed - backend storage only
        }
      }
    } catch (error) {
      console.error('Error loading social data:', error);
    }
  };

  const handleSocialSettingsChange = (field: keyof SocialSettings, value: boolean | string | number) => {
    const newSocialSettings = {
      ...socialSettings,
      [field]: value
    };
    
    setSocialSettings(newSocialSettings);
    // localStorage removed - backend storage only
  };

  const handleAutoPostChange = (platform: string, checked: boolean) => {
    const newSocialSettings = {
      ...socialSettings,
      autoPost: {
        ...socialSettings.autoPost,
        [platform]: checked
      }
    };
    
    setSocialSettings(newSocialSettings);
    // localStorage removed - backend storage only
  };

  const handleConnectAccount = async (platform: string) => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Get OAuth URL from backend
      const response = await fetch(`${getBackendUrl()}/api/social-media/connect/${platform}`, { headers });
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.auth_url) {
          // Redirect to OAuth URL
          window.location.href = data.auth_url;
        } else {
          throw new Error('Failed to get OAuth URL');
        }
      } else {
        throw new Error('Failed to initiate OAuth flow');
      }
    } catch (error) {
      console.error('Error connecting account:', error);
      toast({
        title: "Error",
        description: "Failed to connect account",
        variant: "destructive"
      });
    }
  };

  const handleDisconnectAccount = async (accountId: string) => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${getBackendUrl()}/api/social-media/accounts/${accountId}`, {
        method: 'DELETE',
        headers
      });

      if (response.ok) {
        setSocialAccounts(prev => 
          prev.map(account => 
            account.id === accountId 
              ? { ...account, isConnected: false, connectedAt: undefined }
              : account
          )
        );
        toast({
          title: "Success",
          description: "Account disconnected successfully"
        });
      } else {
        throw new Error('Failed to disconnect account');
      }
    } catch (error) {
      console.error('Error disconnecting account:', error);
      toast({
        title: "Error",
        description: "Failed to disconnect account",
        variant: "destructive"
      });
    }
  };

  const saveToDatabase = async () => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      await fetch(`${getBackendUrl()}/api/auth/social-settings`, {
        method: 'PUT',
        headers,
        body: JSON.stringify(socialSettings),
      });
    } catch (error) {
      console.error('Error saving social settings to database:', error);
    }
  };

  const getAccountStatus = (platform: string) => {
    const account = socialAccounts.find(acc => acc.platform === platform);
    return account?.isConnected || false;
  };

  const getConnectedAccount = (platform: string) => {
    return socialAccounts.find(acc => acc.platform === platform && acc.isConnected);
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      {/* SOCIAL MEDIA TITLE */}
      <div className="flex items-center gap-2 p-4 bg-muted/20 rounded-lg border border-border">
        <div className="p-1.5 rounded-md bg-primary/10">
          <Share2 className="w-4 h-4 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">Social Media</h2>
          <p className="text-sm text-muted-foreground">Connect your social media accounts and manage posting preferences</p>
        </div>
      </div>

      {/* ALL SETTINGS IN SINGLE DIV */}
      <div className="space-y-6 flex-1 overflow-auto">
        {/* SOCIAL MEDIA PLATFORMS */}
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-md bg-blue-500/10">
                <Share2 className="w-4 h-4 text-blue-500" />
              </div>
              <div>
                <h3 className="text-base font-semibold">Social Media Platforms</h3>
                <p className="text-xs text-muted-foreground">Connect your social media accounts and manage posting preferences</p>
              </div>
            </div>

            <div className="space-y-3">
              {socialPlatforms.map((platform) => {
                const Icon = platform.icon;
                const isConnected = getAccountStatus(platform.id);
                const connectedAccount = getConnectedAccount(platform.id);

                return (
                  <div key={platform.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                    <div className={`flex items-center space-x-3 ${!isConnected ? 'opacity-50' : ''}`}>
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isConnected ? platform.color : 'bg-gray-400'} shadow-md`}>
                        <Icon className={`w-5 h-5 ${isConnected ? 'text-white' : 'text-gray-600'}`} />
                      </div>
                      <div className="flex-1">
                        <h4 className={`text-sm font-medium ${!isConnected ? 'text-muted-foreground' : ''}`}>{platform.name}</h4>
                        {isConnected && connectedAccount ? (
                          <div className="flex items-center space-x-2 mt-0.5">
                            <Badge variant="secondary" className="text-xs">
                              <LinkIcon className="w-3 h-3 mr-1" />
                              Connected
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              @{connectedAccount.username}
                            </span>
                          </div>
                        ) : (
                          <p className="text-xs text-muted-foreground mt-0.5">Not connected</p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <div className={`flex items-center space-x-2 ${!isConnected ? 'opacity-50' : ''}`}>
                        <Switch
                          checked={socialSettings.autoPost[platform.id as keyof typeof socialSettings.autoPost]}
                          onCheckedChange={(checked) => handleAutoPostChange(platform.id, checked)}
                          disabled={!isConnected}
                        />
                        <Label className={`text-xs font-medium ${!isConnected ? 'text-muted-foreground' : ''}`}>Auto-post</Label>
                      </div>
                      
                      {isConnected ? (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDisconnectAccount(connectedAccount!.id)}
                          className="px-3 h-8"
                        >
                          <Unlink className="w-3 h-3 mr-1" />
                          Disconnect
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => handleConnectAccount(platform.id)}
                          className="px-3 h-8"
                        >
                          <LinkIcon className="w-3 h-3 mr-1" />
                          Connect
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* AUTO-TAGGING SETTINGS */}
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-md bg-orange-500/10">
                <Tag className="w-4 h-4 text-orange-500" />
              </div>
              <div>
                <h3 className="text-base font-semibold">Auto-Tagging Settings</h3>
                <p className="text-xs text-muted-foreground">Configure automatic tagging for your content</p>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
              <div className="flex items-center space-x-3">
                <div className="p-1.5 rounded-md bg-blue-500/10">
                  <Tag className="w-4 h-4 text-blue-500" />
                </div>
                <div className="space-y-0.5">
                  <Label className="text-sm font-medium">Auto-tag @clipizi</Label>
                  <p className="text-xs text-muted-foreground">
                    Automatically tag @clipizi when publishing content
                  </p>
                </div>
              </div>
              <Switch
                checked={socialSettings.autoTagClipizi}
                onCheckedChange={(checked) => handleSocialSettingsChange('autoTagClipizi', checked)}
              />
            </div>
          </div>
        </div>

        {/* HASHTAGS SETTINGS */}
        <div className="bg-card border border-border rounded-lg p-4 flex-1 flex flex-col">
          <div className="space-y-4 flex-1 flex flex-col">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-md bg-green-500/10">
                <Hash className="w-4 h-4 text-green-500" />
              </div>
              <div>
                <h3 className="text-base font-semibold">Hashtag Settings</h3>
                <p className="text-xs text-muted-foreground">Manage hashtag preferences for your posts</p>
              </div>
            </div>

            <div className="space-y-4 flex-1">
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                <div className="flex items-center space-x-3">
                  <div className="p-1.5 rounded-md bg-purple-500/10">
                    <Hash className="w-4 h-4 text-purple-500" />
                  </div>
                  <div className="space-y-0.5">
                    <Label className="text-sm font-medium">Include Hashtags</Label>
                    <p className="text-xs text-muted-foreground">
                      Automatically include hashtags in posts
                    </p>
                  </div>
                </div>
                <Switch
                  checked={socialSettings.includeHashtags}
                  onCheckedChange={(checked) => handleSocialSettingsChange('includeHashtags', checked)}
                />
              </div>

              {socialSettings.includeHashtags && (
                <div className="space-y-2">
                  <div>
                    <Label htmlFor="customHashtags" className="text-xs font-medium">Custom Hashtags</Label>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Separate hashtags with spaces
                    </p>
                  </div>
                  <input
                    id="customHashtags"
                    type="text"
                    value={socialSettings.customHashtags}
                    onChange={(e) => handleSocialSettingsChange('customHashtags', e.target.value)}
                    placeholder="#music #clipizy #ai"
                    className="w-full px-3 py-2 border border-input rounded-lg bg-background text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
