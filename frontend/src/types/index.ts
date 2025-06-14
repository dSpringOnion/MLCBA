export interface VehicleDetection {
  id: number;
  center: [number, number];
  speed: number;
  acceleration: number;
  lane_changes: number;
  erratic_movements: number;
  behavior_score: number;
  risk_level: 'SAFE' | 'RISKY' | 'DANGEROUS';
  ml_prediction: 'SAFE' | 'RISKY' | 'DANGEROUS';
  confidence: number;
}

export interface DetectionSummary {
  total_vehicles: number;
  risk_distribution: {
    SAFE: number;
    RISKY: number;
    DANGEROUS: number;
  };
  average_score: number;
  alert_level: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface ProcessingResult {
  annotated_image: string;
  detections: VehicleDetection[];
  summary: DetectionSummary;
}

export interface VideoAnalysisResult {
  total_frames: number;
  processed_frames: number;
  results: Array<{
    frame: number;
    id: number;
    risk_level: string;
    behavior_score: number;
    ml_prediction: string;
  }>;
  summary: {
    total_unique_vehicles: number;
    dangerous_vehicles: number;
    risky_vehicles: number;
    safe_vehicles: number;
  };
}

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface SampleVideo {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  duration: string;
  vehicles: number;
  riskLevel: 'low' | 'medium' | 'high';
}