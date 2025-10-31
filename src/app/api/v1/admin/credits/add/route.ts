import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth, ValidationError } from '../../../middleware/error-handling';
import { makeBackendRequest } from '../../../lib/utils/backend';

export const POST = withErrorHandling(requireAuth(async (request: NextRequest) => {
  const body = await request.json();
  const { user_id, amount, description } = body;

  if (!user_id || !amount) {
    throw new ValidationError('user_id and amount are required');
  }

  const response = await makeBackendRequest('/admin/credits/add', {
    method: 'POST',
    body: {
      user_id,
      amount: parseInt(amount),
      description,
    }
  }, request);

  if (!response.ok) {
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  }

  const data = await response.json();
  return NextResponse.json(data);
}));
