import { X } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface Candidate {
  name: string;
  ukupno: string;
  status?: string;
}

interface CandidatesModalProps {
  title: string;
  candidates: Candidate[];
  isOpen: boolean;
  onClose: () => void;
}

export const CandidatesModal = ({
  title,
  candidates,
  isOpen,
  onClose,
}: CandidatesModalProps) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <Card
        className="w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle>{title}</CardTitle>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto">
          {candidates.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              Nema kandidata koji zadovoljavaju uslove.
            </p>
          ) : (
            <div className="space-y-2">
              {candidates.map((candidate, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex flex-col">
                    <span className="font-medium">{candidate.name}</span>
                    {candidate.status && (
                      <span className="text-sm text-gray-500">Status: {candidate.status}</span>
                    )}
                  </div>
                  <span className="text-lg font-semibold text-blue-600">
                    {parseFloat(candidate.ukupno).toFixed(1)} bodova
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

