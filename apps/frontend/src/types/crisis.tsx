export interface CrisisEvent {
    id: number;

    title: string;
    location: string;

    severity:
    | "low"
    | "moderate"
    | "high"
    | "critical";

    riskScore: number;

    confidence: number;

    summary: string;

    impact: string[];

    coordinates: [
        number,
        number
    ];
}