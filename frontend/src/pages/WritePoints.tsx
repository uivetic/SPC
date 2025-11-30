import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { NameSelector } from "@/components/points/NameSelector";
import { ActivitySelector } from "@/components/points/ActivitySelector";
import { useWritePoints } from "@/hooks/usePoints";
import { ArrowLeft, CheckCircle2, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/useToast";

export const WritePoints = () => {
  const navigate = useNavigate();
  const [selectedNames, setSelectedNames] = useState<string[]>([]);
  const [activityData, setActivityData] = useState<string[] | null>(null);
  const writePoints = useWritePoints();
  const { toast } = useToast();

  const handleAddName = (name: string) => {
    if (!selectedNames.includes(name)) {
      setSelectedNames([...selectedNames, name]);
    }
  };

  const handleRemoveName = (name: string) => {
    setSelectedNames(selectedNames.filter((n) => n !== name));
  };

  const handleSubmit = async () => {
    if (selectedNames.length === 0) {
      toast({
        title: "Greška",
        description: "Morate izabrati bar jednu osobu",
        variant: "destructive",
      });
      return;
    }

    if (!activityData || activityData.length < 3) {
      toast({
        title: "Greška",
        description: "Morate popuniti sve aktivnosti (kategorija, aktivnost, uloga, poeni)",
        variant: "destructive",
      });
      return;
    }

    // Prepare batch data
    const batch: string[][] = [[], [], []];
    
    // Determine which category is selected
    const category = activityData[0];
    if (category === "o") {
      batch[0] = activityData;
    } else if (category === "h") {
      batch[1] = activityData;
    } else if (category === "p") {
      batch[2] = activityData;
    }

    // Get points value
    const points = activityData[activityData.length - 1];

    // Create pairs: [(name, points), ...]
    const pairs = selectedNames.map((name) => [name, points]);

    try {
      const result = await writePoints.mutateAsync({
        batch,
        pairs,
      });

      toast({
        title: "Uspeh!",
        description: result.message,
      });

      // Reset form
      setSelectedNames([]);
      setActivityData(null);
    } catch (error: any) {
      toast({
        title: "Greška",
        description: error.response?.data?.detail || "Greška pri upisu bodova",
        variant: "destructive",
      });
    }
  };

  const isFormValid = selectedNames.length > 0 && activityData && activityData.length >= 3;

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
            <CardTitle>Upis Bodova</CardTitle>
            <CardDescription>
              Izaberite osobe i aktivnosti za upis bodova
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Name Selection */}
            <NameSelector
              selectedNames={selectedNames}
              onAddName={handleAddName}
              onRemoveName={handleRemoveName}
            />

            {/* Activity Selection */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Aktivnost</h3>
              <ActivitySelector onSelectionChange={setActivityData} />
            </div>

            {/* Form Status */}
            {activityData && (
              <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <span className="text-sm text-green-800">
                    Aktivnost izabrana: {activityData.join(" → ")}
                  </span>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <Button
              onClick={handleSubmit}
              disabled={!isFormValid || writePoints.isPending}
              className="w-full"
              size="lg"
            >
              {writePoints.isPending ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Upisivanje...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Upiši bodove za {selectedNames.length} {selectedNames.length === 1 ? "osobu" : "osoba"}
                </>
              )}
            </Button>

            {!isFormValid && selectedNames.length > 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-yellow-600" />
                  <span className="text-sm text-yellow-800">
                    Popunite sve aktivnosti pre upisa
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};
