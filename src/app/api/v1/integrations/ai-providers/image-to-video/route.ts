import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth } from '../../../middleware/error-handling';
import { makeBackendRequest } from '../../../lib/utils/backend';

export const GET = withErrorHandling(async () => {
  return NextResponse.json({ 
    message: 'ComfyUI image-to-video generation API is working',
    timestamp: new Date().toISOString()
  });
});

export const POST = withErrorHandling(requireAuth(async (request: NextRequest) => {
  const body = await request.json();
  
  // Convert body parameters to query parameters for the backend
  const queryParams = new URLSearchParams({
    input_image_path: body.input_image_path || '',
    prompt: body.prompt || '',
    width: body.width?.toString() || '1280',
    height: body.height?.toString() || '720',
    num_frames: body.num_frames?.toString() || '81',
    frame_rate: body.frame_rate?.toString() || '16',
    speed: body.speed?.toString() || '0.2',
    ...(body.negative_prompt && { negative_prompt: body.negative_prompt }),
    ...(body.seed && { seed: body.seed }),
    ...(body.camera_motions && { camera_motions: JSON.stringify(body.camera_motions) }),
  });
  
  const response = await makeBackendRequest(`/api/ai/comfyui/video/wan/image-to-video?${queryParams}`, {
    method: 'POST',
    timeout: 600000 // 10 minutes timeout for video generation
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
