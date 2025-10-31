import { NextRequest } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export interface BackendRequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
}

function safeStringify(obj: any): string {
  try {
    const seen = new WeakSet();
    return JSON.stringify(obj, (key, value) => {
      if (typeof value === 'object' && value !== null) {
        if (seen.has(value)) {
          return '[Circular]';
        }
        seen.add(value);
      }
      return value;
    });
  } catch (e) {
    console.error('JSON stringify error:', e);
    throw new Error('Failed to serialize request body');
  }
}

export async function makeBackendRequest(
  endpoint: string,
  options: BackendRequestOptions = {},
  request?: NextRequest
): Promise<Response> {
  const {
    method = 'GET',
    headers = {},
    body,
    timeout = 30000
  } = options;

  if (request) {
    const authHeader = request.headers.get('Authorization');
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      body: body ? safeStringify(body) : undefined,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

export async function makeBackendFormRequest(
  endpoint: string,
  formData: FormData,
  options: Omit<BackendRequestOptions, 'body'> = {},
  request?: NextRequest
): Promise<Response> {
  const {
    method = 'POST',
    headers = {},
    timeout = 300000 // 5 minutes for file uploads
  } = options;

  // Forward authorization header if present
  if (request) {
    const authHeader = request.headers.get('Authorization');
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      method,
      headers,
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

export function getBackendUrl(): string {
  return BACKEND_URL;
}
