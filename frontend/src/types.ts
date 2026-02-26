export type Domain = 'income' | 'sleep' | 'nutrition' | 'movement' | 'stress' | 'social';

export interface DailyPoint {
  date: string;
  o_delta_sum: number;
  cumulative: number;
  constraint_debt_7d: number;
  irreversibility_avg: number;
}

export interface WeeklyExposurePoint {
  week_start: string;
  count: number;
}

export interface AnalyticsSummary {
  totals: {
    sum_o_delta: number;
    avg_o_delta: number;
    constraint_debt_7d_last: number;
    exposure_count_period: number;
    readiness_latest: number;
    capitals_latest: { s: number; n: number; l: number; e: number };
    confidence_latest: number;
  };
  daily: DailyPoint[];
  weekly_exposure: WeeklyExposurePoint[];
}

export interface IncomeModelSettings {
  id: number;
  target_daily_income: number;
  w_s: number;
  w_n: number;
  w_l: number;
  w_e: number;
  half_life_days: number;
  exposure_goal_per_week: number;
  updated_at: string;
}

export interface IncomeModelPoint {
  date: string;
  s: number;
  n: number;
  l: number;
  e: number;
  readiness: number;
  confidence: number;
  low_data_confidence: boolean;
}

export interface IncomeModelSeries {
  daily: IncomeModelPoint[];
  current: IncomeModelPoint | null;
  settings: IncomeModelSettings;
  explanations: string[];
}
