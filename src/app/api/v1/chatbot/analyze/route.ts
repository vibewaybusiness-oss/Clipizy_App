import { NextRequest, NextResponse } from "next/server";
import { makeBackendRequest } from "@/app/api/v1/lib/utils/backend";
import { requireAuth, withErrorHandling } from "@/app/api/v1/middleware/error-handling";

export const POST = withErrorHandling(requireAuth(async (request: NextRequest) => {
  const body = await request.json();
  
  const response = await makeBackendRequest('/api/chatbot/analyze', {
    method: 'POST',
    body: {
      user_input: body.user_input || body.prompt || "",
      input_tracks: body.input_tracks || 0,
      input_images: body.input_images || 0,
      conversation_id: body.conversation_id || null,
      user_response: body.user_response || null,
    },
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 300000,
  }, request);

  if (!response.ok) {
    const errorData = await response.text();
    return NextResponse.json(
      { error: `Backend error: ${response.status} ${errorData}` },
      { status: response.status }
    );
  }

  const data = await response.json();
  return NextResponse.json(data);
}));

