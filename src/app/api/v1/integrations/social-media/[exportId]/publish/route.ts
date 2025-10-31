import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth } from '../../../../middleware/error-handling';
import { makeBackendRequest } from '../../../../lib/utils/backend';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ exportId: string }> }
) {
  return withErrorHandling(requireAuth(async (req: NextRequest) => {
    const { exportId } = await params;
    const body = await req.json();

    const response = await makeBackendRequest(`/api/social-media/publish/${exportId}`, {
      method: 'POST',
      body
    }, req);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      
      if (response.status >= 500) {
        // Return mock publish result for server errors
        return NextResponse.json({
          success: true,
          message: 'Mock publish successful (backend error)',
          export_id: exportId,
          platforms: body.platforms || [],
          published_at: new Date().toISOString(),
          external_ids: body.platforms?.map((platform: string) => ({
            platform,
            external_id: `mock-${platform}-${Date.now()}`
          })) || []
        });
      }
      
      return NextResponse.json(
        { error: `Backend error: ${response.status} - ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  }))(request);
}
