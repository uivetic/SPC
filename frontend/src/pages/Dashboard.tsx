import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { LogOut, FileText, Eye, Users, Award } from "lucide-react";
import { useState } from "react";
import { CandidatesModal } from "@/components/candidates/CandidatesModal";
import { useYoungMemberCandidates, useFullMemberCandidates } from "@/hooks/useCandidates";

export const Dashboard = () => {
  const { user, logout, canWritePoints, canViewPoints } = useAuth();
  const [showYoungModal, setShowYoungModal] = useState(false);
  const [showFullModal, setShowFullModal] = useState(false);
  
  const {
    data: youngCandidatesData,
    refetch: fetchYoungCandidates,
    isLoading: loadingYoung,
  } = useYoungMemberCandidates();
  
  const {
    data: fullCandidatesData,
    refetch: fetchFullCandidates,
    isLoading: loadingFull,
  } = useFullMemberCandidates();

  const handleYoungMemberClick = async () => {
    await fetchYoungCandidates();
    setShowYoungModal(true);
  };

  const handleFullMemberClick = async () => {
    await fetchFullCandidates();
    setShowFullModal(true);
  };

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

          {canWritePoints && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Kandidati za mladog člana</CardTitle>
                  <CardDescription>
                    Pregled osoba sa više od 7 bodova i status N/A
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    className="w-full"
                    variant="outline"
                    onClick={handleYoungMemberClick}
                    disabled={loadingYoung}
                  >
                    <Users className="h-4 w-4 mr-2" />
                    {loadingYoung ? "Učitavanje..." : "Prikaži kandidate"}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Kandidati za punopravnog člana</CardTitle>
                  <CardDescription>
                    Pregled osoba sa više od 50 bodova i status BEBA
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    className="w-full"
                    variant="outline"
                    onClick={handleFullMemberClick}
                    disabled={loadingFull}
                  >
                    <Award className="h-4 w-4 mr-2" />
                    {loadingFull ? "Učitavanje..." : "Prikaži kandidate"}
                  </Button>
                </CardContent>
              </Card>
            </>
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

      <CandidatesModal
        title="Kandidati za mladog člana (> 7 bodova, status N/A)"
        candidates={youngCandidatesData?.candidates || []}
        isOpen={showYoungModal}
        onClose={() => setShowYoungModal(false)}
      />

      <CandidatesModal
        title="Kandidati za punopravnog člana (> 50 bodova, status BEBA)"
        candidates={fullCandidatesData?.candidates || []}
        isOpen={showFullModal}
        onClose={() => setShowFullModal(false)}
      />
    </div>
  );
};

