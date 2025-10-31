"use client";

import { BlogPost, BlogCategory, BlogTag } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TrendingUp, Clock, Tag, ArrowRight, Play, Star } from 'lucide-react';
import Link from 'next/link';

interface BlogSidebarNewProps {
  popularPosts: BlogPost[];
  recentPosts: BlogPost[];
  categories: BlogCategory[];
  tags: BlogTag[];
}

export function BlogSidebarNew({
  popularPosts,
  recentPosts,
  categories,
  tags
}: BlogSidebarNewProps) {
  return (
    <div className="space-y-6">
      {/* CTA Card */}
      <Card className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-800">
        <CardContent className="p-6">
          <div className="text-center space-y-4">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto">
              <Play className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Ready to Create?</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Start creating your first AI music video in just 5 minutes
              </p>
              <Button asChild className="w-full gap-2">
                <Link href="/dashboard/create">
                  Get Started Free
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Popular Posts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <TrendingUp className="w-5 h-5" />
            Most Popular
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {popularPosts.slice(0, 3).map((post, index) => (
            <div key={post.id} className="flex items-start gap-3 group">
              <div className="flex-shrink-0 w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center text-xs font-semibold text-primary">
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <Link
                  href={`/blog/${post.slug}`}
                  className="text-sm font-medium hover:text-primary transition-colors line-clamp-2 group-hover:underline"
                >
                  {post.title}
                </Link>
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                  <span>{post.views.toLocaleString()} views</span>
                  <span>•</span>
                  <span>{post.readTime} min read</span>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Categories */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Browse by Topic</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {categories.map((category) => (
            <Link
              key={category.id}
              href={`/blog?category=${category.slug}`}
              className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 transition-colors group"
            >
              <span className="text-sm font-medium group-hover:text-primary">
                {category.name}
              </span>
              <Badge variant="secondary" className="text-xs">
                {category.postCount}
              </Badge>
            </Link>
          ))}
        </CardContent>
      </Card>

      {/* Quick Start Guide */}
      <Card className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Star className="w-5 h-5 text-green-600 dark:text-green-400" />
            Quick Start Guide
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-sm space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>Upload your audio file</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>Choose a visual style</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>Customize and export</span>
            </div>
          </div>
          <Button asChild variant="outline" size="sm" className="w-full gap-2 mt-4">
            <Link href="/blog/ai-music-video-generator-5-minutes">
              Read Full Guide
              <ArrowRight className="w-3 h-3" />
            </Link>
          </Button>
        </CardContent>
      </Card>

      {/* Popular Tags */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Tag className="w-5 h-5" />
            Popular Tags
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {tags.slice(0, 8).map((tag) => (
              <Link key={tag.id} href={`/blog?tag=${tag.slug}`}>
                <Badge
                  variant="outline"
                  className="text-xs hover:bg-primary/10 hover:text-primary transition-colors cursor-pointer"
                >
                  {tag.name}
                </Badge>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
