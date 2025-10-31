import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth } from '../../middleware/error-handling';

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
    readTime: 5,
    scheduledFor: null
  }
];

export const GET = withErrorHandling(async (request: NextRequest) => {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get('page') || '1');
  const limit = parseInt(searchParams.get('limit') || '10');
  const category = searchParams.get('category');
  const tag = searchParams.get('tag');
  const search = searchParams.get('search');
  const status = searchParams.get('status') || 'published';

  let filteredPosts = blogPosts;

  // Filter by status
  if (status !== 'all') {
    if (status === 'published') {
      filteredPosts = filteredPosts.filter(post => post.status === 'published');
    } else if (status === 'scheduled') {
      filteredPosts = filteredPosts.filter(post =>
        post.status === 'scheduled' ||
        (post.status === 'draft' && post.scheduledFor && new Date(post.scheduledFor) > new Date())
      );
    } else {
      filteredPosts = filteredPosts.filter(post => post.status === status);
    }
  } else {
    filteredPosts = filteredPosts.filter(post => post.status === 'published' || post.status === 'scheduled');
  }

  if (category) {
    filteredPosts = filteredPosts.filter(post => post.category.toLowerCase() === category.toLowerCase());
  }

  if (tag) {
    filteredPosts = filteredPosts.filter(post =>
      post.tags.some(t => t.toLowerCase() === tag.toLowerCase())
    );
  }

  if (search) {
    const searchLower = search.toLowerCase();
    filteredPosts = filteredPosts.filter(post =>
      post.title.toLowerCase().includes(searchLower) ||
      post.excerpt.toLowerCase().includes(searchLower) ||
      post.content.toLowerCase().includes(searchLower)
    );
  }

  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + limit;
  const paginatedPosts = filteredPosts.slice(startIndex, endIndex);

  const totalPages = Math.ceil(filteredPosts.length / limit);

  return NextResponse.json({
    posts: paginatedPosts,
    pagination: {
      page,
      limit,
      total: filteredPosts.length,
      totalPages
    }
  });
});

export const POST = withErrorHandling(requireAuth(async (request: NextRequest) => {
  const body = await request.json();
  
  // Create new blog post
  const newPost = {
    id: Date.now().toString(),
    ...body,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  // In production, save to database
  blogPosts.push(newPost);

  return NextResponse.json(newPost, { status: 201 });
}));
