import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling } from '../../../middleware/error-handling';
import { makeBackendRequest } from '../../../lib/utils/backend';

export const GET = withErrorHandling(async (request: NextRequest) => {
  const response = await makeBackendRequest('/api/auth/google', {
    method: 'GET',
    timeout: 10000
  }, request);

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Backend error response:', errorText);
    
    if (response.status >= 500) {
      return NextResponse.json(
        { error: 'Backend authentication service is not available. Please try again later.' },
        { status: 503 }
      );
    }
    
    return NextResponse.json(
      { error: `Backend error: ${response.status} - ${errorText}` },
      { status: response.status }
    );
  }

  const data = await response.json();
  return NextResponse.json(data);
});
