import { useState, useEffect } from 'react';
import type { ContentCalendar, CalendarBlogPost, ContentCluster } from '@/types/domains/calendar';

interface CalendarStats {
  total: number;
  published: number;
  draft: number;
  scheduled: number;
}

export function useContentCalendar() {
  const [calendar, setCalendar] = useState<ContentCalendar>({
    id: 'default',
    name: 'Content Calendar',
    description: 'Main content calendar for blog posts',
    startDate: new Date().toISOString(),
    endDate: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(), // 90 days from now
    totalWeeks: 12,
    postsPerWeek: 3,
    clusters: [
      {
        id: 'tech',
        name: 'Technology',
        description: 'Tech-related content',
        color: '#3B82F6',
        keywords: ['technology', 'programming', 'software'],
        targetAudience: 'developers',
        priority: 'high'
      },
      {
        id: 'music',
        name: 'Music Production',
        description: 'Music and audio content',
        color: '#10B981',
        keywords: ['music', 'audio', 'production'],
        targetAudience: 'musicians',
        priority: 'high'
      }
    ],
    posts: [],
    settings: {
      publishingDays: ['monday', 'wednesday', 'friday'],
      timezone: 'UTC',
      autoGenerate: false,
      promptPrefix: 'Write a blog post about',
      promptSuffix: 'Make it engaging and informative.',
      defaultAuthor: {
        name: 'Content Team',
        email: 'content@example.com'
      }
    }
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCalendar = async () => {
    try {
      setLoading(true);
      setError(null);

      // Mock data for now - replace with actual API call
      const mockPosts: CalendarBlogPost[] = [
        {
          id: '1',
          title: 'Getting Started with Music Production',
          slug: 'getting-started-music-production',
          content: 'This is a comprehensive guide to music production...',
          excerpt: 'Learn the basics of music production with our step-by-step guide.',
          status: 'published',
          publishedAt: '2024-01-15T10:00:00Z',
          scheduledFor: '2024-01-15T10:00:00Z',
          updatedAt: '2024-01-15T10:00:00Z',
          author: {
            name: 'Content Team',
            email: 'content@example.com'
          },
          tags: ['music', 'production', 'tutorial'],
          category: 'music',
          readTime: 8,
          views: 150,
          likes: 12,
          priority: 'high',
          keywords: ['music production', 'tutorial', 'beginner'],
          cluster: 'music',
          week: 2,
          month: 1,
          seoTitle: 'Music Production Guide for Beginners',
          metaDescription: 'Complete guide to music production for beginners'
        },
        {
          id: '2',
          title: 'Advanced Audio Mixing Techniques',
          slug: 'advanced-audio-mixing-techniques',
          content: 'Take your mixing skills to the next level...',
          excerpt: 'Professional mixing techniques for better sound quality.',
          status: 'draft',
          publishedAt: '',
          scheduledFor: '2024-01-20T14:00:00Z',
          updatedAt: '2024-01-12T10:00:00Z',
          author: {
            name: 'Content Team',
            email: 'content@example.com'
          },
          tags: ['mixing', 'audio', 'advanced'],
          category: 'music',
          readTime: 12,
          views: 0,
          likes: 0,
          priority: 'medium',
          keywords: ['audio mixing', 'professional', 'techniques'],
          cluster: 'music',
          week: 3,
          month: 1,
          seoTitle: 'Advanced Audio Mixing Techniques',
          metaDescription: 'Professional audio mixing techniques for better sound quality'
        }
      ];

      setCalendar(prev => ({
        ...prev,
        posts: mockPosts
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch calendar data');
    } finally {
      setLoading(false);
    }
  };

  const updatePost = (postId: string, updatedPost: Partial<CalendarBlogPost>) => {
    setCalendar(prev => ({
      ...prev,
      posts: prev.posts.map(post =>
        post.id === postId ? { ...post, ...updatedPost } : post
      )
    }));
  };

  const addPost = (newPost: Omit<CalendarBlogPost, 'id' | 'createdAt' | 'updatedAt'>) => {
    const post: CalendarBlogPost = {
      ...newPost,
      id: Date.now().toString(),
      updatedAt: new Date().toISOString()
    };

    setCalendar(prev => ({
      ...prev,
      posts: [...prev.posts, post]
    }));
  };

  const deletePost = (postId: string) => {
    setCalendar(prev => ({
      ...prev,
      posts: prev.posts.filter(p => p.id !== postId)
    }));
  };

  useEffect(() => {
    fetchCalendar();
  }, []);

  // Calculate stats from posts
  const stats = {
    total: calendar.posts.length,
    published: calendar.posts.filter(p => p.status === 'published').length,
    draft: calendar.posts.filter(p => p.status === 'draft').length,
    scheduled: calendar.posts.filter(p => p.status === 'scheduled').length
  };

  return {
    calendar,
    stats,
    loading,
    error,
    updatePost,
    addPost,
    deletePost,
    setCalendar,
    refetch: fetchCalendar
  };
}
