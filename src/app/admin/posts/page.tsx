"use client";

import { Button } from '@/components/ui/button';
import { PostCard, PostsFilters, Pagination } from '@/app/admin/components';
import { usePosts } from '@/hooks/admin';
import { Plus } from 'lucide-react';
import Link from 'next/link';

export default function AdminPostsPage() {
  const {
    data,
    loading,
    error,
    filters,
    handleFilterChange,
    handleDelete,
    handleStatusChange,
    fetchPosts
  } = usePosts();

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/3"></div>
          <div className="h-10 bg-muted rounded"></div>
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-16 bg-muted rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <h1 className="text-2xl font-bold mb-4">Error Loading Posts</h1>
        <p className="text-muted-foreground mb-4">{error}</p>
        <Button onClick={() => fetchPosts()}>Try Again</Button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="p-6 space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Posts</h1>
          <p className="text-muted-foreground">Manage your blog content</p>
        </div>
        <Button asChild>
          <Link href="/admin/posts/create">
            <Plus className="w-4 h-4 mr-2" />
            New Post
          </Link>
        </Button>
      </div>

      {/* FILTERS */}
      <PostsFilters
        search={filters.search}
        status={filters.status}
        onSearchChange={(search) => handleFilterChange({ search })}
        onStatusChange={(status) => handleFilterChange({ status })}
      />

      {/* POSTS LIST */}
      <div className="space-y-3">
        {data.posts.map((post) => (
          <PostCard
            key={post.id}
            post={post}
            onDelete={handleDelete}
            onStatusChange={handleStatusChange}
          />
        ))}
      </div>

      {/* PAGINATION */}
      <Pagination
        currentPage={data.pagination.page}
        totalPages={data.pagination.totalPages}
        onPageChange={(page) => fetchPosts(page, filters)}
        hasNext={data.pagination.hasNext}
        hasPrev={data.pagination.hasPrev}
      />
    </div>
  );
}
