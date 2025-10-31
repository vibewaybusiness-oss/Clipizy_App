import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, ValidationError } from '../../../../middleware/error-handling';

export const POST = withErrorHandling(async (request: NextRequest) => {
  const body = await request.json();
  const { code, state } = body;

  if (!code) {
    throw new ValidationError('Authorization code is required');
  }

  // Mock YouTube OAuth callback handling
  // In production, this would exchange the code for tokens and store them
  
  const mockResponse = {
    success: true,
    message: 'YouTube account connected successfully',
    account: {
      id: 'youtube_' + Date.now(),
      platform: 'youtube',
      name: 'YouTube Channel',
      username: '@youtubechannel',
      connected: true,
      connectedAt: new Date().toISOString()
    }
  };

  return NextResponse.json(mockResponse);
});
