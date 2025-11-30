import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export const useUsers = () => {
  return useQuery<string[]>({
    queryKey: ["users"],
    queryFn: async () => {
      const response = await api.get("/users");
      return response.data.users;
    },
  });
};

export const useSearchUsers = (query: string) => {
  return useQuery<string[]>({
    queryKey: ["users", "search", query],
    queryFn: async () => {
      const response = await api.get("/users/search", {
        params: { q: query },
      });
      return response.data.results;
    },
    enabled: query.length > 0,
  });
};

