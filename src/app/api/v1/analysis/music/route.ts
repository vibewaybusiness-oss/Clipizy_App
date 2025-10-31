import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth, ValidationError } from '../../middleware/error-handling';
import { makeBackendFormRequest } from '../../lib/utils/backend';

export const POST = withErrorHandling(requireAuth(async (request: NextRequest) => {
  const body = await request.json();
  const { track_id, audio_data } = body;

  if (!track_id) {
    throw new ValidationError('track_id is required');
  }

  if (!audio_data) {
    throw new ValidationError('audio_data is required for fallback analysis');
  }

  // Convert audio_data (data URI) to a file for upload
  const base64Data = audio_data.split(',')[1];
  const binaryData = atob(base64Data);
  const bytes = new Uint8Array(binaryData.length);
  for (let i = 0; i < binaryData.length; i++) {
    bytes[i] = binaryData.charCodeAt(i);
  }

  // Create a Blob and then a File
  const blob = new Blob([bytes], { type: 'audio/wav' });
  const file = new File([blob], `track_${track_id}.wav`, { type: 'audio/wav' });

  const formData = new FormData();
  formData.append('file', file);

  const response = await makeBackendFormRequest(
    '/api/analytics/analysis/analyze/comprehensive?analysis_type=music',
    formData,
    { timeout: 300000 }, // 5 minutes for analysis
    request
  );

  if (!response.ok) {
    const errorText = await response.text();
    console.error('Backend error response:', errorText);
    return NextResponse.json(
      { error: `Backend error: ${response.status} - ${errorText}` },
      { status: response.status }
    );
  }

  const data = await response.json();
  return NextResponse.json(data);
}));
