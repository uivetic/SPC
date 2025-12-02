import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { LogOut, FileText, Eye } from "lucide-react";

export const Dashboard = () => {
  const { user, logout, canWritePoints, canViewPoints } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Aplikacija za praćenje članstva</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.name || user?.email}</span>
            <Button variant="outline" onClick={logout} size="sm">
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {canWritePoints && (
            <Card>
              <CardHeader>
                <CardTitle>Upis bodova</CardTitle>
                <CardDescription>
                  Unesite bodove za članove
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Link to="/write-points">
                  <Button className="w-full">
                    <FileText className="h-4 w-4 mr-2" />
                    Upiši bodove
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}

          {canViewPoints && (
            <Card>
              <CardHeader>
                <CardTitle>Pregled bodova</CardTitle>
                <CardDescription>
                  Pregledajte bodove pojedinačnih članova
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Link to="/view-points">
                  <Button className="w-full" variant="outline">
                    <Eye className="h-4 w-4 mr-2" />
                    Pregledaj bodove
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )}

          {!canWritePoints && !canViewPoints && (
            <Card>
              <CardHeader>
                <CardTitle>Nemate pristup</CardTitle>
                <CardDescription>
                  Vaš email nema dozvolu za pristup aplikaciji.
                </CardDescription>
              </CardHeader>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
};

