"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  TrendingUp,
  Eye,
  Heart,
  Users,
  Calendar,
  BarChart3,
  FileText,
  Clock
} from 'lucide-react';

interface AnalyticsData {
  totalPosts: number;
  publishedPosts: number;
  draftPosts: number;
  scheduledPosts: number;
  totalViews: number;
  totalLikes: number;
  totalComments: number;
  averageReadTime: number;
  topPosts: Array<{
    title: string;
    views: number;
    likes: number;
    publishedAt: string;
  }>;
  monthlyStats: Array<{
    month: string;
    posts: number;
    views: number;
    likes: number;
  }>;
}

export default function AdminAnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/v1/content/blog?status=all&limit=100');
        if (!response.ok) {
          throw new Error('Failed to fetch analytics data');
        }
        const result = await response.json();

        // Process the data for analytics
        const posts = result.posts;
        const publishedPosts = posts.filter((post: any) => post.status === 'published');
        const draftPosts = posts.filter((post: any) => post.status === 'draft');
        const scheduledPosts = posts.filter((post: any) => post.status === 'scheduled');

        const totalViews = posts.reduce((sum: number, post: any) => sum + post.views, 0);
        const totalLikes = posts.reduce((sum: number, post: any) => sum + post.likes, 0);
        const averageReadTime = posts.reduce((sum: number, post: any) => sum + post.readTime, 0) / posts.length;

        const topPosts = publishedPosts
          .sort((a: any, b: any) => b.views - a.views)
          .slice(0, 5)
          .map((post: any) => ({
            title: post.title,
            views: post.views,
            likes: post.likes,
            publishedAt: post.publishedAt
          }));

        // Generate mock monthly stats
        const monthlyStats = [
          { month: 'Jan 2024', posts: 3, views: 1250, likes: 89 },
          { month: 'Feb 2024', posts: 2, views: 2100, likes: 156 },
          { month: 'Mar 2024', posts: 1, views: 890, likes: 67 },
          { month: 'Apr 2024', posts: 0, views: 0, likes: 0 },
        ];

        setData({
          totalPosts: posts.length,
          publishedPosts: publishedPosts.length,
          draftPosts: draftPosts.length,
          scheduledPosts: scheduledPosts.length,
          totalViews,
          totalLikes,
          totalComments: 0, // Mock data
          averageReadTime: Math.round(averageReadTime),
          topPosts,
          monthlyStats
        });
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [timeRange]);

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 bg-muted rounded"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-64 bg-muted rounded"></div>
            <div className="h-64 bg-muted rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold mb-4">Error Loading Analytics</h1>
        <p className="text-muted-foreground">Failed to load analytics data.</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analytics</h1>
          <p className="text-muted-foreground">Monitor your blog performance and engagement</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={timeRange === '7d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeRange('7d')}
          >
            7 Days
          </Button>
          <Button
            variant={timeRange === '30d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeRange('30d')}
          >
            30 Days
          </Button>
          <Button
            variant={timeRange === '90d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeRange('90d')}
          >
            90 Days
          </Button>
        </div>
      </div>

      {/* KEY METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Posts</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.totalPosts}</div>
            <p className="text-xs text-muted-foreground">
              {data.publishedPosts} published, {data.draftPosts} drafts
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.totalViews.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Likes</CardTitle>
            <Heart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.totalLikes}</div>
            <p className="text-xs text-muted-foreground">
              {data.totalViews > 0 ? Math.round(data.totalLikes / data.totalViews * 100) : 0}% engagement
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Read Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.averageReadTime} min</div>
            <p className="text-xs text-muted-foreground">
              Per article
            </p>
          </CardContent>
        </Card>
      </div>

      {/* CHARTS AND DETAILS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* TOP POSTS */}
        <Card>
          <CardHeader>
            <CardTitle>Top Performing Posts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.topPosts.map((post, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded border">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{post.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(post.publishedAt).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      <span>{post.views.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Heart className="w-4 h-4" />
                      <span>{post.likes}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* MONTHLY STATS */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.monthlyStats.map((stat, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="text-sm font-medium">{stat.month}</div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>{stat.posts} posts</span>
                    <span>{stat.views.toLocaleString()} views</span>
                    <span>{stat.likes} likes</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* CONTENT STATUS */}
      <Card>
        <CardHeader>
          <CardTitle>Content Status Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">{data.publishedPosts}</div>
              <p className="text-sm text-muted-foreground">Published Posts</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">{data.draftPosts}</div>
              <p className="text-sm text-muted-foreground">Draft Posts</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">{data.scheduledPosts}</div>
              <p className="text-sm text-muted-foreground">Scheduled Posts</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
