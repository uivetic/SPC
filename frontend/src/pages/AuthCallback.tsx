import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { saveToken } from "@/lib/auth";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const AuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const code = searchParams.get("code");
  const token = searchParams.get("token");
  const errorParam = searchParams.get("error");

  useEffect(() => {
    // If we have an error parameter
    if (errorParam) {
      setError(errorParam);
      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 3000);
      return;
    }

    // If we have a token directly (from backend redirect)
    if (token) {
      saveToken(token);
      // Use window.location to ensure full page reload and token is read
      window.location.href = "/dashboard";
      return;
    }

    // If we have a code, exchange it for a token
    if (code) {
      const exchangeCodeForToken = async () => {
        try {
          // Send code to backend to exchange for token
          const response = await axios.post(
            `${API_URL}/api/v1/auth/google/callback`,
            null,
            {
              params: { code },
            }
          );
          
          if (response.data.token) {
            saveToken(response.data.token);
            // Small delay to ensure token is saved, then use window.location for full reload
            setTimeout(() => {
              window.location.href = "/dashboard";
            }, 100);
          } else {
            setError("Failed to get token from server");
            setTimeout(() => {
              navigate("/login", { replace: true });
            }, 3000);
          }
        } catch (err: any) {
          console.error("Auth error:", err);
          setError(err.response?.data?.detail || "Authentication failed");
          setTimeout(() => {
            navigate("/login", { replace: true });
          }, 3000);
        }
      };

      exchangeCodeForToken();
    } else {
      // No code or token, redirect to login
      navigate("/login", { replace: true });
    }
  }, [code, token, errorParam, navigate]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">{error}</div>
          <div className="text-sm text-gray-600">Redirecting to login...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div>Processing authentication...</div>
    </div>
  );
};

