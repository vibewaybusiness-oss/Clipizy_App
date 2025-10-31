import { Metadata } from 'next';
import { BlogPostPageClient } from './client';
import { blogPostMetadata } from '@/app/blog/components/blog-metadata';

interface BlogPostPageProps {
  params: Promise<{ slug: string }>;
}

// Generate static params for known blog posts
export async function generateStaticParams() {
  return [
    { slug: 'ai-music-video-generator-5-minutes' },
    { slug: 'top-ai-music-video-generators-2025' }
  ];
}

export async function generateMetadata({ params }: BlogPostPageProps): Promise<Metadata> {
  const { slug } = await params;
  const metadata = blogPostMetadata[slug];
  
  if (!metadata) {
    return {
      title: 'Blog Post Not Found - clipizy',
      description: 'The requested blog post could not be found.',
    };
  }

  return {
    title: metadata.title,
    description: metadata.description,
    keywords: metadata.keywords.join(', '),
    authors: [{ name: metadata.author }],
    openGraph: {
      title: metadata.title,
      description: metadata.description,
      type: 'article',
      publishedTime: metadata.publishedAt,
      authors: [metadata.author],
      tags: metadata.tags,
      url: `https://clipizy.ai/blog/${metadata.slug}`,
      siteName: 'clipizy',
      images: [
        {
          url: `https://clipizy.ai/blog/${metadata.slug}.jpg`,
          width: 1200,
          height: 630,
          alt: metadata.title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: metadata.title,
      description: metadata.description,
      images: [`https://clipizy.ai/blog/${metadata.slug}.jpg`],
    },
    alternates: {
      canonical: `https://clipizy.ai/blog/${metadata.slug}`,
    },
  };
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const { slug } = await params;
  return <BlogPostPageClient params={{ slug }} />;
}

// Enable dynamic routes
export const dynamicParams = true;