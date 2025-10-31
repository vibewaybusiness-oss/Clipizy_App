import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  try {
    const { workflowId } = await params;
    
    console.log(`🚀 Next.js API: Fetching workflow definition for ${workflowId}`);
    
    // Get authorization header from the request
    const authHeader = request.headers.get('authorization');
    
    // Forward the request to the FastAPI backend
    const backendUrl = `${BACKEND_URL}/api/workflows/${workflowId}`;
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
        { error: 'Failed to fetch workflow', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log(`✅ Next.js API: Backend response received`);
    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ Next.js API: Error fetching workflow:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ workflowId: string }> }
) {
  try {
    const { workflowId } = await params;
    const body = await request.json();
    
    console.log(`🚀 Next.js API: POST request for workflow ${workflowId}`);
    
    // Get authorization header from the request
    const authHeader = request.headers.get('authorization');
    
    // Forward the request to the FastAPI backend
    const backendUrl = `${BACKEND_URL}/api/workflows/${workflowId}`;
    console.log(`📡 Next.js API: Forwarding to ${backendUrl}`);
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && { 'Authorization': authHeader }),
      },
      body: JSON.stringify(body),
    });

    console.log(`📡 Next.js API: Backend response status: ${response.status}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ Next.js API: Backend error: ${errorText}`);
      return NextResponse.json(
        { error: 'Failed to process workflow request', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log(`✅ Next.js API: Backend response received`);
    return NextResponse.json(data);
  } catch (error) {
    console.error('❌ Next.js API: Error processing workflow request:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
