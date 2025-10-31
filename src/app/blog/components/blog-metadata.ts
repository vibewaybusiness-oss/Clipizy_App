import { Metadata } from 'next';

interface BlogPostMetadata {
  title: string;
  description: string;
  slug: string;
  keywords: string[];
  publishedAt: string;
  author: string;
  category: string;
  tags: string[];
}

export function generateBlogPostMetadata(post: BlogPostMetadata): Metadata {
  return {
    title: post.title,
    description: post.description,
    keywords: post.keywords.join(', '),
    authors: [{ name: post.author }],
    openGraph: {
      title: post.title,
      description: post.description,
      type: 'article',
      publishedTime: post.publishedAt,
      authors: [post.author],
      tags: post.tags,
      url: `https://clipizy.ai/blog/${post.slug}`,
      siteName: 'clipizy',
      images: [
        {
          url: `https://clipizy.ai/blog/${post.slug}.jpg`,
          width: 1200,
          height: 630,
          alt: post.title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.description,
      images: [`https://clipizy.ai/blog/${post.slug}.jpg`],
    },
    alternates: {
      canonical: `https://clipizy.ai/blog/${post.slug}`,
    },
  };
}

export const blogPostMetadata: Record<string, BlogPostMetadata> = {
  'ai-music-video-generator-5-minutes': {
    title: 'Make a Music Video in 5 Minutes with AI | clipizy',
    description: 'Learn how to create a professional music video in just 5 minutes using an AI music video generator. Perfect for indie artists and creators.',
    slug: 'ai-music-video-generator-5-minutes',
    keywords: ['AI music video generator', 'automatic music video maker', 'music video creation online', 'create music video with AI'],
    publishedAt: '2024-01-07T10:00:00Z',
    author: 'clipizy Team',
    category: 'Tutorials',
    tags: ['AI tools', 'music marketing', 'video creation', 'YouTube growth']
  },
  'top-ai-music-video-generators-2025': {
    title: 'Top 5 AI Music Video Generators Compared [2025 Edition]',
    description: 'Discover the best AI music video makers in 2025. Compare clipizy, Pictory, InVideo, Runway, and Descript to find your perfect fit.',
    slug: 'top-ai-music-video-generators-2025',
    keywords: ['AI music video generator', 'automatic music video maker', 'music video creation online', 'best AI video generator'],
    publishedAt: '2024-01-28T10:00:00Z',
    author: 'clipizy Team',
    category: 'Comparison',
    tags: ['AI video tools', 'music promotion', 'creator economy', 'software comparisons']
  }
};
