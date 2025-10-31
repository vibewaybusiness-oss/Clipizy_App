import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BlogPost } from '@/types';
import { Eye, Edit, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { format } from 'date-fns';

interface PostCardProps {
  post: BlogPost;
  onEdit?: (post: BlogPost) => void;
  onDelete?: (postId: string) => void;
  onStatusChange?: (postId: string, status: string) => void;
  showActions?: boolean;
}

export function PostCard({
  post,
  onEdit,
  onDelete,
  onStatusChange,
  showActions = true
}: PostCardProps) {
  const getStatusBadge = (post: BlogPost) => {
    if (post.status === 'published') {
      return <Badge className="bg-green-100 text-green-800">Published</Badge>;
    } else if (post.status === 'draft') {
      return <Badge className="bg-yellow-100 text-yellow-800">Draft</Badge>;
    } else if (post.status === 'scheduled') {
      return <Badge className="bg-blue-100 text-blue-800">Scheduled</Badge>;
    } else {
      return <Badge className="bg-gray-100 text-gray-800">Archived</Badge>;
    }
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="font-semibold truncate">{post.title}</h3>
              {getStatusBadge(post)}
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>{format(new Date(post.publishedAt), 'MMM dd, yyyy')}</span>
              <span className="flex items-center gap-1">
                <Eye className="w-4 h-4" />
                {post.views.toLocaleString()}
              </span>
              <span>{post.category}</span>
            </div>
          </div>
          {showActions && (
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" asChild>
                <Link href={`/blog/${post.slug}`}>
                  <Eye className="w-4 h-4" />
                </Link>
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit?.(post)}
                asChild
              >
                <Link href={`/admin/posts/edit/${post.slug}`}>
                  <Edit className="w-4 h-4" />
                </Link>
              </Button>
              {onDelete && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete(post.slug)}
                  className="text-destructive hover:text-destructive"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
