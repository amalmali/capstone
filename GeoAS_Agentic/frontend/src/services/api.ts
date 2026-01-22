/**
 * API Service - Connection to FastAPI Backend
 * Base URL: http://127.0.0.1:8000/llm
 */

// const API_BASE_URL = "http://127.0.0.1:8000/llm";
const API_BASE_URL = "/llm";

// ======================================================
// Types
// ======================================================

export interface VoiceResponse {
  status: "success" | "no_speech";
  query?: string;
  response?: string;
  source?: "protected" | "general";
  inside_geofence?: boolean;
  zone_name?: string | null;
  protection_level?: "high" | "medium" | "low" | null;
}

export interface AddPointResponse {
  status: "saved";
  inside: boolean;
  zone_name: string | null;
  protection_level: "high" | "medium" | "low" | null;
}

export interface MapDataResponse {
  zones: GeoJSON.FeatureCollection;
  points: GeoJSON.FeatureCollection;
}

export interface AnalyzeImageResponse {
  status: "success" | "error";
  violation_type?: string;
  violation_severity?: string;
  people_count?: number;
  detected_objects?: string[];
  confidence?: number;
  details?: string;
}

// ======================================================
// API Functions
// ======================================================

/**
 * Send text/voice query to the AI assistant
 * POST /llm/voice
 */
export async function sendQuery(
  query: string,
  useVoice: boolean = false
): Promise<VoiceResponse> {
  const formData = new FormData();
  formData.append("query", query);
  formData.append("use_voice", useVoice ? "true" : "false");

  const response = await fetch(`${API_BASE_URL}/voice`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Voice API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Add a GPS point and check if inside protected zone
 * POST /llm/add-point
 */
export async function addPoint(
  lat: number,
  lng: number
): Promise<AddPointResponse> {
  const response = await fetch(`${API_BASE_URL}/add-point`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ lat, lng }),
  });

  if (!response.ok) {
    throw new Error(`Add point API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get map data (zones and points)
 * GET /llm/map-data
 */
export async function getMapData(): Promise<MapDataResponse> {
  const response = await fetch(`${API_BASE_URL}/map-data`);

  if (!response.ok) {
    throw new Error(`Map data API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Analyze an image for violations
 * POST /llm/analyze-image
 */
export async function analyzeImage(
  file: File
): Promise<AnalyzeImageResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/analyze-image`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Analyze image API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Voice interaction (microphone input on backend)
 * POST /llm/voice with no query (backend handles mic)
 */
export async function voiceInteraction(
  useVoice: boolean = false
): Promise<VoiceResponse> {
  const formData = new FormData();
  formData.append("use_voice", useVoice ? "true" : "false");

  const response = await fetch(`${API_BASE_URL}/voice`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Voice API error: ${response.status}`);
  }

  return response.json();
}
