"use client";

import { useState, useEffect } from 'react';
import { BlogPost } from '@/types';
import { BlogPost as BlogPostComponent } from '@/app/blog/components/BlogPost';
import { BlogSidebarNew } from '@/app/blog/components/BlogSidebarNew';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';

interface BlogPostPageClientProps {
  params: { slug: string };
}

export function BlogPostPageClient({ params }: BlogPostPageClientProps) {
  const [post, setPost] = useState<BlogPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [relatedPosts, setRelatedPosts] = useState<BlogPost[]>([]);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/v1/content/blog/${params.slug}`);

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('Blog post not found');
          }
          throw new Error('Failed to fetch blog post');
        }

        const postData = await response.json();
        setPost(postData);

        // Fetch related posts (same category)
        const relatedResponse = await fetch(`/api/v1/content/blog?category=${postData.category}&limit=3`);
        if (relatedResponse.ok) {
          const relatedData = await relatedResponse.json();
          setRelatedPosts(relatedData.posts.filter((p: BlogPost) => p.slug !== params.slug));
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [params.slug]);

  const handleLike = async (postId: string) => {
    // In production, this would make an API call to like the post
    console.log('Liked post:', postId);
  };

  const handleShare = async (postId: string) => {
    // In production, this would track share analytics
    console.log('Shared post:', postId);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="animate-pulse space-y-8">
            <div className="h-8 bg-muted rounded w-1/4"></div>
            <div className="h-4 bg-muted rounded w-1/2"></div>
            <div className="h-64 bg-muted rounded"></div>
            <div className="space-y-4">
              <div className="h-4 bg-muted rounded"></div>
              <div className="h-4 bg-muted rounded"></div>
              <div className="h-4 bg-muted rounded w-3/4"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-destructive mb-4">
                <FileText className="w-12 h-12 mx-auto" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Post Not Found</h3>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button asChild>
                <Link href="/blog">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Blog
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!post) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* MAIN CONTENT WITH SIDEBAR */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* BLOG POST HEADER - Spans both columns */}
          <div className="lg:col-span-4 mb-8">
            <BlogPostComponent
              post={post}
              onLike={handleLike}
              onShare={handleShare}
              showHeaderOnly={true}
            />
          </div>

          {/* MAIN CONTENT */}
          <div className="lg:col-span-3">
            {/* FEATURED IMAGE AND CONTENT */}
            <BlogPostComponent
              post={post}
              onLike={handleLike}
              onShare={handleShare}
              showContentOnly={true}
            />

            {/* RELATED POSTS */}
            {relatedPosts.length > 0 && (
              <div className="mt-16">
                <h2 className="text-2xl font-bold mb-6">Related Posts</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {relatedPosts.map((relatedPost) => (
                    <Card key={relatedPost.id} className="group hover:shadow-lg transition-all duration-300">
                      {relatedPost.featuredImage && (
                        <div className="relative overflow-hidden rounded-t-lg h-48">
                          <img
                            src={relatedPost.featuredImage}
                            alt={relatedPost.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          />
                        </div>
                      )}
                      <CardContent className="p-6">
                        <h3 className="font-semibold group-hover:text-primary transition-colors mb-2">
                          <Link href={`/blog/${relatedPost.slug}`} className="hover:underline">
                            {relatedPost.title}
                          </Link>
                        </h3>
                        <p className="text-sm text-muted-foreground mb-3">
                          {relatedPost.excerpt}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{relatedPost.readTime} min read</span>
                          <span>•</span>
                          <span>{relatedPost.views.toLocaleString()} views</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* SIDEBAR - Positioned to align with featured image */}
          <div className="lg:col-span-1">
            <div className="sticky top-32 max-h-[calc(100vh-8rem)] overflow-y-auto scrollbar-hide">
              <BlogSidebarNew
                popularPosts={[post]} // In production, fetch actual popular posts
                recentPosts={[post]} // In production, fetch actual recent posts
                categories={[{ id: '1', name: post.category, slug: post.category.toLowerCase(), description: '', color: '#3B82F6', postCount: 1 }]}
                tags={post.tags.map((tag, index) => ({ id: index.toString(), name: tag, slug: tag.toLowerCase(), postCount: 1 }))}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
