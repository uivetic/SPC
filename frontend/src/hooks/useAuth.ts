import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { User } from "@/types/user";
import { isAuthenticated, removeToken } from "@/lib/auth";

interface UserPermissions {
  email: string;
  can_write_points: boolean;
  can_view_points: boolean;
}

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

  // Fetch user permissions from backend
  const { data: permissions, error: permissionsError } = useQuery<UserPermissions>({
    queryKey: ["auth", "permissions"],
    queryFn: async () => {
      const response = await api.get("/auth/permissions");
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
    isLoading: isLoading || (isAuthenticated() && permissions === undefined && permissionsError === undefined),
    isAuthenticated: !!user && !error,
    logout,
    canWritePoints: permissions?.can_write_points ?? false,
    canViewPoints: permissions?.can_view_points ?? false,
    permissionsError,
  };
};

