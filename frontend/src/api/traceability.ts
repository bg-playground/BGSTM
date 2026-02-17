import { apiClient } from "./client";

export interface LinkedTestCase {
  test_case_id: string;
  title: string;
  link_status: string;
  link_id: string;
  link_type: string;
  confidence_score?: number;
}

export interface RequirementCoverage {
  requirement_id: string;
  requirement_title: string;
  external_id?: string;
  linked_test_cases: LinkedTestCase[];
  coverage_status: string;
}

export interface OrphanTestCase {
  test_case_id: string;
  title: string;
  external_id?: string;
}

export interface TraceabilityMatrix {
  coverage_percentage: number;
  total_requirements: number;
  covered_requirements: number;
  uncovered_requirements: number;
  total_test_cases: number;
  orphan_test_cases: number;
  matrix: RequirementCoverage[];
  orphans: OrphanTestCase[];
}

export interface AlgorithmMetrics {
  algorithm: string;
  total_suggestions: number;
  accepted_suggestions: number;
  rejected_suggestions: number;
  pending_suggestions: number;
  acceptance_rate: number;
}

export interface Metrics {
  coverage_percentage: number;
  suggestion_acceptance_rate: number;
  total_requirements: number;
  total_test_cases: number;
  total_links: number;
  total_suggestions: number;
  accepted_suggestions: number;
  rejected_suggestions: number;
  pending_suggestions: number;
  manual_links: number;
  ai_suggested_links: number;
  algorithm_breakdown: AlgorithmMetrics[];
}

const traceabilityApi = {
  async getMatrix(): Promise<TraceabilityMatrix> {
    const response = await apiClient.get<TraceabilityMatrix>("/traceability-matrix");
    return response.data;
  },

  async getMetrics(): Promise<Metrics> {
    const response = await apiClient.get<Metrics>("/metrics");
    return response.data;
  },

  async exportMatrix(format: "csv" | "json"): Promise<Blob> {
    const response = await apiClient.get(`/traceability-matrix/export?format=${format}`, {
      responseType: "blob",
    });
    return response.data;
  },

  downloadExport(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};

export default traceabilityApi;
