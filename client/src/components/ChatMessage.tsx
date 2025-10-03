import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Bot, User, Stethoscope, AlertTriangle, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ChatMessageProps {
  id: string;
  sender: "patient" | "ai" | "nurse" | "doctor";
  content: string;
  timestamp: string;
  confidenceScore?: number;
  nurseAnnotation?: string;
  doctorAnnotation?: string;
  isNurseReviewed?: boolean;
  isDoctorReviewed?: boolean;
  escalatedToDoctor?: boolean;
  viewerRole?: "patient" | "nurse" | "doctor"; // Controls what information is visible
}

export default function ChatMessage({
  sender,
  content,
  timestamp,
  confidenceScore,
  nurseAnnotation,
  doctorAnnotation,
  isNurseReviewed = false,
  isDoctorReviewed = false,
  escalatedToDoctor = false,
  viewerRole = "patient",
}: ChatMessageProps) {
  const isPatient = sender === "patient";
  const isAI = sender === "ai";
  const isNurse = sender === "nurse";
  const isDoctor = sender === "doctor";
  const isMedicalStaff = isNurse || isDoctor;

  const getIcon = () => {
    if (isPatient) return <User className="h-4 w-4" />;
    if (isAI) return <Bot className="h-4 w-4" />;
    if (isNurse) return <Stethoscope className="h-4 w-4" />;
    if (isDoctor) return <Stethoscope className="h-4 w-4" />;
    return <User className="h-4 w-4" />;
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
          isNurse && "bg-chart-2 text-white",
          isDoctor && "bg-medical-blue text-medical-blue-foreground"
        )}>
          {getIcon()}
        </AvatarFallback>
      </Avatar>

      <div className={cn("flex-1 space-y-2", isPatient && "max-w-xs")}>
        <Card className={cn(
          "p-4",
          isPatient && "bg-primary text-primary-foreground",
          isAI && "bg-card border-chart-1/20",
          isNurse && "bg-chart-2/10 text-chart-2-foreground border-chart-2/20",
          isDoctor && "bg-medical-blue text-medical-blue-foreground"
        )}>
          <div className="space-y-2">
            <p className="text-sm leading-relaxed" data-testid="message-content">
              {content}
            </p>
            
            {/* AI Confidence Score - Only show to medical staff, never to patients */}
            {(viewerRole === "nurse" || viewerRole === "doctor") && isAI && confidenceScore !== undefined && (
              <div className="space-y-2 pt-2 border-t border-border/50">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Confidence Score</span>
                  <span className={getConfidenceColor(confidenceScore)}>
                    {confidenceScore >= 90 ? "Pass" : "Fail"}
                  </span>
                </div>
                <Progress value={confidenceScore} className="h-1" />
                <div className="flex gap-2 flex-wrap">
                  {getConfidenceBadge(confidenceScore)}
                  {isNurseReviewed && (
                    <Badge variant="outline" className="bg-chart-2/10 text-chart-2 border-chart-2/20">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Nurse Reviewed
                    </Badge>
                  )}
                  {isDoctorReviewed && (
                    <Badge variant="outline" className="bg-success/10 text-success border-success/20">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Doctor Reviewed
                    </Badge>
                  )}
                  {escalatedToDoctor && (
                    <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">
                      <AlertTriangle className="h-3 w-3 mr-1" />
                      Escalated to Doctor
                    </Badge>
                  )}
                </div>
              </div>
            )}

            {/* Medical Staff Annotations - Only show to medical staff, never to patients */}
            {(viewerRole === "nurse" || viewerRole === "doctor") && nurseAnnotation && (
              <Card className="p-3 bg-chart-2/10 border-chart-2/20">
                <div className="flex items-start gap-2">
                  <Stethoscope className="h-4 w-4 text-chart-2 flex-shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-chart-2">Nurse Note</p>
                    <p className="text-xs text-muted-foreground">{nurseAnnotation}</p>
                  </div>
                </div>
              </Card>
            )}
            {(viewerRole === "nurse" || viewerRole === "doctor") && doctorAnnotation && (
              <Card className="p-3 bg-medical-blue/10 border-medical-blue/20">
                <div className="flex items-start gap-2">
                  <Stethoscope className="h-4 w-4 text-medical-blue flex-shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-medical-blue">Doctor Note</p>
                    <p className="text-xs text-muted-foreground">{doctorAnnotation}</p>
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