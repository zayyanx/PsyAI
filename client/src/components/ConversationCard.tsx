import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { MessageSquare, Clock, AlertTriangle, CheckCircle, Eye } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ConversationCardProps {
  id: string;
  title: string;
  patientName: string;
  status: "active" | "pending_review" | "reviewed" | "closed";
  confidenceScore: number;
  needsExpertReview?: boolean; // Legacy field - kept for compatibility
  needsNurseReview?: boolean;
  needsDoctorReview?: boolean;
  escalatedToDoctor?: boolean;
  escalationReason?: string;
  lastMessage: string;
  timestamp: string;
  messageCount: number;
  onView?: () => void;
  onReview?: () => void;
  onEscalate?: () => void;
  viewerRole?: "nurse" | "doctor";
  className?: string;
}

export default function ConversationCard({
  id,
  title,
  patientName,
  status,
  confidenceScore,
  needsExpertReview = false,
  needsNurseReview = false,
  needsDoctorReview = false,
  escalatedToDoctor = false,
  escalationReason,
  lastMessage,
  timestamp,
  messageCount,
  onView,
  onReview,
  onEscalate,
  viewerRole = "nurse",
  className,
}: ConversationCardProps) {
  const getStatusBadge = () => {
    switch (status) {
      case "active":
        return (
          <Badge variant="outline" className="bg-chart-1/10 text-chart-1 border-chart-1/20">
            Active
          </Badge>
        );
      case "pending_review":
        return (
          <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">
            <AlertTriangle className="h-3 w-3 mr-1" />
            Pending Review
          </Badge>
        );
      case "reviewed":
        return (
          <Badge variant="outline" className="bg-success/10 text-success border-success/20">
            <CheckCircle className="h-3 w-3 mr-1" />
            Reviewed
          </Badge>
        );
      case "closed":
        return (
          <Badge variant="outline" className="bg-muted/50 text-muted-foreground border-muted">
            Closed
          </Badge>
        );
      default:
        return null;
    }
  };
  
  // Color-coded left border based on confidence score
  const getConfidenceBorderColor = () => {
    if (confidenceScore < 60) return "border-l-4 border-l-destructive";
    if (confidenceScore < 90) return "border-l-4 border-l-warning";
    return "";
  };

  return (
    <Card 
      className={cn(
        "hover-elevate transition-all duration-200",
        getConfidenceBorderColor(),
        className
      )}
      data-testid={`conversation-card-${id}`}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <Avatar className="h-10 w-10 flex-shrink-0">
              <AvatarFallback className="bg-primary text-primary-foreground">
                {patientName.split(' ').map(n => n[0]).join('').toUpperCase()}
              </AvatarFallback>
            </Avatar>
            
            <div className="flex-1 min-w-0 space-y-1">
              <h3 className="font-medium text-sm truncate" data-testid="conversation-title">
                {title}
              </h3>
              <p className="text-xs text-muted-foreground" data-testid="patient-name">
                {patientName}
              </p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <MessageSquare className="h-3 w-3" />
                <span data-testid="message-count">{messageCount} messages</span>
                <span>•</span>
                <Clock className="h-3 w-3" />
                <span data-testid="timestamp">{timestamp}</span>
              </div>
            </div>
          </div>
          
        </div>
      </CardHeader>
      
      <CardContent className="pt-0 space-y-4">
        {/* Confidence Score Button */}
        <Button
          variant="outline"
          size="sm"
          className={cn(
            "w-fit",
            confidenceScore >= 90 
              ? "bg-success/10 text-success border-success/20" 
              : "bg-destructive/10 text-destructive border-destructive/20"
          )}
          onClick={onView}
          data-testid="button-confidence"
        >
          <div className="flex items-center gap-2">
            {confidenceScore >= 90 ? (
              <CheckCircle className="h-4 w-4" />
            ) : (
              <AlertTriangle className="h-4 w-4" />
            )}
            <span className="font-semibold">
              {confidenceScore >= 90 ? "Pass" : "Fail"} ({confidenceScore}%)
            </span>
          </div>
        </Button>
        
        <div className="flex gap-2 pt-2">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onView}
            className="flex-1"
            data-testid="button-view-conversation"
          >
            <Eye className="h-4 w-4 mr-1" />
            View
          </Button>
          
          {(needsExpertReview || needsNurseReview || needsDoctorReview || status === "pending_review") && (
            <Button 
              size="sm" 
              onClick={onReview}
              className="flex-1"
              data-testid="button-review-conversation"
            >
              Review
            </Button>
          )}
          
          {viewerRole === "nurse" && onEscalate && (needsNurseReview || confidenceScore < 90) && (
            <Button 
              variant="outline"
              size="sm" 
              onClick={onEscalate}
              className="flex-1 text-warning hover:text-warning"
              data-testid="button-escalate-conversation"
            >
              <AlertTriangle className="h-4 w-4 mr-1" />
              Escalate
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}