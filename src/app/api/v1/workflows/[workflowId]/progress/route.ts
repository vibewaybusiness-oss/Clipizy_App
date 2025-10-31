import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  try {
    const { workflowId } = await params;
    const url = new URL(request.url);
    const jobId = url.searchParams.get('job_id');
    
    console.log(`🚀 Next.js API: Getting workflow progress for ${workflowId}, job ${jobId}`);
    
    // Get authorization header from the request
    const authHeader = request.headers.get('authorization');
    
    // Forward the request to the FastAPI backend
    const backendUrl = `${BACKEND_URL}/api/workflows/${workflowId}/progress?job_id=${jobId}`;
    console.log(`📡 Next.js API: Forwarding to ${backendUrl}`);
    
    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && { 'Authorization': authHeader }),
      },
    });

    console.log(`📡 Next.js API: Backend response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Next.js API: Backend error: ${errorText}`);
      return NextResponse.json(
        { error: 'Failed to get workflow progress', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log(`✅ Next.js API: Backend response received`);
    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ Next.js API: Error getting workflow progress:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
