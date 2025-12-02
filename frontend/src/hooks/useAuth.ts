import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { User } from "@/types/user";
import { isAuthenticated, removeToken } from "@/lib/auth";
import { useMemo } from "react";

// Allowed emails for writing points
const ALLOWED_WRITE_EMAILS = [
  "hr@best.rs",
  "vpp@best.rs",
  "secretary@best.rs",
  "fr@best.rs",
  "president@best.rs",
  "pr@best.rs",
  "treasurer@best.rs",
];

export const useAuth = () => {
  const { data: user, isLoading, error } = useQuery<User>({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const response = await api.get("/auth/me");
      return response.data;
    },
    enabled: isAuthenticated(),
    retry: false,
  });

  const logout = () => {
    removeToken();
    window.location.href = "/login";
  };

  // Check if user can write points
  const canWritePoints = useMemo(() => {
    if (!user?.email) return false;
    return ALLOWED_WRITE_EMAILS.some(
      (email) => email.toLowerCase() === user.email.toLowerCase()
    );
  }, [user?.email]);

  // Check if user can view points (all @best.rs emails)
  const canViewPoints = useMemo(() => {
    if (!user?.email) return false;
    return user.email.toLowerCase().endsWith("@best.rs");
  }, [user?.email]);

  return {
    user,
    isLoading,
    isAuthenticated: !!user && !error,
    logout,
    canWritePoints,
    canViewPoints,
  };
};

