"use client";

import type { BlogPost } from '@/types';
import { Calendar, Clock, Eye, Heart, User, ArrowLeft, Share2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { useState } from 'react';

// Convert markdown to HTML with proper table support
function convertMarkdownToHtml(content: string): string {
  let html = content;

  // Convert markdown tables to HTML
  const tableRegex = /\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|\n\|------\|----------\|--------------\|----------------\|-------------\|\n((?:\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|[^|]+\|\n?)+)/g;

  html = html.replace(tableRegex, (match: string, header1: string, header2: string, header3: string, header4: string, header5: string, rows: string) => {
    const tableRows = rows.trim().split('\n').filter((row: string) => row.trim());
    const tableBody = tableRows.map((row: string, rowIndex: number) => {
      const cells = row.split('|').slice(1, -1).map((cell: string) => cell.trim());
      const isEven = rowIndex % 2 === 0;
      return `<tr class="${isEven ? 'bg-card/80' : 'bg-muted/20'} hover:bg-primary/5 transition-all duration-200">${cells.map((cell: string, cellIndex: number) => `<td class="p-6 text-base ${cellIndex === 0 ? 'font-bold text-foreground' : 'text-foreground/80'} leading-relaxed">${cell}</td>`).join('')}</tr>`;
    }).join('');

    return `
      <div class="overflow-x-auto my-12 rounded-2xl border border-border/30 shadow-lg bg-card/50 backdrop-blur-sm">
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-gradient-to-r from-primary/10 via-primary/5 to-primary/10">
              <th class="p-6 text-left font-black text-foreground text-lg tracking-tight first:rounded-tl-2xl last:rounded-tr-2xl">${header1.trim()}</th>
              <th class="p-6 text-left font-black text-foreground text-lg tracking-tight first:rounded-tl-2xl last:rounded-tr-2xl">${header2.trim()}</th>
              <th class="p-6 text-left font-black text-foreground text-lg tracking-tight first:rounded-tl-2xl last:rounded-tr-2xl">${header3.trim()}</th>
              <th class="p-6 text-left font-black text-foreground text-lg tracking-tight first:rounded-tl-2xl last:rounded-tr-2xl">${header4.trim()}</th>
              <th class="p-6 text-left font-black text-foreground text-lg tracking-tight first:rounded-tl-2xl last:rounded-tr-2xl">${header5.trim()}</th>
            </tr>
          </thead>
          <tbody>
            ${tableBody}
          </tbody>
        </table>
      </div>
    `;
  });

      // Convert other markdown elements
      html = html
        .replace(/^### (.*$)/gim, '<div class="my-8 w-full"><div class="w-full h-px bg-border"></div></div><h3 class="text-2xl font-bold mt-6 mb-4 text-foreground tracking-[-0.01em] relative"><span class="bg-gradient-to-r from-primary/20 to-primary/10 px-3 py-1 rounded-lg text-sm font-semibold text-primary absolute -left-4 -top-1">SECTION</span><br/>$1</h3>')
        .replace(/^## (.*$)/gim, '<div class="my-8 w-full"><div class="w-full h-px bg-border"></div></div><h2 class="text-4xl font-black mt-6 mb-6 text-foreground tracking-[-0.02em] leading-tight relative"><span class="absolute -left-8 top-0 w-1 h-full bg-gradient-to-b from-primary to-primary/50 rounded-full"></span>$1</h2>')
        .replace(/^# (.*$)/gim, '<div class="my-8 w-full"><div class="w-full h-px bg-border"></div></div><h1 class="text-5xl font-black mt-6 mb-8 text-foreground tracking-[-0.02em] leading-tight bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-foreground bg-gradient-to-r from-primary/10 to-primary/5 px-1 py-0.5 rounded">$1</strong>')
        .replace(/\*(.*?)\*/g, '<em class="italic text-foreground/80 font-medium">$1</em>')
        .replace(/^- (.*$)/gim, '<li class="ml-6 text-foreground/85 leading-relaxed relative"><span class="absolute -left-4 top-2 w-1.5 h-1.5 bg-primary rounded-full"></span>$1</li>')
        .replace(/(<li class="ml-6 text-foreground\/85 leading-relaxed relative"><span class="absolute -left-4 top-2 w-1\.5 h-1\.5 bg-primary rounded-full"><\/span>.*<\/li>)/g, '<ul class="my-6 space-y-3 text-foreground/85">$1</ul>')
        .replace(/\n\n/g, '</p><p class="my-6 text-foreground/85 leading-relaxed text-lg">')
        .replace(/^(?!<[h|u|d|t])/gm, '<p class="my-6 text-foreground/85 leading-relaxed text-lg">')
        .replace(/(<p class="my-6 text-foreground\/85 leading-relaxed text-lg"><\/p>)/g, '');

  return html;
}

interface BlogPostProps {
  post: BlogPost;
  onLike?: (postId: string) => void;
  onShare?: (postId: string) => void;
  showHeaderOnly?: boolean;
  showContentOnly?: boolean;
}

export function BlogPost({ post, onLike, onShare, showHeaderOnly = false, showContentOnly = false }: BlogPostProps) {
  const [isLiked, setIsLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(post.likes);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleLike = () => {
    if (!isLiked) {
      setIsLiked(true);
      setLikeCount(prev => prev + 1);
      onLike?.(post.id);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: post.title,
        text: post.excerpt,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
    }
    onShare?.(post.id);
  };

  // If showing only header, return just the header section
  if (showHeaderOnly) {
    return (
      <article className="w-full">
        {/* BACK BUTTON */}
        <div className="mb-8">
          <Button variant="ghost" asChild>
            <Link href="/blog" className="flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Blog
            </Link>
          </Button>
        </div>

        {/* HEADER */}
        <header className="mb-12">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
            <div className="flex items-center gap-2 px-3 py-1 bg-muted/50 rounded-full">
              <User className="w-4 h-4" />
              <span className="font-medium">{post.author.name}</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-muted/50 rounded-full">
              <Calendar className="w-4 h-4" />
              <span>{formatDate(post.publishedAt)}</span>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-muted/50 rounded-full">
              <Clock className="w-4 h-4" />
              <span>{post.readTime} min read</span>
            </div>
          </div>

          <h1 className="text-6xl font-black mb-12 leading-[1.1] bg-gradient-to-br from-foreground via-foreground to-foreground/70 bg-clip-text text-transparent tracking-[-0.02em]">
            {post.title}
          </h1>

          <p className="text-2xl text-foreground/75 mb-16 leading-relaxed font-light">
            {post.excerpt}
          </p>

          <div className="flex flex-wrap gap-3 mb-8">
            <Badge variant="secondary" className="text-sm px-4 py-2 font-medium">
              {post.category}
            </Badge>
            {post.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="text-sm px-4 py-2 hover:bg-primary/10 transition-colors">
                {tag}
              </Badge>
            ))}
          </div>

          <div className="flex items-center gap-8 text-sm">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Eye className="w-4 h-4" />
              <span className="font-medium">{post.views.toLocaleString()} views</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLike}
              className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${
                isLiked ? 'text-red-500 bg-red-50' : 'hover:text-red-500 hover:bg-red-50'
              }`}
            >
              <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
              <span className="font-medium">{likeCount}</span>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleShare}
              className="flex items-center gap-2 px-4 py-2 rounded-full hover:text-primary hover:bg-primary/10 transition-all"
            >
              <Share2 className="w-4 h-4" />
              <span className="font-medium">Share</span>
            </Button>
          </div>
        </header>
      </article>
    );
  }

  // If showing only content, return just the content section
  if (showContentOnly) {
    return (
      <article className="max-w-4xl mx-auto">
        {/* FEATURED IMAGE */}
        {post.featuredImage && (
          <div className="mb-12 relative overflow-hidden rounded-2xl shadow-2xl">
            <div className="aspect-video relative">
              <img
                src={post.featuredImage}
                alt={post.title}
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent" />
              <div className="absolute bottom-4 left-4 right-4">
                <div className="bg-white/90 backdrop-blur-sm rounded-lg p-4">
                  <h2 className="text-lg font-semibold text-gray-900 line-clamp-2">
                    {post.title}
                  </h2>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* CONTENT */}
        <div className="prose prose-xl max-w-none prose-headings:font-black prose-headings:text-foreground prose-h1:text-5xl prose-h2:text-4xl prose-h3:text-2xl prose-p:text-foreground/85 prose-p:leading-relaxed prose-p:font-normal prose-p:text-lg prose-p:my-12 prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-strong:text-foreground prose-strong:font-bold prose-ul:list-none prose-ol:list-decimal prose-li:marker:text-muted-foreground prose-blockquote:border-l-4 prose-blockquote:border-primary prose-blockquote:bg-muted/50 prose-blockquote:px-8 prose-blockquote:py-6 prose-blockquote:rounded-xl prose-blockquote:my-16 prose-code:bg-muted prose-code:px-3 prose-code:py-1 prose-code:rounded-md prose-code:text-sm prose-pre:bg-muted prose-pre:border prose-pre:border-border prose-pre:rounded-xl prose-pre:my-16">
          <div
            dangerouslySetInnerHTML={{
              __html: convertMarkdownToHtml(post.content)
            }}
          />
        </div>

        {/* AUTHOR INFO */}
        <div className="mt-16 p-8 bg-gradient-to-r from-muted/50 to-muted/30 rounded-2xl border border-border/50">
          <div className="flex items-start gap-6">
            {post.author.avatar ? (
              <img
                src={post.author.avatar}
                alt={post.author.name}
                className="w-20 h-20 rounded-full object-cover ring-4 ring-background shadow-lg"
              />
            ) : (
              <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center ring-4 ring-background shadow-lg">
                <User className="w-8 h-8 text-primary" />
              </div>
            )}
            <div className="flex-1">
              <h3 className="font-bold text-xl mb-2">{post.author.name}</h3>
              <p className="text-muted-foreground mb-3">{post.author.email}</p>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  <span>Published {formatDate(post.publishedAt)}</span>
                </div>
                {post.updatedAt !== post.publishedAt && (
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    <span>Updated {formatDate(post.updatedAt)}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </article>
    );
  }

  // Default: show everything
  return (
    <article className="max-w-4xl mx-auto">
      {/* BACK BUTTON */}
      <div className="mb-8">
        <Button variant="ghost" asChild>
          <Link href="/blog" className="flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back to Blog
          </Link>
        </Button>
      </div>

      {/* HEADER */}
      <header className="mb-12">
        <div className="flex items-center gap-2 text-sm text-foreground/70 mb-6">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-muted/50 rounded-full">
            <User className="w-4 h-4" />
            <span className="font-medium text-foreground/90">{post.author.name}</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-muted/50 rounded-full">
            <Calendar className="w-4 h-4" />
            <span className="text-foreground/80">{formatDate(post.publishedAt)}</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-muted/50 rounded-full">
            <Clock className="w-4 h-4" />
            <span className="text-foreground/80">{post.readTime} min read</span>
          </div>
        </div>

        <h1 className="text-5xl font-bold mb-6 leading-tight bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
          {post.title}
        </h1>

        <p className="text-xl text-muted-foreground mb-8 leading-relaxed max-w-3xl">
          {post.excerpt}
        </p>

        <div className="flex flex-wrap gap-3 mb-8">
          <Badge variant="secondary" className="text-sm px-4 py-2 font-medium">
            {post.category}
          </Badge>
          {post.tags.map((tag) => (
            <Badge key={tag} variant="outline" className="text-sm px-4 py-2 hover:bg-primary/10 transition-colors">
              {tag}
            </Badge>
          ))}
        </div>

        <div className="flex items-center gap-8 text-sm mb-16">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Eye className="w-4 h-4" />
            <span className="font-medium">{post.views.toLocaleString()} views</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLike}
            className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${
              isLiked ? 'text-red-500 bg-red-50' : 'hover:text-red-500 hover:bg-red-50'
            }`}
          >
            <Heart className={`w-4 h-4 ${isLiked ? 'fill-current' : ''}`} />
            <span className="font-medium">{likeCount}</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleShare}
            className="flex items-center gap-2 px-4 py-2 rounded-full hover:text-primary hover:bg-primary/10 transition-all"
          >
            <Share2 className="w-4 h-4" />
            <span className="font-medium">Share</span>
          </Button>
        </div>
      </header>

      {/* FEATURED IMAGE */}
      {post.featuredImage && (
        <div className="mb-12 relative overflow-hidden rounded-2xl shadow-2xl">
          <div className="aspect-video relative">
            <img
              src={post.featuredImage}
              alt={post.title}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent" />
            <div className="absolute bottom-4 left-4 right-4">
              <div className="bg-white/90 backdrop-blur-sm rounded-lg p-4">
                <h2 className="text-lg font-semibold text-gray-900 line-clamp-2">
                  {post.title}
                </h2>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CONTENT */}
      <div className="prose prose-lg max-w-none prose-headings:font-bold prose-headings:text-foreground prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl prose-p:text-muted-foreground prose-p:leading-relaxed prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-strong:text-foreground prose-ul:list-disc prose-ol:list-decimal prose-li:marker:text-muted-foreground prose-blockquote:border-l-4 prose-blockquote:border-primary prose-blockquote:bg-muted/50 prose-blockquote:px-6 prose-blockquote:py-4 prose-blockquote:rounded-r-lg">
        <div
          dangerouslySetInnerHTML={{
            __html: convertMarkdownToHtml(post.content)
          }}
        />
      </div>

      {/* AUTHOR INFO */}
      <div className="mt-16 p-8 bg-gradient-to-r from-muted/50 to-muted/30 rounded-2xl border border-border/50">
        <div className="flex items-start gap-6">
          {post.author.avatar ? (
            <img
              src={post.author.avatar}
              alt={post.author.name}
              className="w-20 h-20 rounded-full object-cover ring-4 ring-background shadow-lg"
            />
          ) : (
            <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center ring-4 ring-background shadow-lg">
              <User className="w-8 h-8 text-primary" />
            </div>
          )}
          <div className="flex-1">
            <h3 className="font-bold text-xl mb-2">{post.author.name}</h3>
            <p className="text-muted-foreground mb-3">{post.author.email}</p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                <span>Published {formatDate(post.publishedAt)}</span>
              </div>
              {post.updatedAt !== post.publishedAt && (
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>Updated {formatDate(post.updatedAt)}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}
