import { NextRequest, NextResponse } from 'next/server';

export interface AuthenticatedRequest extends NextRequest {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

export async function authenticateRequest(request: NextRequest): Promise<{ user?: any; error?: NextResponse }> {
  try {
    console.log('🔐 AUTH: Starting authentication process');
    
    const authHeader = request.headers.get('Authorization');
    console.log('🔐 AUTH: Authorization header present:', !!authHeader);
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      console.error('❌ AUTH: No valid authorization header');
      return {
        error: NextResponse.json(
          { error: 'Authorization header required' },
          { status: 401 }
        )
      };
    }

    const token = authHeader.substring(7);
    console.log('🔐 AUTH: Token extracted, length:', token.length);
    
    // Use our v1 auth validation endpoint
    const baseUrl = process.env.NEXTAUTH_URL || 'http://localhost:3000';
    const validateUrl = `${baseUrl}/api/v1/auth/validate`;
    console.log('🔐 AUTH: Calling validation endpoint:', validateUrl);
    
    const response = await fetch(validateUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    console.log('🔐 AUTH: Validation response status:', response.status);

    if (!response.ok) {
      console.error('❌ AUTH: Token validation failed with status:', response.status);
      return {
        error: NextResponse.json(
          { error: 'Invalid or expired token' },
          { status: 401 }
        )
      };
    }

    const userData = await response.json();
    console.log('✅ AUTH: Authentication successful for user:', userData.email || 'unknown');
    return { user: userData };
  } catch (error) {
    console.error('❌ AUTH: Authentication error:', error);
    console.error('❌ AUTH: Error stack:', (error as Error).stack);
    return {
      error: NextResponse.json(
        { error: 'Authentication failed' },
        { status: 500 }
      )
    };
  }
}

export function requireAuth(handler: (request: AuthenticatedRequest) => Promise<NextResponse>) {
  return async (request: NextRequest) => {
    const { user, error } = await authenticateRequest(request);
    
    if (error) {
      return error;
    }

    (request as AuthenticatedRequest).user = user;
    return handler(request as AuthenticatedRequest);
  };
}
