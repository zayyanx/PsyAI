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
  compact?: boolean; // When true, don't render Card wrapper
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
  compact = false,
  className,
}: DetailedConfidenceProps) {
  const getConfidenceStatus = (score: number) => {
    // Pass/Fail threshold at 90%
    if (score >= 90) return { 
      status: "pass",
      label: "Pass", 
      color: "text-success", 
      bg: "bg-success/10", 
      border: "border-success/20" 
    };
    return { 
      status: "fail",
      label: "Fail", 
      color: "text-destructive", 
      bg: "bg-destructive/10", 
      border: "border-destructive/20" 
    };
  };

  const getOverallIcon = (status: string) => {
    const iconSize = size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4";
    if (status === "pass") return <CheckCircle className={iconSize} />;
    return <AlertTriangle className={iconSize} />;
  };

  const overallConfidence = getConfidenceStatus(overallScore);
  const progressHeight = size === "sm" ? "h-1" : size === "lg" ? "h-2" : "h-1.5";

  const metrics: ConfidenceMetric[] = [
    {
      name: "Decision Alignment",
      score: decisionAlignment ?? null,
      description: "Alignment with clinical protocols and guidelines",
      icon: Target,
    },
    {
      name: "Clinical Accuracy", 
      score: clinicalAccuracy ?? null,
      description: "Medical soundness and correctness of response",
      icon: Stethoscope,
    },
    {
      name: "Safety Assessment",
      score: safetyAssessment ?? null, 
      description: "Safety of recommendations and risk management",
      icon: Shield,
    },
    {
      name: "Context Understanding",
      score: contextUnderstanding ?? null,
      description: "AI's comprehension of patient situation",
      icon: Brain,
    },
    {
      name: "Response Appropriateness",
      score: responseAppropriateness ?? null,
      description: "Tone, empathy, and communication suitability",
      icon: MessageCircle,
    },
  ];

  const hasDetailedScores = metrics.some(metric => metric.score !== null && metric.score !== undefined);

  // Calculate overall score as percentage of metrics that pass (score >= 90%)
  const calculateOverallScore = () => {
    const validMetrics = metrics.filter(m => m.score !== null && m.score !== undefined);
    if (validMetrics.length === 0) return overallScore; // Fallback to provided score
    
    const passingMetrics = validMetrics.filter(m => m.score! >= 90).length;
    return Math.round((passingMetrics / validMetrics.length) * 100);
  };

  const calculatedOverallScore = hasDetailedScores ? calculateOverallScore() : overallScore;
  const overallConfidenceCalculated = getConfidenceStatus(calculatedOverallScore);

  const overallContent = showOverall && (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">Overall AI Confidence</span>
        <span className={overallConfidenceCalculated.color} data-testid="overall-confidence-score">
          {overallConfidenceCalculated.label} ({calculatedOverallScore}%)
        </span>
      </div>
      
      <Progress value={calculatedOverallScore} className={progressHeight} data-testid="overall-confidence-progress" />
      
      <div className="flex items-center gap-2">
        <Badge 
          variant="outline" 
          className={cn(overallConfidenceCalculated.bg, overallConfidenceCalculated.color, overallConfidenceCalculated.border)}
          data-testid="overall-confidence-badge"
        >
          {getOverallIcon(overallConfidenceCalculated.status)}
          <span className="ml-1">
            {overallConfidenceCalculated.label} ({calculatedOverallScore}%)
          </span>
        </Badge>
      </div>
    </div>
  );

  const detailsContent = showDetails && hasDetailedScores && (
    <div className="space-y-4">
      {!compact && (
        <h4 className="text-sm font-medium">Confidence Breakdown</h4>
      )}
      {metrics.map((metric) => {
        if (metric.score === null || metric.score === undefined) return null;
        
        const confidence = getConfidenceStatus(metric.score);
        const IconComponent = metric.icon;
        
        return (
          <div key={metric.name} className="space-y-2">
            <div className="flex items-center gap-2">
              <IconComponent className="h-4 w-4 text-muted-foreground" />
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">{metric.name}</span>
                  <span className={cn("text-sm font-medium", confidence.color)}>
                    {confidence.label}
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
    </div>
  );

  const noDataContent = showDetails && !hasDetailedScores && (
    <div className="text-center text-muted-foreground">
      <Brain className="h-8 w-8 mx-auto mb-2 opacity-50" />
      <p className="text-sm">Detailed confidence breakdown not available</p>
      <p className="text-xs mt-1">Only overall confidence score is provided</p>
    </div>
  );

  if (compact) {
    return (
      <div className={cn("space-y-4", className)} data-testid="detailed-confidence-indicator">
        {overallContent}
        {detailsContent}
        {noDataContent}
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)} data-testid="detailed-confidence-indicator">
      {showOverall && (
        <Card>
          <CardContent className="pt-4">
            {overallContent}
          </CardContent>
        </Card>
      )}

      {showDetails && hasDetailedScores && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Confidence Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            {detailsContent}
          </CardContent>
        </Card>
      )}

      {showDetails && !hasDetailedScores && (
        <Card>
          <CardContent className="pt-4">
            {noDataContent}
          </CardContent>
        </Card>
      )}
    </div>
  );
}