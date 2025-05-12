import { Realogram } from "../store/shelf/realogram";

export interface RealogramsPageResponse {
  realograms: Realogram[];
  total_count: number;
  page: number;
}