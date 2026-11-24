/**
 * Common types shared across the application.
 */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ErrorResponse {
  detail: string;
  code?: string;
  correlation_id?: string;
}
