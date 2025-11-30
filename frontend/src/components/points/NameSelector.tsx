import { useState } from "react";
import { Input } from "@/components/ui/input";
import { useUsers, useSearchUsers } from "@/hooks/useUsers";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NameSelectorProps {
  selectedNames: string[];
  onAddName: (name: string) => void;
  onRemoveName: (name: string) => void;
}

export const NameSelector = ({
  selectedNames,
  onAddName,
  onRemoveName,
}: NameSelectorProps) => {
  const [searchQuery, setSearchQuery] = useState("");
  const { data: users } = useUsers();
  const { data: searchResults } = useSearchUsers(searchQuery);

  const displayUsers = searchQuery ? (searchResults || []) : (users || []);

  const handleUserClick = (user: string) => {
    if (!selectedNames.includes(user)) {
      onAddName(user);
    }
    setSearchQuery("");
  };

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Pretraga i dodavanje osoba
        </label>
        <Input
          placeholder="Pretraži osobe..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {searchQuery && displayUsers.length > 0 && (
          <div className="mt-2 border rounded-md max-h-48 overflow-y-auto bg-white shadow-lg">
            {displayUsers.map((user) => (
              <button
                key={user}
                onClick={() => handleUserClick(user)}
                className="w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors"
              >
                {user}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected Names */}
      {selectedNames.length > 0 && (
        <div>
          <label className="block text-sm font-medium mb-2">
            Izabrane osobe ({selectedNames.length})
          </label>
          <div className="flex flex-wrap gap-2">
            {selectedNames.map((name) => (
              <div
                key={name}
                className="flex items-center gap-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full"
              >
                <span>{name}</span>
                <button
                  onClick={() => onRemoveName(name)}
                  className="text-blue-600 hover:text-blue-800 ml-1"
                  aria-label={`Ukloni ${name}`}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

