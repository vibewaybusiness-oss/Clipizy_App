import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth } from '../../../../middleware/error-handling';
import { makeBackendRequest } from '../../../../lib/utils/backend';

export const GET = withErrorHandling(requireAuth(async (request: NextRequest) => {
  const response = await makeBackendRequest('/api/admin/stripe/customers', {
    method: 'GET'
  }, request);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return NextResponse.json(data);
}));
