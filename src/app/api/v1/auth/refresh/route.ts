import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, ValidationError } from '../../middleware/error-handling';
import { makeBackendRequest } from '../../lib/utils/backend';

export const POST = withErrorHandling(async (request: NextRequest) => {
  const body = await request.json();
  const { refresh_token } = body;

  if (!refresh_token) {
    throw new ValidationError('Refresh token is required');
  }

  const response = await makeBackendRequest('/api/auth/refresh', {
    method: 'POST',
    body: { refresh_token }
  }, request);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Token refresh failed' }));
    return NextResponse.json(errorData, { status: response.status });
  }

  const data = await response.json();
  return NextResponse.json(data);
});
