import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PointsResponse, PointsWriteRequest, PointsWriteResponse } from "@/types/points";

export const usePoints = (name?: string) => {
  return useQuery<PointsResponse>({
    queryKey: ["points", name],
    queryFn: async () => {
      const response = await api.get(`/points/${name}`);
      return response.data;
    },
    enabled: !!name,
  });
};

export const useWritePoints = () => {
  const queryClient = useQueryClient();

  return useMutation<PointsWriteResponse, Error, PointsWriteRequest>({
    mutationFn: async (data) => {
      const response = await api.post("/points/write", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["points"] });
    },
  });
};

export const useAllPoints = () => {
  return useQuery({
    queryKey: ["points", "all"],
    queryFn: async () => {
      const response = await api.get("/points/all");
      return response.data;
    },
  });
};

