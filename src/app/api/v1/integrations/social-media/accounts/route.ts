import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth } from '../../../middleware/error-handling';

export const GET = withErrorHandling(requireAuth(async (request: NextRequest) => {
  // Mock social media accounts data
  const accounts = [
    {
      id: '1',
      platform: 'youtube',
      name: 'My YouTube Channel',
      username: '@mychannel',
      connected: true,
      connectedAt: '2024-01-15T10:00:00Z',
      avatar: '/images/social/youtube-avatar.jpg'
    },
    {
      id: '2',
      platform: 'instagram',
      name: 'My Instagram',
      username: '@myinstagram',
      connected: true,
      connectedAt: '2024-01-10T10:00:00Z',
      avatar: '/images/social/instagram-avatar.jpg'
    }
  ];

  return NextResponse.json(accounts);
}));
