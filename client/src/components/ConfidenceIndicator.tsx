import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ConfidenceIndicatorProps {
  score: number;
  showBadge?: boolean;
  showIcon?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export default function ConfidenceIndicator({
  score,
  showBadge = true,
  showIcon = true,
  size = "md",
  className,
}: ConfidenceIndicatorProps) {
  const getConfidenceLevel = (score: number) => {
    if (score >= 80) return { level: "high", color: "text-success", bg: "bg-success/10", border: "border-success/20" };
    if (score >= 60) return { level: "medium", color: "text-warning", bg: "bg-warning/10", border: "border-warning/20" };
    return { level: "low", color: "text-destructive", bg: "bg-destructive/10", border: "border-destructive/20" };
  };

  const getIcon = (level: string) => {
    const iconSize = size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4";
    if (level === "high") return <CheckCircle className={iconSize} />;
    if (level === "medium") return <AlertCircle className={iconSize} />;
    return <AlertTriangle className={iconSize} />;
  };

  const confidence = getConfidenceLevel(score);
  const progressHeight = size === "sm" ? "h-1" : size === "lg" ? "h-2" : "h-1.5";

  return (
    <div className={cn("space-y-2", className)} data-testid="confidence-indicator">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">AI Confidence</span>
        <span className={confidence.color} data-testid="confidence-score">
          {score}%
        </span>
      </div>
      
      <Progress value={score} className={progressHeight} data-testid="confidence-progress" />
      
      {showBadge && (
        <div className="flex items-center gap-2">
          <Badge 
            variant="outline" 
            className={cn(confidence.bg, confidence.color, confidence.border)}
            data-testid="confidence-badge"
          >
            {showIcon && getIcon(confidence.level)}
            <span className={showIcon ? "ml-1" : ""}>
              {confidence.level.charAt(0).toUpperCase() + confidence.level.slice(1)} Confidence
            </span>
          </Badge>
        </div>
      )}
    </div>
  );
}