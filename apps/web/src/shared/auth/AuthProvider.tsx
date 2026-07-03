"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { authApi, type AuthUser } from "../api/auth";
import { clearStoredToken, getStoredToken, setStoredToken } from "./session";

type AuthContextValue = {
  user: AuthUser | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!getStoredToken()) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const response = await authApi.getMe();
      setUser(response.user);
    } catch {
      clearStoredToken();
      setUser(null);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function login(email: string, password: string) {
    const response = await authApi.login({ email, password });
    setStoredToken(response.token);
    setUser(response.user);
  }

  async function register(email: string, password: string, displayName: string) {
    const response = await authApi.register({
      email,
      password,
      display_name: displayName,
    });
    setStoredToken(response.token);
    setUser(response.user);
  }

  async function logout() {
    await authApi.logout().catch(() => undefined);
    clearStoredToken();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
