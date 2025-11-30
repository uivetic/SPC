import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { usePoints } from "@/hooks/usePoints";
import { useUsers, useSearchUsers } from "@/hooks/useUsers";
import { ArrowLeft } from "lucide-react";

export const ViewPoints = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedName, setSelectedName] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { data: allUsers, isLoading: usersLoading } = useUsers();
  const { data: searchResults, isLoading: searchLoading } = useSearchUsers(searchQuery);
  const { data: points, isLoading: pointsLoading } = usePoints(selectedName || undefined);

  // Filter users based on search query
  const filteredUsers = useMemo(() => {
    if (!searchQuery) {
      return allUsers || [];
    }
    
    if (searchResults && searchResults.length > 0) {
      return searchResults;
    }
    
    // Fallback: simple filter if search API doesn't return results
    const query = searchQuery.toLowerCase();
    return (allUsers || []).filter(user => 
      user.toLowerCase().includes(query)
    );
  }, [searchQuery, allUsers, searchResults]);

  const handleSelectName = (name: string) => {
    setSelectedName(name);
    setSearchQuery(name);
    setShowSuggestions(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setShowSuggestions(true);
    if (selectedName) {
      setSelectedName(null);
    }
  };

  const handleInputFocus = () => {
    setShowSuggestions(true);
  };

  const handleInputBlur = () => {
    // Delay hiding suggestions to allow click events
    setTimeout(() => {
      setShowSuggestions(false);
    }, 200);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Button variant="ghost" onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Nazad
          </Button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Pregled Bodova</CardTitle>
            <CardDescription>
              Pretražite i pregledajte bodove pojedinačnih članova
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Search */}
            <div className="relative">
              <label className="block text-sm font-medium mb-2">
                Pretraga osobe
              </label>
              <Input
                placeholder="Unesite ime osobe..."
                value={searchQuery}
                onChange={handleInputChange}
                onFocus={handleInputFocus}
                onBlur={handleInputBlur}
              />
              {showSuggestions && filteredUsers && filteredUsers.length > 0 && (
                <div className="absolute z-10 w-full mt-1 border rounded-md max-h-48 overflow-y-auto bg-white shadow-lg">
                  {filteredUsers.slice(0, 10).map((user) => (
                    <button
                      key={user}
                      type="button"
                      onClick={() => handleSelectName(user)}
                      className="w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors"
                    >
                      {user}
                    </button>
                  ))}
                  {filteredUsers.length > 10 && (
                    <div className="px-4 py-2 text-sm text-gray-500">
                      + {filteredUsers.length - 10} više rezultata
                    </div>
                  )}
                </div>
              )}
              {showSuggestions && searchQuery && !usersLoading && !searchLoading && filteredUsers.length === 0 && (
                <div className="absolute z-10 w-full mt-1 border rounded-md bg-white shadow-lg px-4 py-2 text-sm text-gray-500">
                  Nema rezultata
                </div>
              )}
            </div>

            {/* Points Display */}
            {selectedName && (
              <div>
                <h3 className="text-lg font-semibold mb-4">{selectedName}</h3>
                {pointsLoading ? (
                  <p>Učitavanje...</p>
                ) : points ? (
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600">HR</div>
                      <div className="text-2xl font-bold">{points.hr}</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600">Opšte</div>
                      <div className="text-2xl font-bold">{points.opste}</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600">Projekti</div>
                      <div className="text-2xl font-bold">{points.projekti}</div>
                    </div>
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600">Ukupno</div>
                      <div className="text-2xl font-bold">{points.ukupno}</div>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600">Status</div>
                      <div className="text-lg font-semibold">{points.status || "N/A"}</div>
                    </div>
                  </div>
                ) : (
                  <p>Nema podataka</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

