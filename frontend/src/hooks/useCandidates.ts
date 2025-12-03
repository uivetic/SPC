import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface Candidate {
  name: string;
  ukupno: string;
  status?: string;
}

interface CandidatesResponse {
  candidates: Candidate[];
}

export const useYoungMemberCandidates = () => {
  return useQuery<CandidatesResponse>({
    queryKey: ["candidates", "young-member"],
    queryFn: async () => {
      const response = await api.get("/points/candidates/young-member");
      return response.data;
    },
    enabled: false, // Only fetch when explicitly called
  });
};

export const useFullMemberCandidates = () => {
  return useQuery<CandidatesResponse>({
    queryKey: ["candidates", "full-member"],
    queryFn: async () => {
      const response = await api.get("/points/candidates/full-member");
      return response.data;
    },
    enabled: false, // Only fetch when explicitly called
  });
};

