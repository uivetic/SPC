import { toast as showToast } from "@/components/ui/toast";

export const useToast = () => {
  return {
    toast: showToast,
  };
};

