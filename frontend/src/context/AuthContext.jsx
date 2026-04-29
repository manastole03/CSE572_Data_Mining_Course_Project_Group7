import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { authApi } from "../api/tutor";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("memory_tutor_token");
    if (!token) {
      setLoading(false);
      return;
    }
    authApi
      .me()
      .then(setUser)
      .catch(() => localStorage.removeItem("memory_tutor_token"))
      .finally(() => setLoading(false));
  }, []);

  const commitAuth = (payload) => {
    localStorage.setItem("memory_tutor_token", payload.access_token);
    setUser(payload.user);
  };

  const value = useMemo(
    () => ({
      user,
      loading,
      login: async (payload) => commitAuth(await authApi.login(payload)),
      register: async (payload) => commitAuth(await authApi.register(payload)),
      demoLogin: async () => commitAuth(await authApi.demo()),
      logout: () => {
        localStorage.removeItem("memory_tutor_token");
        setUser(null);
      }
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

