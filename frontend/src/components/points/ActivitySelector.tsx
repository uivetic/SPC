import { useState, useEffect } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { useActivities } from "@/hooks/useActivities";
import { ActivityCategory } from "@/types/activity";

interface ActivitySelectorProps {
  onSelectionChange: (data: string[] | null) => void;
}

export const ActivitySelector = ({ onSelectionChange }: ActivitySelectorProps) => {
  const { data: activitiesData, isLoading } = useActivities();
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedActivity, setSelectedActivity] = useState<string | null>(null);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [selectedQuarter, setSelectedQuarter] = useState<string | null>(null);
  const [selectedPoints, setSelectedPoints] = useState<string | null>(null);

  const currentCategory = activitiesData?.categories.find(
    (cat) => cat.category === selectedCategory
  );

  const currentActivityData = currentCategory?.activities[selectedActivity || ""] || {};

  useEffect(() => {
    if (selectedCategory && selectedActivity && selectedRole) {
      const category = activitiesData?.categories.find(
        (cat) => cat.category === selectedCategory
      );
      
      if (!category) {
        onSelectionChange(null);
        return;
      }

      const activityData = category.activities[selectedActivity];
      if (!activityData || typeof activityData !== "object") {
        onSelectionChange(null);
        return;
      }

      const roleData = activityData[selectedRole];
      if (!Array.isArray(roleData)) {
        onSelectionChange(null);
        return;
      }

      // For Opšte category
      if (selectedCategory === "o") {
        // Check if this activity needs kvartal (quarter)
        // Activities that need kvartal: "Aktivacija u godišnjim timovima", "Radne grupe"
        const needsKvartal = selectedActivity === "Aktivacija u godišnjim timovima" || 
                             selectedActivity === "Radne grupe";
        
        if (needsKvartal) {
          // For activities that need kvartal, we need: activity, role, kvartal, points
          // But wait - for "Radne grupe", the structure is different
          // Let me check the original logic...
          // Actually, looking at the code, "Radne grupe" uses item[3] for search when i==2
          // So the structure should be: [category, activity, role, kvartal/extra, points]
          if (selectedQuarter && selectedPoints) {
            const result = [
              selectedCategory,
              selectedActivity,
              selectedRole,
              selectedQuarter,
              selectedPoints,
            ];
            onSelectionChange(result);
          } else {
            onSelectionChange(null);
          }
        }
        // For other Opšte activities (like "Zapisničar na Skupštini"), 
        // role IS the kvartal (e.g., "I Kvartalna"), and points come from that
        else if (selectedPoints) {
          // For these, role is actually the kvartal/type
          const result = [
            selectedCategory,
            selectedActivity,
            selectedRole, // This is actually kvartal/type
            selectedPoints,
          ];
          onSelectionChange(result);
        } else {
          onSelectionChange(null);
        }
      }
      // For HR and Projekti, points come directly from role
      else if ((selectedCategory === "h" || selectedCategory === "p") && selectedPoints) {
        const result = [
          selectedCategory,
          selectedActivity,
          selectedRole,
          selectedPoints,
        ];
        onSelectionChange(result);
      } else {
        onSelectionChange(null);
      }
    } else {
      onSelectionChange(null);
    }
  }, [
    selectedCategory,
    selectedActivity,
    selectedRole,
    selectedQuarter,
    selectedPoints,
    activitiesData,
    onSelectionChange,
  ]);

  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value);
    setSelectedActivity(null);
    setSelectedRole(null);
    setSelectedQuarter(null);
    setSelectedPoints(null);
  };

  const handleActivityChange = (value: string) => {
    setSelectedActivity(value);
    setSelectedRole(null);
    setSelectedQuarter(null);
    setSelectedPoints(null);
  };

  const handleRoleChange = (value: string) => {
    setSelectedRole(value);
    setSelectedQuarter(null);
    setSelectedPoints(null);
  };

  if (isLoading) {
    return <div>Učitavanje aktivnosti...</div>;
  }

  if (!activitiesData) {
    return <div>Greška pri učitavanju aktivnosti</div>;
  }

  const roleOptions = selectedActivity
    ? Object.keys(currentActivityData)
    : [];

  const pointsOptions = selectedRole
    ? (currentActivityData[selectedRole] || [])
    : [];

  return (
    <div className="space-y-4">
      {/* Category Selection */}
      <div>
        <label className="block text-sm font-medium mb-2">
          Kategorija
        </label>
        <Select value={selectedCategory || ""} onValueChange={handleCategoryChange}>
          <SelectTrigger>
            <SelectValue placeholder="Izaberi kategoriju" />
          </SelectTrigger>
          <SelectContent>
            {activitiesData.categories.map((cat) => (
              <SelectItem key={cat.category} value={cat.category}>
                {cat.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Activity Selection */}
      {selectedCategory && (
        <div>
          <label className="block text-sm font-medium mb-2">
            Aktivnost
          </label>
          <Select
            value={selectedActivity || ""}
            onValueChange={handleActivityChange}
          >
            <SelectTrigger>
              <SelectValue placeholder="Izaberi aktivnost" />
            </SelectTrigger>
            <SelectContent>
              {Object.keys(currentCategory?.activities || {}).map((activity) => (
                <SelectItem key={activity} value={activity}>
                  {activity}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Role Selection */}
      {selectedActivity && roleOptions.length > 0 && (
        <div>
          <label className="block text-sm font-medium mb-2">
            Uloga
          </label>
          <Select value={selectedRole || ""} onValueChange={handleRoleChange}>
            <SelectTrigger>
              <SelectValue placeholder="Izaberi ulogu" />
            </SelectTrigger>
            <SelectContent>
              {roleOptions.map((role) => (
                <SelectItem key={role} value={role}>
                  {role}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Quarter Selection (only for Opšte - Aktivacija u godišnjim timovima and Radne grupe) */}
      {selectedCategory === "o" && 
       (selectedActivity === "Aktivacija u godišnjim timovima" || selectedActivity === "Radne grupe") && 
       selectedRole && (
        <div>
          <label className="block text-sm font-medium mb-2">
            {selectedActivity === "Radne grupe" ? "Dodatna vrednost" : "Kvartal"}
          </label>
          {selectedActivity === "Radne grupe" ? (
            <Input
              placeholder="Unesite dodatnu vrednost..."
              value={selectedQuarter || ""}
              onChange={(e) => setSelectedQuarter(e.target.value)}
            />
          ) : (
            <Select
              value={selectedQuarter || ""}
              onValueChange={setSelectedQuarter}
            >
              <SelectTrigger>
                <SelectValue placeholder="Izaberi kvartal" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="I">I</SelectItem>
                <SelectItem value="II">II</SelectItem>
                <SelectItem value="III">III</SelectItem>
                <SelectItem value="IV">IV</SelectItem>
              </SelectContent>
            </Select>
          )}
        </div>
      )}

      {/* Points Selection */}
      {selectedRole && pointsOptions.length > 0 && (
        <div>
          <label className="block text-sm font-medium mb-2">
            Poeni
          </label>
          <Select
            value={selectedPoints || ""}
            onValueChange={setSelectedPoints}
          >
            <SelectTrigger>
              <SelectValue placeholder="Izaberi poene" />
            </SelectTrigger>
            <SelectContent>
              {pointsOptions.map((point) => (
                <SelectItem key={String(point)} value={String(point)}>
                  {String(point)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}
    </div>
  );
};

