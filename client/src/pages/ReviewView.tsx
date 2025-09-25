import { useState } from 'react';
import { useRoute } from 'wouter';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { ArrowLeft, Save, AlertTriangle, CheckCircle, MessageSquare, Brain, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import ChatMessage from '@/components/ChatMessage';

interface ReviewCase {
  id: string;
  conversationId: string;
  patientName: string;
  timestamp: string;
  confidenceScore: number;
  status: 'pending_review' | 'in_review' | 'completed';
  reviewType: 'nurse' | 'doctor';
  escalationReason?: string;
  priority: 'low' | 'medium' | 'high';
  messages: Array<{
    id: string;
    sender: 'patient' | 'ai' | 'nurse' | 'doctor';
    content: string;
    timestamp: string;
    confidenceScore?: number;
    flagged?: boolean;
  }>;
}

export default function ReviewView() {
  const [, params] = useRoute('/review/:id');
  const caseId = params?.id;
  
  const queryClient = useQueryClient();
  
  // All hooks must be called before any early returns
  const [reviewDecision, setReviewDecision] = useState<'approve' | 'modify' | 'escalate'>('approve');
  const [reviewNotes, setReviewNotes] = useState('');
  const [actionItems, setActionItems] = useState<string[]>([]);
  const [needsFollowUp, setNeedsFollowUp] = useState(false);
  const [escalationReason, setEscalationReason] = useState('');
  
  // Fetch case data from API
  const { data: caseData, isLoading, error } = useQuery({
    queryKey: ['/api/messages', caseId, 'detail'],
    enabled: !!caseId,
  });

  // Mutation for saving review
  const saveReviewMutation = useMutation({
    mutationFn: async () => {
      return apiRequest('POST', '/api/medical-reviews', {
        conversationId: caseId,
        reviewerId: 'nurse-1', // In real app, get from auth context
        reviewerRole: 'nurse',
        status: reviewDecision === 'escalate' ? 'escalated_to_doctor' : reviewDecision === 'approve' ? 'approved' : 'modified',
        feedback: reviewNotes,
        escalationReason: reviewDecision === 'escalate' ? escalationReason : undefined
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/messages', caseId, 'detail'] });
      queryClient.invalidateQueries({ queryKey: ['/api/conversations'] });
      alert('Review saved successfully');
    }
  });

  if (isLoading) {
    return <div className="container mx-auto py-6" data-testid="review-loading">Loading...</div>;
  }

  if (error || !caseData) {
    return <div className="container mx-auto py-6" data-testid="review-error">Error loading case data</div>;
  }

  const conversation = (caseData as any)?.conversation;
  const messages = (caseData as any)?.messages || [];
  const patient = (caseData as any)?.patient;
  const reviewCase = {
    id: caseId || '1',
    conversationId: conversation?.id,
    patientName: patient?.name || 'Unknown',
    timestamp: conversation?.createdAt,
    confidenceScore: conversation?.confidenceScore || 0,
    status: conversation?.status,
    reviewType: 'nurse' as const,
    priority: (conversation?.confidenceScore || 100) < 50 ? 'high' as const : 'medium' as const,
    messages: messages.filter((msg: any) => msg.sender === 'ai' && (msg.confidenceScore || 100) < 90).map((msg: any) => ({
      ...msg,
      flagged: (msg.confidenceScore || 100) < 90
    })),
    escalationReason: conversation?.escalationReason || undefined
  };

  const handleSaveReview = () => {
    saveReviewMutation.mutate();
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high':
        return <Badge variant="destructive">High Priority</Badge>;
      case 'medium':
        return <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">Medium Priority</Badge>;
      default:
        return <Badge variant="secondary">Low Priority</Badge>;
    }
  };

  const getConfidenceBadge = (score: number) => {
    if (score >= 90) return <Badge variant="outline" className="bg-success/10 text-success border-success/20">High Confidence</Badge>;
    if (score >= 70) return <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">Medium Confidence</Badge>;
    return <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/20">Low Confidence</Badge>;
  };

  return (
    <div className="container mx-auto py-6" data-testid="review-view">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="sm" onClick={() => window.history.back()} data-testid="button-back">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        <div>
          <h1 className="text-2xl font-bold" data-testid="page-title">
            {reviewCase.reviewType === 'nurse' ? 'Nurse Review' : 'Doctor Review'}
          </h1>
          <p className="text-muted-foreground">Case ID: {reviewCase.id}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Review Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Case Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Case Overview</span>
                <div className="flex items-center gap-2">
                  {getPriorityBadge(reviewCase.priority)}
                  {getConfidenceBadge(reviewCase.confidenceScore)}
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-muted-foreground">Patient</p>
                  <p data-testid="patient-name">{reviewCase.patientName}</p>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">Session Time</p>
                  <p>{reviewCase.timestamp}</p>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">AI Confidence</p>
                  <p>{reviewCase.confidenceScore}%</p>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">Review Type</p>
                  <p className="capitalize">{reviewCase.reviewType}</p>
                </div>
              </div>
              
              {reviewCase.escalationReason && (
                <>
                  <Separator />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-1">Escalation Reason</p>
                    <p className="text-sm bg-warning/10 text-warning p-2 rounded border border-warning/20">
                      {reviewCase.escalationReason}
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Messages to Review */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Messages Requiring Review
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]" data-testid="review-messages-scroll">
                <div className="space-y-4">
                  {reviewCase.messages.map((message) => (
                    <div key={message.id} className="space-y-2">
                      <div className={`${message.flagged ? 'ring-2 ring-warning/20 rounded-lg p-2' : ''}`}>
                        <ChatMessage
                          id={message.id}
                          sender={message.sender}
                          content={message.content}
                          timestamp={message.timestamp}
                          confidenceScore={message.confidenceScore}
                          viewerRole={reviewCase.reviewType}
                        />
                        {message.flagged && (
                          <div className="flex items-center gap-2 mt-2 text-warning">
                            <AlertTriangle className="h-4 w-4" />
                            <span className="text-sm font-medium">Flagged for Review</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Review Form Sidebar */}
        <div className="space-y-6">
          {/* Review Decision */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Review Decision
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <RadioGroup value={reviewDecision} onValueChange={(value: 'approve' | 'modify' | 'escalate') => setReviewDecision(value)}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="approve" id="approve" data-testid="radio-approve" />
                  <Label htmlFor="approve" className="text-sm">
                    Approve AI Response
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="modify" id="modify" data-testid="radio-modify" />
                  <Label htmlFor="modify" className="text-sm">
                    Request Modification
                  </Label>
                </div>
                {reviewCase.reviewType === 'nurse' && (
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="escalate" id="escalate" data-testid="radio-escalate" />
                    <Label htmlFor="escalate" className="text-sm">
                      Escalate to Doctor
                    </Label>
                  </div>
                )}
              </RadioGroup>

              {reviewDecision === 'escalate' && (
                <div className="space-y-2">
                  <Label htmlFor="escalation-reason" className="text-sm">
                    Escalation Reason
                  </Label>
                  <Textarea
                    id="escalation-reason"
                    placeholder="Explain why this case needs doctor review..."
                    value={escalationReason}
                    onChange={(e) => setEscalationReason(e.target.value)}
                    data-testid="textarea-escalation-reason"
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Review Notes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Clinical Notes
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="review-notes" className="text-sm">
                  Professional Assessment
                </Label>
                <Textarea
                  id="review-notes"
                  placeholder="Add your clinical notes and assessment..."
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  className="min-h-[120px]"
                  data-testid="textarea-review-notes"
                />
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="follow-up"
                  checked={needsFollowUp}
                  onCheckedChange={(checked) => setNeedsFollowUp(checked as boolean)}
                  data-testid="checkbox-follow-up"
                />
                <Label htmlFor="follow-up" className="text-sm">
                  Schedule follow-up session
                </Label>
              </div>
            </CardContent>
          </Card>

          {/* Action Items */}
          <Card>
            <CardHeader>
              <CardTitle>Action Items</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span>Patient notification</span>
                  <Badge variant="outline" className="bg-success/10 text-success border-success/20">Auto</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Update patient record</span>
                  <Badge variant="outline" className="bg-success/10 text-success border-success/20">Auto</Badge>
                </div>
                {needsFollowUp && (
                  <div className="flex items-center justify-between">
                    <span>Schedule follow-up</span>
                    <Badge variant="outline" className="bg-chart-2/10 text-chart-2 border-chart-2/20">Manual</Badge>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Save Actions */}
          <div className="space-y-2">
            <Button 
              onClick={handleSaveReview}
              className="w-full"
              data-testid="button-save-review"
            >
              <Save className="h-4 w-4 mr-2" />
              Complete Review
            </Button>
            <Button 
              variant="outline"
              className="w-full"
              data-testid="button-save-draft"
            >
              Save Draft
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}