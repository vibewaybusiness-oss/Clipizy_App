"use client";

import { BlogPost } from '@/types';
import Link from 'next/link';
import { Calendar, Clock, Eye, Heart, User } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';

interface BlogCardProps {
  post: BlogPost;
  featured?: boolean;
}

export function BlogCard({ post, featured = false }: BlogCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Card className={`group hover:shadow-xl transition-all duration-300 border-border/50 hover:border-primary/20 ${
      featured ? 'md:col-span-2 xl:col-span-1' : ''
    }`}>
      {post.featuredImage && (
        <div className={`relative overflow-hidden rounded-t-lg ${
          featured ? 'h-64' : 'h-48'
        }`}>
          <img
            src={post.featuredImage}
            alt={post.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
        </div>
      )}

      <CardHeader className={post.featuredImage ? 'pt-6' : 'pt-6'}>
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
          <User className="w-4 h-4" />
          <span>{post.author.name}</span>
          <span>•</span>
          <Calendar className="w-4 h-4" />
          <span>{formatDate(post.publishedAt)}</span>
        </div>

        <h3 className={`font-semibold group-hover:text-primary transition-colors leading-tight ${
          featured ? 'text-xl mb-3' : 'text-lg mb-3'
        }`}>
          <Link href={`/blog/${post.slug}`} className="hover:underline">
            {post.title}
          </Link>
        </h3>

        <p className={`text-muted-foreground leading-relaxed ${
          featured ? 'text-base' : 'text-sm'
        }`}>
          {post.excerpt}
        </p>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="flex flex-wrap gap-2 mb-4">
          <Badge variant="secondary" className="text-xs px-2 py-1">
            {post.category}
          </Badge>
          {post.tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs px-2 py-1">
              {tag}
            </Badge>
          ))}
        </div>
      </CardContent>

      <CardFooter className="pt-0 pb-6 flex items-center justify-between text-sm text-muted-foreground">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            <span>{post.readTime} min read</span>
          </div>
          <div className="flex items-center gap-1">
            <Eye className="w-4 h-4" />
            <span>{post.views.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <Heart className="w-4 h-4" />
            <span>{post.likes}</span>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
}
