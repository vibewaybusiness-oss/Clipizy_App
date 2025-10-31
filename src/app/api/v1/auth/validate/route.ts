import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('Authorization');
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return NextResponse.json(
      { error: 'Authorization header required' },
      { status: 401 }
    );
  }

  const token = authHeader.substring(7);
  
  try {
    // Forward to the running backend for token validation
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    console.log('🔐 BACKEND: Validating auth token with backend:', backendUrl);
    
    const response = await fetch(`${backendUrl}/api/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Backend auth validation error:', errorText);
      
      return NextResponse.json(
        { error: 'Invalid or expired token' },
        { status: 401 }
      );
    }

    const userData = await response.json();
    console.log('✅ REAL: Auth validation successful via backend');
    return NextResponse.json(userData);
  } catch (error) {
    console.error('❌ Auth validation error:', error);
    return NextResponse.json(
      { error: 'Authentication failed' },
      { status: 500 }
    );
  }
}
