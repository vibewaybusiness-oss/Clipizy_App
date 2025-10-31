// BLOG DOMAIN TYPES
export interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  author: {
    name: string;
    email: string;
    avatar?: string;
  };
  publishedAt: string;
  updatedAt: string;
  scheduledFor?: string;
  tags: string[];
  category: string;
  featuredImage?: string;
  status: 'draft' | 'published' | 'archived' | 'scheduled';
  readTime: number;
  views: number;
  likes: number;
}

export interface BlogCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
  color: string;
  postCount: number;
}

export interface BlogTag {
  id: string;
  name: string;
  slug: string;
  postCount: number;
}

export interface BlogComment {
  id: string;
  postId: string;
  author: {
    name: string;
    email: string;
    avatar?: string;
  };
  content: string;
  createdAt: string;
  updatedAt: string;
  status: 'pending' | 'approved' | 'rejected';
  parentId?: string;
  replies: BlogComment[];
}

export interface BlogStats {
  totalPosts: number;
  totalViews: number;
  totalLikes: number;
  totalComments: number;
  popularPosts: BlogPost[];
  recentPosts: BlogPost[];
  categories: BlogCategory[];
  tags: BlogTag[];
}
