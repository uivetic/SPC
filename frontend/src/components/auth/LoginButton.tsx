import { Button } from "@/components/ui/button";
import { getGoogleAuthUrl } from "@/lib/auth";

export const LoginButton = () => {
  const handleLogin = () => {
    window.location.href = getGoogleAuthUrl();
  };

  return (
    <Button onClick={handleLogin} size="lg" className="w-full">
      Sign in with Google
    </Button>
  );
};

