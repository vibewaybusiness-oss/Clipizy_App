import { NextRequest, NextResponse } from 'next/server';

export interface ApiError {
  code: string;
  message: string;
  details?: any;
  statusCode: number;
}

export class ValidationError extends Error {
  public code = 'VALIDATION_ERROR';
  public statusCode = 400;
  
  constructor(message: string, public details?: any) {
    super(message);
  }
}

export class AuthenticationError extends Error {
  public code = 'AUTHENTICATION_ERROR';
  public statusCode = 401;
  
  constructor(message: string = 'Authentication required') {
    super(message);
  }
}

export class AuthorizationError extends Error {
  public code = 'AUTHORIZATION_ERROR';
  public statusCode = 403;
  
  constructor(message: string = 'Insufficient permissions') {
    super(message);
  }
}

export class NotFoundError extends Error {
  public code = 'NOT_FOUND';
  public statusCode = 404;
  
  constructor(resource: string, id?: string) {
    super(`${resource}${id ? ` with ID ${id}` : ''} not found`);
  }
}

export class ConflictError extends Error {
  public code = 'CONFLICT';
  public statusCode = 409;
  
  constructor(message: string) {
    super(message);
  }
}

export class RateLimitError extends Error {
  public code = 'RATE_LIMIT_EXCEEDED';
  public statusCode = 429;
  
  constructor(message: string = 'Rate limit exceeded') {
    super(message);
  }
}

export function handleApiError(error: any): NextResponse {
  console.error('API Error:', error);

  // Handle known API errors
  if (error instanceof ValidationError) {
    return NextResponse.json(
      {
        error: {
          code: error.code,
          message: error.message,
          details: error.details
        }
      },
      { status: error.statusCode }
    );
  }

  if (error instanceof AuthenticationError) {
    return NextResponse.json(
      {
        error: {
          code: error.code,
          message: error.message
        }
      },
      { status: error.statusCode }
    );
  }

  if (error instanceof AuthorizationError) {
    return NextResponse.json(
      {
        error: {
          code: error.code,
          message: error.message
        }
      },
      { status: error.statusCode }
    );
  }

  if (error instanceof NotFoundError) {
    return NextResponse.json(
      {
        error: {
          code: error.code,
          message: error.message
        }
      },
      { status: error.statusCode }
    );
  }

  if (error instanceof ConflictError) {
    return NextResponse.json(
      {
        error: {
          code: error.code,
          message: error.message
        }
      },
      { status: error.statusCode }
    );
  }

  if (error instanceof RateLimitError) {
    return NextResponse.json(
      {
        error: {
          code: error.code,
          message: error.message
        }
      },
      { status: error.statusCode }
    );
  }

  // Handle unknown errors
  return NextResponse.json(
    {
      error: {
        code: 'INTERNAL_SERVER_ERROR',
        message: 'An unexpected error occurred'
      }
    },
    { status: 500 }
  );
}

export function withErrorHandling(handler: (request: NextRequest) => Promise<NextResponse>) {
  return async (request: NextRequest) => {
    try {
      return await handler(request);
    } catch (error) {
      return handleApiError(error);
    }
  };
}

// Re-export requireAuth from auth middleware
export { requireAuth } from './auth';
