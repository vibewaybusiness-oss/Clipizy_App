import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, NotFoundError } from '../../../middleware/error-handling';

// Mock blog data - in production, this would come from a database
const blogPosts = [
  {
    id: '1',
    title: 'Getting Started with Music Video Creation',
    slug: 'getting-started-music-video-creation',
    excerpt: 'Learn the basics of creating professional music videos with AI',
    content: 'Full content here...',
    author: 'Clipizy Team',
    publishedAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
    status: 'published',
    category: 'tutorials',
    tags: ['music', 'video', 'ai', 'tutorial'],
    featuredImage: '/images/blog/featured-1.jpg',
    readTime: 5
  }
];

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  return withErrorHandling(async () => {
    const { slug } = await params;
    
    const post = blogPosts.find(p => p.slug === slug);
    
    if (!post) {
      throw new NotFoundError('Blog post', slug);
    }

    return NextResponse.json(post);
  })(request);
}
