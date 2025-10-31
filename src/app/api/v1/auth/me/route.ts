import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth } from '../../middleware/error-handling';
import { makeBackendRequest } from '../../lib/utils/backend';

export const GET = withErrorHandling(requireAuth(async (request) => {
  const response = await makeBackendRequest('/api/auth/me', {
    method: 'GET'
  }, request);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Authentication failed' }));
    return NextResponse.json(errorData, { status: response.status });
  }

  const userData = await response.json();
  return NextResponse.json(userData);
}));
