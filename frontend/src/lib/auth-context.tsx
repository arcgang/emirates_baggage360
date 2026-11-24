/**
 * Authentication context provider.
 * Manages login/logout and token storage.
 */
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from './api-client';

interface User {
  user_id: string;
  role: string;
  display_name: string;
  scopes: string[];
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = sessionStorage.getItem('access_token');
    if (token) {
      // Fetch current user
      fetchCurrentUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const principal = await apiClient.get<User>('/auth/me');
      setUser(principal);
    } catch (error) {
      // Token invalid or expired
      sessionStorage.removeItem('access_token');
      setUser(null);
    }
  };

  const login = async (credentials: LoginCredentials) => {
    const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
    
    // Store token
    sessionStorage.setItem('access_token', response.access_token);
    
    // Set user
    setUser(response.user);
  };

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      // Logout endpoint may not exist yet, continue anyway
      console.warn('Logout endpoint error:', error);
    }
    
    // Clear token and user
    sessionStorage.removeItem('access_token');
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
