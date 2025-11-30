import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ActivityResponse } from "@/types/activity";

export const useActivities = () => {
  return useQuery<ActivityResponse>({
    queryKey: ["activities"],
    queryFn: async () => {
      const response = await api.get("/sheets/activities");
      return response.data;
    },
  });
};

