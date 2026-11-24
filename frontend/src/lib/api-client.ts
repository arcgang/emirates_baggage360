/**
 * Centralized API client for all backend communication.
 * Uses same-origin /api routing pattern.
 */

// API base is the only place /api is written on the frontend
const API_BASE = import.meta.env.VITE_API_URL ?? '/api';
const API_VERSION = '/v1';

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public code?: string
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = sessionStorage.getItem('access_token');
  const headers = new Headers(options.headers);
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const url = `${API_BASE}${API_VERSION}${path}`;
  
  try {
    const response = await fetch(url, { ...options, headers });
    
    // Handle 401 - clear token and redirect to login
    if (response.status === 401) {
      sessionStorage.removeItem('access_token');
      window.location.href = '/login';
      throw new ApiError(401, 'Unauthorized');
    }
    
    // Handle other non-2xx responses
    if (!response.ok) {
      let detail = 'Request failed';
      let code: string | undefined;
      
      try {
        const errorData = await response.json();
        detail = errorData.detail || detail;
        code = errorData.code;
      } catch {
        detail = await response.text() || detail;
      }
      
      throw new ApiError(response.status, detail, code);
    }
    
    // Handle 204 No Content
    if (response.status === 204) {
      return null as T;
    }
    
    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, error instanceof Error ? error.message : 'Network error');
  }
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path, { method: 'GET' }),
  
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),
  
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};

export { ApiError };
