"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { authApi, type AuthUser } from "../api/auth";
import { hasSessionCookie } from "./session";

type AuthContextValue = {
  user: AuthUser | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    displayName: string,
  ) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(() => hasSessionCookie());

  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await authApi.getMe();
      setUser(response.user);
    } catch {
      setUser(null);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    // Anonymous visitors (no CSRF cookie => definitely no session) must not
    // trigger any setState here: a client-side setState in this provider —
    // however brief — duplicates SSR content on force-dynamic pages (see
    // Episode 14 postmortem). The CSRF cookie is the one session signal
    // readable synchronously by JS, so it stands in for the old
    // localStorage-token check that did the same job pre-AE-3.
    if (!hasSessionCookie()) return;
    void refresh();
  }, [refresh]);

  async function login(email: string, password: string) {
    const response = await authApi.login({ email, password });
    setUser(response.user);
  }

  async function register(
    email: string,
    password: string,
    displayName: string,
  ) {
    const response = await authApi.register({
      email,
      password,
      display_name: displayName,
    });
    setUser(response.user);
  }

  async function logout() {
    await authApi.logout().catch(() => undefined);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{ user, isLoading, login, register, logout, refresh }}
    >
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
