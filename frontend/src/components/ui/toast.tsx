import { useState, useEffect } from "react";
import { X, CheckCircle2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface Toast {
  id: string;
  title: string;
  description?: string;
  variant?: "default" | "destructive";
}

let toastState: Toast[] = [];
let listeners: Array<() => void> = [];

const notify = () => {
  listeners.forEach((listener) => listener());
};

export const toast = ({ title, description, variant = "default" }: Omit<Toast, "id">) => {
  const id = Math.random().toString(36).substring(7);
  const newToast: Toast = { id, title, description, variant };
  toastState = [...toastState, newToast];
  notify();
  
  setTimeout(() => {
    toastState = toastState.filter((t) => t.id !== id);
    notify();
  }, 5000);
};

export const useToastState = () => {
  const [toasts, setToasts] = useState<Toast[]>(toastState);

  useEffect(() => {
    const listener = () => setToasts([...toastState]);
    listeners.push(listener);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  }, []);

  return toasts;
};

export const Toaster = () => {
  const toasts = useToastState();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toastItem) => (
        <Toast key={toastItem.id} toast={toastItem} />
      ))}
    </div>
  );
};

const Toast = ({ toast: toastItem }: { toast: Toast }) => {
  const removeToast = () => {
    toastState = toastState.filter((t) => t.id !== toastItem.id);
    notify();
  };

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-lg border p-4 shadow-lg min-w-[300px] max-w-[400px]",
        toast.variant === "destructive"
          ? "bg-red-50 border-red-200 text-red-800"
          : "bg-white border-gray-200 text-gray-900"
      )}
    >
      {toast.variant === "destructive" ? (
        <AlertCircle className="h-5 w-5 text-red-600" />
      ) : (
        <CheckCircle2 className="h-5 w-5 text-green-600" />
      )}
      <div className="flex-1">
        <div className="font-semibold">{toast.title}</div>
        {toast.description && (
          <div className="text-sm mt-1">{toast.description}</div>
        )}
      </div>
      <button
        onClick={removeToast}
        className="text-gray-400 hover:text-gray-600"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
};

