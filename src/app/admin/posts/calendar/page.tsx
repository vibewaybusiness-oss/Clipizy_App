"use client";

import { useState } from 'react';
import { ContentCalendar as ContentCalendarComponent } from '@/components/calendar/ContentCalendar';
import { GeminiGenerator } from '@/components/calendar/GeminiGenerator';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { StatsCard, QuickActions } from '@/app/admin/components';
import { useContentCalendar } from '@/hooks/admin';
import {
  Calendar,
  Bot,
  BarChart3,
  Download,
  Upload,
  RefreshCw
} from 'lucide-react';

export default function ContentCalendarPage() {
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [showGenerator, setShowGenerator] = useState(false);
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const { calendar, stats, updatePost, setCalendar } = useContentCalendar();

  const handlePostClick = (post: any) => {
    setSelectedPost(post);
    setShowGenerator(false);
  };

  const handleGeneratePost = (post: any) => {
    setSelectedPost(post);
    setShowGenerator(true);
  };

  const handleEditPost = (post: any) => {
    // Navigate to edit page or open edit modal
    console.log('Edit post:', post);
  };

  const handleContentGenerated = (content: string) => {
    if (selectedPost) {
      const updatedPost = {
        ...selectedPost,
        content,
        excerpt: content.split('\n\n')[0] || content.substring(0, 200),
        status: 'draft'
      };

      updatePost(selectedPost.id, updatedPost);
    }
  };

  const handleSavePost = (post: any) => {
    updatePost(post.id, post);
    setShowGenerator(false);
    setSelectedPost(null);
  };

  if (showGenerator && selectedPost) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            onClick={() => setShowGenerator(false)}
          >
            ← Back to Calendar
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Generate Content</h1>
            <p className="text-muted-foreground">Use AI to generate blog post content</p>
          </div>
        </div>

        <GeminiGenerator
          post={selectedPost}
          onGenerate={handleContentGenerated}
          onSave={handleSavePost}
          apiKey={geminiApiKey}
          onApiKeyChange={setGeminiApiKey}
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Content Calendar</h1>
          <p className="text-muted-foreground">Plan, generate, and manage your blog content</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm">
            <Upload className="w-4 h-4 mr-2" />
            Import
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* QUICK STATS */}
      <div className="grid grid-cols-3 gap-4">
        <StatsCard
          title="Total Posts"
          value={stats.total}
          icon={Calendar}
          color="blue"
        />
        <StatsCard
          title="Published"
          value={stats.published}
          icon={BarChart3}
          color="green"
        />
        <StatsCard
          title="Drafts"
          value={stats.draft}
          icon={Bot}
          color="yellow"
        />
      </div>

      {/* CALENDAR COMPONENT */}
      <ContentCalendarComponent
        calendar={calendar}
        onPostClick={handlePostClick}
        onGeneratePost={handleGeneratePost}
        onEditPost={handleEditPost}
      />
    </div>
  );
}
