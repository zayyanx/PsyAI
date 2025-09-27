import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, CheckCircle, AlertCircle, Brain, Shield, Target, MessageCircle, Stethoscope } from "lucide-react";
import { cn } from "@/lib/utils";

export interface DetailedConfidenceProps {
  overallScore: number;
  decisionAlignment?: number | null;
  clinicalAccuracy?: number | null;
  safetyAssessment?: number | null;
  contextUnderstanding?: number | null;
  responseAppropriateness?: number | null;
  showOverall?: boolean;
  showDetails?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

interface ConfidenceMetric {
  name: string;
  score: number | null;
  description: string;
  icon: React.ElementType;
}

export default function DetailedConfidenceIndicator({
  overallScore,
  decisionAlignment,
  clinicalAccuracy,
  safetyAssessment,
  contextUnderstanding,
  responseAppropriateness,
  showOverall = true,
  showDetails = true,
  size = "md",
  className,
}: DetailedConfidenceProps) {
  const getConfidenceLevel = (score: number) => {
    if (score >= 90) return { level: "high", color: "text-success", bg: "bg-success/10", border: "border-success/20" };
    if (score >= 70) return { level: "medium", color: "text-warning", bg: "bg-warning/10", border: "border-warning/20" };
    return { level: "low", color: "text-destructive", bg: "bg-destructive/10", border: "border-destructive/20" };
  };

  const getOverallIcon = (level: string) => {
    const iconSize = size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4";
    if (level === "high") return <CheckCircle className={iconSize} />;
    if (level === "medium") return <AlertCircle className={iconSize} />;
    return <AlertTriangle className={iconSize} />;
  };

  const overallConfidence = getConfidenceLevel(overallScore);
  const progressHeight = size === "sm" ? "h-1" : size === "lg" ? "h-2" : "h-1.5";

  const metrics: ConfidenceMetric[] = [
    {
      name: "Decision Alignment",
      score: decisionAlignment,
      description: "Alignment with clinical protocols and guidelines",
      icon: Target,
    },
    {
      name: "Clinical Accuracy", 
      score: clinicalAccuracy,
      description: "Medical soundness and correctness of response",
      icon: Stethoscope,
    },
    {
      name: "Safety Assessment",
      score: safetyAssessment, 
      description: "Safety of recommendations and risk management",
      icon: Shield,
    },
    {
      name: "Context Understanding",
      score: contextUnderstanding,
      description: "AI's comprehension of patient situation",
      icon: Brain,
    },
    {
      name: "Response Appropriateness",
      score: responseAppropriateness,
      description: "Tone, empathy, and communication suitability",
      icon: MessageCircle,
    },
  ];

  const hasDetailedScores = metrics.some(metric => metric.score !== null && metric.score !== undefined);

  return (
    <div className={cn("space-y-4", className)} data-testid="detailed-confidence-indicator">
      {showOverall && (
        <Card>
          <CardContent className="pt-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Overall AI Confidence</span>
                <span className={overallConfidence.color} data-testid="overall-confidence-score">
                  {overallScore}%
                </span>
              </div>
              
              <Progress value={overallScore} className={progressHeight} data-testid="overall-confidence-progress" />
              
              <div className="flex items-center gap-2">
                <Badge 
                  variant="outline" 
                  className={cn(overallConfidence.bg, overallConfidence.color, overallConfidence.border)}
                  data-testid="overall-confidence-badge"
                >
                  {getOverallIcon(overallConfidence.level)}
                  <span className="ml-1">
                    {overallConfidence.level.charAt(0).toUpperCase() + overallConfidence.level.slice(1)} Confidence
                  </span>
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {showDetails && hasDetailedScores && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Confidence Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {metrics.map((metric) => {
              if (metric.score === null || metric.score === undefined) return null;
              
              const confidence = getConfidenceLevel(metric.score);
              const IconComponent = metric.icon;
              
              return (
                <div key={metric.name} className="space-y-2">
                  <div className="flex items-center gap-2">
                    <IconComponent className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">{metric.name}</span>
                        <span className={cn("text-sm font-medium", confidence.color)}>
                          {metric.score}%
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {metric.description}
                      </p>
                    </div>
                  </div>
                  <Progress 
                    value={metric.score} 
                    className={progressHeight}
                    data-testid={`progress-${metric.name.toLowerCase().replace(' ', '-')}`}
                  />
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}

      {showDetails && !hasDetailedScores && (
        <Card>
          <CardContent className="pt-4">
            <div className="text-center text-muted-foreground">
              <Brain className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Detailed confidence breakdown not available</p>
              <p className="text-xs mt-1">Only overall confidence score is provided</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}