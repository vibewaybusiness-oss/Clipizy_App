import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling } from '../../../middleware/error-handling';
import { makeBackendRequest } from '../../../lib/utils/backend';

export const GET = withErrorHandling(async (_request: NextRequest) => {
  const response = await makeBackendRequest('/api/ai/llm/health', {
    method: 'GET',
    timeout: 15000,
  });

  const data = await response.json();
  return NextResponse.json(data, { status: response.status });
});


