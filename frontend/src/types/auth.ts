/**
 * Authentication and authorization types.
 */

export interface PrincipalContext {
  user_id: string;
  role: string;
  display_name: string;
  scopes: string[];
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: PrincipalContext;
}
