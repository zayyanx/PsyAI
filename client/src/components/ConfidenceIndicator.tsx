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

  const getIcon = (status: string) => {
    const iconSize = size === "sm" ? "h-3 w-3" : size === "lg" ? "h-5 w-5" : "h-4 w-4";
    if (status === "pass") return <CheckCircle className={iconSize} />;
    return <AlertTriangle className={iconSize} />;
  };

  const confidence = getConfidenceStatus(score);

  return (
    <div className={cn("space-y-2", className)} data-testid="confidence-indicator">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">AI Confidence</span>
        <span className={confidence.color} data-testid="confidence-score">
          {confidence.label} ({score}%)
        </span>
      </div>
      
      {showBadge && (
        <div className="flex items-center gap-2">
          <Badge 
            variant="outline" 
            className={cn(confidence.bg, confidence.color, confidence.border)}
            data-testid="confidence-badge"
          >
            {showIcon && getIcon(confidence.status)}
            <span className={showIcon ? "ml-1" : ""}>
              {confidence.label} ({score}%)
            </span>
          </Badge>
        </div>
      )}
    </div>
  );
}