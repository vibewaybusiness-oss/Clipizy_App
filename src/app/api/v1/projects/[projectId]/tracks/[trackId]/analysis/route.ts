import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth, ValidationError } from '../../../../../middleware/error-handling';
import { makeBackendRequest } from '../../../../../lib/utils/backend';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ projectId: string; trackId: string }> }
) {
  return withErrorHandling(requireAuth(async (req: NextRequest) => {
    const { projectId, trackId } = await params;

    if (!projectId || !trackId) {
      throw new ValidationError('Project ID and Track ID are required');
    }

    const response = await makeBackendRequest(`/api/music-analysis/music/${trackId}`, {
      method: 'POST',
      timeout: 300000 // 5 minutes for analysis
    }, req);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status} - ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  }))(request);
}
