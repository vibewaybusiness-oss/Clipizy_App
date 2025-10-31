import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth } from '../../../../middleware/error-handling';
import { makeBackendRequest } from '../../../../lib/utils/backend';

export const GET = withErrorHandling(async () => {
  return NextResponse.json({ 
    message: 'LLM create_dynamic_scenes_script API is working',
    timestamp: new Date().toISOString()
  });
});

export const POST = withErrorHandling(requireAuth(async (request: NextRequest) => {
  const body = await request.json();
  
  const response = await makeBackendRequest('/api/ai/llm/create_dynamic_scenes_script', {
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
