import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth } from '../../../middleware/error-handling';
import { makeBackendRequest, getBackendUrl } from '../../../lib/utils/backend';

export const GET = withErrorHandling(async () => {
  return NextResponse.json({ 
    message: 'LLM (qwen-omni) generation API is working',
    backendUrl: getBackendUrl(),
    timestamp: new Date().toISOString()
  });
});

export const POST = withErrorHandling(requireAuth(async (request: NextRequest) => {
  const body = await request.json();
  
  const response = await makeBackendRequest('/api/ai/llm/generate', {
    method: 'POST',
    body,
    timeout: 300000 // 5 minutes timeout for LLM requests (pod allocation can take time)
  }, request);

  if (!response.ok) {
    const errorData = await response.text();
    return NextResponse.json(
      { error: `Backend error: ${response.status} ${errorData}` },
      { status: response.status }
    );
  }

  const data = await response.json();
  return NextResponse.json(data);
}));
