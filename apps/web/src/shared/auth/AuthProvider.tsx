"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { authApi, type AuthUser } from "../api/auth";
import { clearSessionHint, hasSessionHint, setSessionHint } from "./session";

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
  const [isLoading, setIsLoading] = useState(() => hasSessionHint());

  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await authApi.getMe();
      setUser(response.user);
      setSessionHint();
    } catch {
      setUser(null);
      clearSessionHint();
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    // Visitors with no session hint must not trigger any setState here: a
    // client-side setState in this provider — however brief — duplicates
    // SSR content on force-dynamic pages (see Episode 14 postmortem). The
    // hint is a first-party cookie this app sets itself on successful
    // login/refresh, not a read of the API's own session/CSRF cookies —
    // those are invisible to document.cookie whenever the API is deployed
    // on a different origin than the frontend (separate subdomain in prod,
    // 127.0.0.1 vs localhost in CI).
    if (!hasSessionHint()) return;
    void refresh();
  }, [refresh]);

  async function login(email: string, password: string) {
    const response = await authApi.login({ email, password });
    setUser(response.user);
    setSessionHint();
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
    setSessionHint();
  }

  async function logout() {
    await authApi.logout().catch(() => undefined);
    setUser(null);
    clearSessionHint();
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
