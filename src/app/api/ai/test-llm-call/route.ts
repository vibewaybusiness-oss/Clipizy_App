import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const authHeader = request.headers.get('authorization');
    
    const response = await fetch(`${BACKEND_URL}/api/ai/test-llm-call`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader ? { Authorization: authHeader } : {}),
      },
      body: JSON.stringify(body),
    });

    const contentType = response.headers.get('content-type');
    let data;
    
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      try {
        data = JSON.parse(text);
      } catch {
        return NextResponse.json(
          { error: 'Invalid response from backend', details: text.substring(0, 200) },
          { status: response.status }
        );
      }
    }
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Error in test-llm-call proxy:', error);
    return NextResponse.json(
      { error: 'Failed to test LLM call', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

