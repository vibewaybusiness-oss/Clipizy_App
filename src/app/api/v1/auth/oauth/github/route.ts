import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling } from '../../../middleware/error-handling';
import { makeBackendRequest } from '../../../lib/utils/backend';

export const GET = withErrorHandling(async (request: NextRequest) => {
  try {
    const response = await makeBackendRequest('/api/auth/github', {
      method: 'GET',
      timeout: 10000
    }, request);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      
      if (response.status >= 500) {
        // Fallback to direct GitHub OAuth URL generation
        const OAUTH_GITHUB_CLIENT_ID = process.env.OAUTH_GITHUB_CLIENT_ID || 'your_github_client_id';
        const redirect_uri = process.env.OAUTH_REDIRECT_URI || `${process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'}/auth/callback`;
        
        const params = {
          client_id: OAUTH_GITHUB_CLIENT_ID,
          redirect_uri: redirect_uri,
          scope: 'user:email',
          response_type: 'code',
        };
        
        const query_string = Object.entries(params)
          .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
          .join('&');
        
        const auth_url = `https://github.com/login/oauth/authorize?${query_string}`;
        
        return NextResponse.json({ auth_url });
      }
      
      return NextResponse.json(
        { error: `Backend error: ${response.status} - ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('GitHub auth API error:', error);
    
    // Fallback to direct GitHub OAuth URL generation
    const OAUTH_GITHUB_CLIENT_ID = process.env.OAUTH_GITHUB_CLIENT_ID || 'your_github_client_id';
    const redirect_uri = process.env.OAUTH_REDIRECT_URI || `${process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'}/auth/callback`;
    
    const params = {
      client_id: OAUTH_GITHUB_CLIENT_ID,
      redirect_uri: redirect_uri,
      scope: 'user:email',
      response_type: 'code',
    };
    
    const query_string = Object.entries(params)
      .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
      .join('&');
    
    const auth_url = `https://github.com/login/oauth/authorize?${query_string}`;
    
    return NextResponse.json({ auth_url });
  }
});
