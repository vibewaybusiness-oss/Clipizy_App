import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth } from '../../../middleware/error-handling';
import { makeBackendRequest } from '../../../lib/utils/backend';

export const GET = withErrorHandling(async () => {
  return NextResponse.json({ 
    message: 'ComfyUI image-to-image generation API is working',
    timestamp: new Date().toISOString()
  });
});

export const POST = withErrorHandling(requireAuth(async (request: NextRequest) => {
  const body = await request.json();
  
  // Convert body parameters to query parameters for the backend
  const queryParams = new URLSearchParams({
    prompt: body.prompt || '',
    reference_image_path: body.reference_image_path || '',
    width: body.width?.toString() || '1328',
    height: body.height?.toString() || '1328',
    ...(body.seed && { seed: body.seed }),
    ...(body.negative_prompt && { negative_prompt: body.negative_prompt }),
  });
  
  const response = await makeBackendRequest(`/api/ai/comfyui/image/qwen/generate?${queryParams}`, {
    method: 'POST',
    timeout: 300000 // 5 minutes timeout for image generation
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
