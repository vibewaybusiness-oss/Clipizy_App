import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, ValidationError } from '../../../../middleware/error-handling';
import { makeBackendRequest } from '../../../../lib/utils/backend';

export const POST = withErrorHandling(async (request: NextRequest) => {
  const body = await request.json();
  const { code, state } = body;

  if (!code) {
    throw new ValidationError('Authorization code is required');
  }

  const response = await makeBackendRequest('/api/auth/google/callback', {
    method: 'POST',
    body,
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
