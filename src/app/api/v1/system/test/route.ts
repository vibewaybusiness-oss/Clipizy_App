import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling } from '../../middleware/error-handling';

export const GET = withErrorHandling(async (request: NextRequest) => {
  console.log('🧪 Test API endpoint called');
  console.log('🧪 Request URL:', request.url);
  console.log('🧪 Request headers:', Object.fromEntries(request.headers.entries()));
  
  return NextResponse.json({ 
    message: 'Test API endpoint is working!',
    timestamp: new Date().toISOString(),
    url: request.url
  });
});
