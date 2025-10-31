import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Generate a demo token for testing
    const demoToken = 'demo-admin-token-' + Date.now();
    
    return NextResponse.json({
      token: demoToken,
      message: 'Demo token generated for testing',
      expires_in: 3600, // 1 hour
    });
  } catch (error) {
    console.error('Demo token generation error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
