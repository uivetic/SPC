export interface PointsResponse {
  hr: string;
  opste: string;
  projekti: string;
  ukupno: string;
  status: string;
}

export interface PointsWriteRequest {
  batch: string[][];
  pairs: [string, string][];
}

export interface PointsWriteResponse {
  success: boolean;
  message: string;
  count: number;
}

