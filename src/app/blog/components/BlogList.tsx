"use client";

import { BlogPost, BlogCategory, BlogTag } from '@/types';
import { BlogCard } from './BlogCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, X } from 'lucide-react';
import { useState } from 'react';

interface BlogListProps {
  posts: BlogPost[];
  categories: BlogCategory[];
  tags: BlogTag[];
  pagination?: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  onPageChange?: (page: number) => void;
  onFilterChange?: (filters: {
    search?: string;
    category?: string;
    tag?: string;
  }) => void;
}

export function BlogList({
  posts,
  categories,
  tags,
  pagination,
  onPageChange,
  onFilterChange
}: BlogListProps) {
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedTag, setSelectedTag] = useState('');

  const handleSearch = (value: string) => {
    setSearch(value);
    onFilterChange?.({
      search: value,
      category: selectedCategory,
      tag: selectedTag
    });
  };

  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value);
    onFilterChange?.({
      search,
      category: value,
      tag: selectedTag
    });
  };

  const handleTagChange = (tag: string) => {
    const newTag = selectedTag === tag ? '' : tag;
    setSelectedTag(newTag);
    onFilterChange?.({
      search,
      category: selectedCategory,
      tag: newTag
    });
  };

  const clearFilters = () => {
    setSearch('');
    setSelectedCategory('');
    setSelectedTag('');
    onFilterChange?.({});
  };

  const hasActiveFilters = search || selectedCategory || selectedTag;

  return (
    <div className="space-y-10">
      {/* FILTERS */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <Input
              placeholder="Search blog posts..."
              value={search}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10 h-12"
            />
          </div>
          <Select value={selectedCategory || "all"} onValueChange={(value) => handleCategoryChange(value === "all" ? "" : value)}>
            <SelectTrigger className="w-full sm:w-48 h-12">
              <SelectValue placeholder="All Categories" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              {categories.map((category) => (
                <SelectItem key={category.id} value={category.slug}>
                  {category.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* TAGS */}
        <div className="flex flex-wrap gap-2">
          <span className="text-sm font-medium text-muted-foreground mr-2">Tags:</span>
          {tags.map((tag) => (
            <Badge
              key={tag.id}
              variant={selectedTag === tag.slug ? "default" : "outline"}
              className="cursor-pointer hover:bg-primary/10 transition-colors px-3 py-1"
              onClick={() => handleTagChange(tag.slug)}
            >
              {tag.name} ({tag.postCount})
            </Badge>
          ))}
        </div>

        {/* ACTIVE FILTERS */}
        {hasActiveFilters && (
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm text-muted-foreground">Active filters:</span>
            {search && (
              <Badge variant="secondary" className="gap-1">
                Search: "{search}"
                <X className="w-3 h-3 cursor-pointer" onClick={() => handleSearch('')} />
              </Badge>
            )}
            {selectedCategory && (
              <Badge variant="secondary" className="gap-1">
                Category: {categories.find(c => c.slug === selectedCategory)?.name}
                <X className="w-3 h-3 cursor-pointer" onClick={() => handleCategoryChange('')} />
              </Badge>
            )}
            {selectedTag && (
              <Badge variant="secondary" className="gap-1">
                Tag: {tags.find(t => t.slug === selectedTag)?.name}
                <X className="w-3 h-3 cursor-pointer" onClick={() => handleTagChange('')} />
              </Badge>
            )}
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              Clear all
            </Button>
          </div>
        )}
      </div>

      {/* POSTS GRID */}
      {posts.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {posts.map((post, index) => (
              <BlogCard
                key={post.id}
                post={post}
                featured={index === 0 && posts.length > 0}
              />
            ))}
          </div>

          {/* PAGINATION */}
          {pagination && pagination.totalPages > 1 && (
            <div className="flex items-center justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange?.(pagination.page - 1)}
                disabled={!pagination.hasPrev}
              >
                Previous
              </Button>

              <div className="flex items-center gap-1">
                {Array.from({ length: pagination.totalPages }, (_, i) => i + 1).map((page) => (
                  <Button
                    key={page}
                    variant={page === pagination.page ? "default" : "outline"}
                    size="sm"
                    onClick={() => onPageChange?.(page)}
                    className="w-10 h-10"
                  >
                    {page}
                  </Button>
                ))}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange?.(pagination.page + 1)}
                disabled={!pagination.hasNext}
              >
                Next
              </Button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12">
          <div className="text-muted-foreground mb-4">
            <Filter className="w-12 h-12 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No posts found</h3>
            <p>Try adjusting your search or filter criteria.</p>
          </div>
          {hasActiveFilters && (
            <Button onClick={clearFilters} variant="outline">
              Clear filters
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
