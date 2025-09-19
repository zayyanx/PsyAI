import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Bot, User, Stethoscope, AlertTriangle, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ChatMessageProps {
  id: string;
  sender: "patient" | "ai" | "expert";
  content: string;
  timestamp: string;
  confidenceScore?: number;
  expertAnnotation?: string;
  isReviewed?: boolean;
  viewerRole?: "patient" | "expert"; // Controls what information is visible
}

export default function ChatMessage({
  sender,
  content,
  timestamp,
  confidenceScore,
  expertAnnotation,
  isReviewed = false,
  viewerRole = "patient",
}: ChatMessageProps) {
  const isPatient = sender === "patient";
  const isAI = sender === "ai";
  const isExpert = sender === "expert";

  const getIcon = () => {
    if (isPatient) return <User className="h-4 w-4" />;
    if (isAI) return <Bot className="h-4 w-4" />;
    return <Stethoscope className="h-4 w-4" />;
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 80) return "text-success";
    if (score >= 60) return "text-warning";
    return "text-destructive";
  };

  const getConfidenceBadge = (score: number) => {
    if (score >= 80) return <Badge variant="outline" className="bg-success/10 text-success border-success/20">High Confidence</Badge>;
    if (score >= 60) return <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">Medium Confidence</Badge>;
    return <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/20">Low Confidence</Badge>;
  };

  return (
    <div
      className={cn(
        "flex gap-3 mb-4",
        isPatient && "flex-row-reverse"
      )}
      data-testid={`message-${sender}`}
    >
      <Avatar className="h-8 w-8 flex-shrink-0">
        <AvatarFallback className={cn(
          isPatient && "bg-primary text-primary-foreground",
          isAI && "bg-chart-1 text-white",
          isExpert && "bg-medical-blue text-medical-blue-foreground"
        )}>
          {getIcon()}
        </AvatarFallback>
      </Avatar>

      <div className={cn("flex-1 space-y-2", isPatient && "max-w-xs")}>
        <Card className={cn(
          "p-4",
          isPatient && "bg-primary text-primary-foreground",
          isAI && "bg-card border-chart-1/20",
          isExpert && "bg-medical-blue text-medical-blue-foreground"
        )}>
          <div className="space-y-2">
            <p className="text-sm leading-relaxed" data-testid="message-content">
              {content}
            </p>
            
            {/* AI Confidence Score - Only show to experts/reviewers, never to patients */}
            {viewerRole === "expert" && isAI && confidenceScore !== undefined && (
              <div className="space-y-2 pt-2 border-t border-border/50">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Confidence Score</span>
                  <span className={getConfidenceColor(confidenceScore)}>
                    {confidenceScore}%
                  </span>
                </div>
                <Progress value={confidenceScore} className="h-1" />
                <div className="flex gap-2">
                  {getConfidenceBadge(confidenceScore)}
                  {isReviewed && (
                    <Badge variant="outline" className="bg-success/10 text-success border-success/20">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Expert Reviewed
                    </Badge>
                  )}
                </div>
              </div>
            )}

            {/* Expert Annotation - Only show to experts/reviewers, never to patients */}
            {viewerRole === "expert" && expertAnnotation && (
              <Card className="p-3 bg-warning/10 border-warning/20">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-warning flex-shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-warning">Expert Note</p>
                    <p className="text-xs text-muted-foreground">{expertAnnotation}</p>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </Card>

        <div className="text-xs text-muted-foreground px-2" data-testid="message-timestamp">
          {timestamp}
        </div>
      </div>
    </div>
  );
}