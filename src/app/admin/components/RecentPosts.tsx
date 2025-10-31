import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BlogPost } from '@/types';
import { Eye } from 'lucide-react';
import Link from 'next/link';
import { format } from 'date-fns';

interface RecentPostsProps {
  posts: BlogPost[];
  title?: string;
  maxPosts?: number;
}

export function RecentPosts({
  posts,
  title = 'Recent Posts',
  maxPosts = 3
}: RecentPostsProps) {
  const displayPosts = posts.slice(0, maxPosts);

  const getStatusBadge = (post: BlogPost) => {
    if (post.status === 'published') {
      return <Badge className="bg-green-100 text-green-800">Published</Badge>;
    } else {
      return <Badge className="bg-yellow-100 text-yellow-800">Draft</Badge>;
    }
  };

  return (
    <Card>
      <CardContent className="p-6">
        <h3 className="font-semibold mb-4">{title}</h3>
        <div className="space-y-3">
          {displayPosts.map((post) => (
            <div key={post.id} className="flex items-center justify-between p-3 rounded-lg border">
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate">{post.title}</p>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  {getStatusBadge(post)}
                  <span>{format(new Date(post.publishedAt), 'MMM dd, yyyy')}</span>
                </div>
              </div>
              <Button variant="ghost" size="sm" asChild>
                <Link href={`/admin/posts/edit/${post.slug}`}>
                  <Eye className="w-4 h-4" />
                </Link>
              </Button>
            </div>
          ))}
          {displayPosts.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-4">
              No posts found
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
