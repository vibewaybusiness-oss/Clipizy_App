import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, ValidationError } from '../../middleware/error-handling';

export const POST = withErrorHandling(async (request: NextRequest) => {
  const body = await request.json();
  const { email, password, name } = body;

  if (!email || !password) {
    throw new ValidationError('Email and password are required');
  }

  // For now, return an error since we're only supporting OAuth
  return NextResponse.json(
    { error: 'Email/password registration not supported. Please use Google or GitHub login.' },
    { status: 501 }
  );
});
