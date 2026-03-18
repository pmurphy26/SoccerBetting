export interface User {
  name: string;
}

export type TimeGrouping = "weekly" | "biweekly" | "monthly";

export interface NetworkData {
  id: number;
  matchInfo: {
    matchDate: string;
    team1ID: number;
    team2ID: number;
    team1IsHome?: boolean;
    completed?: boolean;
  };
  finalScore?: {
    home: number;
    away: number;
    matchResult: number;
  };
  bookOdds?: {
    home: number;
    draw: number;
    away: number;
  };
  predicted: {
    home: number;
    draw: number;
    away: number;
    predictedResult: number;
  };
  networkInput?: {
    home_strength: number[];
    away_strength: number[];
    home_form: number[];
    away_form: number[];
  };
}

export enum GRAPH_INTERFACE {
  showMultipleYears = "Show seasons graphs",
  showMultipleLeagues = "Shows leagues graphs",
  showSingleGraph = "Show single graph",
}
