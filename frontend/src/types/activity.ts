export interface ActivityOption {
  value: string;
  label: string;
}

export interface ActivityCategory {
  category: string; // 'o', 'h', 'p'
  name: string; // 'Opšte', 'HR', 'Projekti'
  activities: Record<string, any>; // Activity name -> roles/points mapping (can be dict or list)
}

export interface ActivityResponse {
  categories: ActivityCategory[];
}

