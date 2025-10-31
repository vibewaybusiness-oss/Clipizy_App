import { useState, useEffect } from 'react';

interface AdminStats {
  totalPosts: number;
  publishedPosts: number;
  draftPosts: number;
  recentPosts: Array<{
    id: string;
    title: string;
    status: 'published' | 'draft';
    createdAt: string;
  }>;
}

export function useAdminStats() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Mock data for now - replace with actual API call
        const mockStats: AdminStats = {
          totalPosts: 12,
          publishedPosts: 8,
          draftPosts: 4,
          recentPosts: [
            {
              id: '1',
              title: 'Getting Started with Video Editing',
              status: 'published',
              createdAt: '2024-01-15T10:30:00Z'
            },
            {
              id: '2',
              title: 'Advanced Effects Tutorial',
              status: 'draft',
              createdAt: '2024-01-14T15:45:00Z'
            },
            {
              id: '3',
              title: 'Audio Sync Techniques',
              status: 'published',
              createdAt: '2024-01-13T09:20:00Z'
            }
          ]
        };
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setStats(mockStats);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load admin stats');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return { stats, loading, error };
}
