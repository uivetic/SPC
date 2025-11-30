import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { User } from "@/types/user";
import { isAuthenticated, removeToken } from "@/lib/auth";

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

  return {
    user,
    isLoading,
    isAuthenticated: !!user && !error,
    logout,
  };
};

