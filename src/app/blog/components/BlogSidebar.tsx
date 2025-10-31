"use client";

import { BlogPost, BlogCategory, BlogTag } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Clock, Tag } from 'lucide-react';
import Link from 'next/link';

interface BlogSidebarProps {
  popularPosts: BlogPost[];
  recentPosts: BlogPost[];
  categories: BlogCategory[];
  tags: BlogTag[];
}

export function BlogSidebar({
  popularPosts,
  recentPosts,
  categories,
  tags
}: BlogSidebarProps) {
  return (
    <div className="space-y-8">
      {/* POPULAR POSTS */}
      <Card className="border-border/50 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg font-bold text-foreground tracking-tight">
            <TrendingUp className="w-5 h-5 text-primary" />
            Popular Posts
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {popularPosts.map((post, index) => (
            <div key={post.id} className="group flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/10 rounded-full flex items-center justify-center text-sm font-bold text-primary">
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <Link
                  href={`/blog/${post.slug}`}
                  className="text-sm font-semibold hover:text-primary transition-colors line-clamp-2 group-hover:underline text-foreground/90 leading-snug"
                >
                  {post.title}
                </Link>
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2">
                  <span className="flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    {post.views.toLocaleString()}
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <span>❤️</span>
                    {post.likes}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* RECENT POSTS */}
      <Card className="border-border/50 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg font-bold text-foreground tracking-tight">
            <Clock className="w-5 h-5 text-primary" />
            Recent Posts
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {recentPosts.map((post) => (
            <div key={post.id} className="group flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
              {post.featuredImage ? (
                <img
                  src={post.featuredImage}
                  alt={post.title}
                  className="w-12 h-12 object-cover rounded-lg shadow-sm group-hover:shadow-md transition-shadow"
                />
              ) : (
                <div className="w-12 h-12 bg-gradient-to-br from-muted to-muted/50 rounded-lg flex items-center justify-center">
                  <Clock className="w-5 h-5 text-muted-foreground" />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <Link
                  href={`/blog/${post.slug}`}
                  className="text-sm font-medium hover:text-primary transition-colors line-clamp-2 group-hover:underline"
                >
                  {post.title}
                </Link>
                <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(post.publishedAt).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* CATEGORIES */}
      <Card className="border-border/50 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-bold text-foreground tracking-tight">Categories</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {categories.map((category) => (
            <div key={category.id} className="group flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 transition-colors">
              <Link
                href={`/blog?category=${category.slug}`}
                className="text-sm font-medium hover:text-primary transition-colors group-hover:underline"
              >
                {category.name}
              </Link>
              <Badge variant="secondary" className="text-xs px-2 py-1">
                {category.postCount}
              </Badge>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* TAGS */}
      <Card className="border-border/50 shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg font-bold text-foreground tracking-tight">
            <Tag className="w-5 h-5 text-primary" />
            Popular Tags
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {tags.slice(0, 10).map((tag) => (
              <Link key={tag.id} href={`/blog?tag=${tag.slug}`}>
                <Badge
                  variant="outline"
                  className="text-xs px-3 py-1 hover:bg-primary/10 hover:border-primary/30 transition-all cursor-pointer"
                >
                  {tag.name} ({tag.postCount})
                </Badge>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
