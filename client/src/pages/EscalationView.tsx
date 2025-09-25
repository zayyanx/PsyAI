import { useState } from 'react';
import { useRoute } from 'wouter';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { ArrowLeft, ArrowUp, Send, User, Stethoscope, Clock, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import ChatMessage from '@/components/ChatMessage';

interface EscalationCase {
  id: string;
  conversationId: string;
  patientName: string;
  timestamp: string;
  confidenceScore: number;
  nurseReviewerName: string;
  nurseNotes: string;
  escalationReason: string;
  urgencyLevel: 'low' | 'medium' | 'high' | 'urgent';
  specialization?: string;
  messages: Array<{
    id: string;
    sender: 'patient' | 'ai' | 'nurse' | 'doctor';
    content: string;
    timestamp: string;
    confidenceScore?: number;
    flagged?: boolean;
  }>;
  nurseAssessment: {
    concernAreas: string[];
    recommendedActions: string[];
    timeframe: string;
  };
}

export default function EscalationView() {
  const [, params] = useRoute('/escalation/:id');
  const caseId = params?.id;
  
  const queryClient = useQueryClient();
  
  // All hooks must be called before any early returns
  const [doctorNotes, setDoctorNotes] = useState('');
  const [escalationDecision, setEscalationDecision] = useState<'accept' | 'request_more_info' | 'return_to_nurse'>('accept');
  const [assignedDoctor, setAssignedDoctor] = useState('');
  const [priorityLevel, setPriorityLevel] = useState('medium');
  
  // Fetch escalation case data from API
  const { data: caseData, isLoading, error } = useQuery({
    queryKey: ['/api/messages', caseId, 'detail'],
    enabled: !!caseId,
  });

  // Mutation for processing escalation
  const processEscalationMutation = useMutation({
    mutationFn: async () => {
      return apiRequest('POST', '/api/medical-reviews', {
        conversationId: caseId,
        reviewerId: 'doctor-1', // In real app, get from auth context
        reviewerRole: 'doctor',
        status: escalationDecision === 'accept' ? 'completed' : 'pending',
        feedback: doctorNotes
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/messages', caseId, 'detail'] });
      queryClient.invalidateQueries({ queryKey: ['/api/conversations'] });
      alert(`Escalation ${escalationDecision === 'accept' ? 'accepted' : escalationDecision.replace('_', ' ')}`);
    }
  });

  if (isLoading) {
    return <div className="container mx-auto py-6" data-testid="escalation-loading">Loading...</div>;
  }

  if (error || !caseData) {
    return <div className="container mx-auto py-6" data-testid="escalation-error">Error loading escalation data</div>;
  }

  const conversation = (caseData as any)?.conversation;
  const messages = (caseData as any)?.messages || [];
  const patient = (caseData as any)?.patient;
  const escalationCase = {
    id: caseId || '1',
    conversationId: conversation?.id,
    patientName: patient?.name || 'Unknown',
    timestamp: conversation?.createdAt,
    confidenceScore: conversation?.confidenceScore || 0,
    nurseReviewerName: 'Nurse Jennifer Adams',
    nurseNotes: 'Case escalated for clinical assessment based on low AI confidence and complexity.',
    escalationReason: conversation?.escalationReason || 'Requires professional medical evaluation',
    urgencyLevel: (conversation?.confidenceScore || 100) < 50 ? 'high' as const : 'medium' as const,
    specialization: 'psychiatry',
    messages: messages.map((msg: any) => ({
      ...msg,
      flagged: msg.sender === 'ai' && (msg.confidenceScore || 100) < 90
    })),
    nurseAssessment: {
      concernAreas: ['AI confidence low', 'Requires clinical assessment'],
      recommendedActions: ['Doctor review', 'Clinical evaluation'],
      timeframe: 'Within 48 hours'
    }
  };

  // Update priority level after escalation case is computed
  if (priorityLevel === 'medium' && escalationCase.urgencyLevel !== 'medium') {
    setPriorityLevel(escalationCase.urgencyLevel);
  }

  const handleProcessEscalation = () => {
    processEscalationMutation.mutate();
  };

  const getUrgencyBadge = (level: string) => {
    switch (level) {
      case 'urgent':
        return <Badge variant="destructive" className="animate-pulse">Urgent</Badge>;
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
    <div className="container mx-auto py-6" data-testid="escalation-view">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="sm" onClick={() => window.history.back()} data-testid="button-back">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2" data-testid="page-title">
            <ArrowUp className="h-6 w-6 text-warning" />
            Case Escalation
          </h1>
          <p className="text-muted-foreground">Case ID: {escalationCase.id} • Escalated by {escalationCase.nurseReviewerName}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Escalation Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Escalation Summary */}
          <Card className="border-warning/20">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-warning" />
                  Escalation Summary
                </span>
                <div className="flex items-center gap-2">
                  {getUrgencyBadge(escalationCase.urgencyLevel)}
                  {getConfidenceBadge(escalationCase.confidenceScore)}
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="font-medium text-muted-foreground">Patient</p>
                  <p data-testid="patient-name">{escalationCase.patientName}</p>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">Session Time</p>
                  <p>{escalationCase.timestamp}</p>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">Reviewed By</p>
                  <p>{escalationCase.nurseReviewerName}</p>
                </div>
                <div>
                  <p className="font-medium text-muted-foreground">Specialization</p>
                  <p className="capitalize">{escalationCase.specialization || 'General'}</p>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Escalation Reason</p>
                <p className="text-sm bg-warning/10 text-warning p-3 rounded border border-warning/20">
                  {escalationCase.escalationReason}
                </p>
              </div>
              
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Nurse Clinical Notes</p>
                <p className="text-sm bg-muted p-3 rounded border">
                  {escalationCase.nurseNotes}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Flagged Messages */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                Flagged Messages
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]" data-testid="flagged-messages-scroll">
                <div className="space-y-4">
                  {escalationCase.messages
                    .filter(message => message.flagged)
                    .map((message) => (
                    <div key={message.id} className="ring-2 ring-warning/20 rounded-lg p-2">
                      <ChatMessage
                        id={message.id}
                        sender={message.sender}
                        content={message.content}
                        timestamp={message.timestamp}
                        confidenceScore={message.confidenceScore}
                        viewerRole="doctor"
                      />
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Nurse Assessment */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Stethoscope className="h-5 w-5" />
                Nurse Assessment
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Areas of Concern</p>
                <div className="flex flex-wrap gap-2">
                  {escalationCase.nurseAssessment.concernAreas.map((area, index) => (
                    <Badge key={index} variant="outline" className="bg-chart-2/10 text-chart-2 border-chart-2/20">
                      {area}
                    </Badge>
                  ))}
                </div>
              </div>
              
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-2">Recommended Actions</p>
                <ul className="text-sm space-y-1">
                  {escalationCase.nurseAssessment.recommendedActions.map((action, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-chart-2 rounded-full" />
                      {action}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">Recommended Timeframe</p>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-warning" />
                  <span className="text-sm font-medium text-warning">{escalationCase.nurseAssessment.timeframe}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Doctor Response Sidebar */}
        <div className="space-y-6">
          {/* Escalation Decision */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Doctor Response
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="escalation-decision" className="text-sm font-medium">
                  Decision
                </Label>
                <Select value={escalationDecision} onValueChange={(value: 'accept' | 'request_more_info' | 'return_to_nurse') => setEscalationDecision(value)}>
                  <SelectTrigger data-testid="select-escalation-decision">
                    <SelectValue placeholder="Select decision" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="accept">Accept & Review Case</SelectItem>
                    <SelectItem value="request_more_info">Request More Information</SelectItem>
                    <SelectItem value="return_to_nurse">Return to Nurse</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="assigned-doctor" className="text-sm font-medium">
                  Assign to Doctor
                </Label>
                <Select value={assignedDoctor} onValueChange={setAssignedDoctor}>
                  <SelectTrigger data-testid="select-assigned-doctor">
                    <SelectValue placeholder="Select doctor" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="dr-wilson">Dr. Sarah Wilson (Psychiatry)</SelectItem>
                    <SelectItem value="dr-chen">Dr. Michael Chen (Psychology)</SelectItem>
                    <SelectItem value="dr-patel">Dr. Priya Patel (General Practice)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="priority-level" className="text-sm font-medium">
                  Priority Level
                </Label>
                <Select value={priorityLevel} onValueChange={(value: 'low' | 'medium' | 'high' | 'urgent') => setPriorityLevel(value)}>
                  <SelectTrigger data-testid="select-priority-level">
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="urgent">Urgent (Same Day)</SelectItem>
                    <SelectItem value="high">High (Within 24h)</SelectItem>
                    <SelectItem value="medium">Medium (Within 48h)</SelectItem>
                    <SelectItem value="low">Low (Within 1 week)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Doctor Notes */}
          <Card>
            <CardHeader>
              <CardTitle>Clinical Assessment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="doctor-notes" className="text-sm font-medium">
                  Doctor Notes
                </Label>
                <Textarea
                  id="doctor-notes"
                  placeholder="Add your clinical assessment and next steps..."
                  value={doctorNotes}
                  onChange={(e) => setDoctorNotes(e.target.value)}
                  className="min-h-[120px]"
                  data-testid="textarea-doctor-notes"
                />
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button 
                variant="outline" 
                className="w-full justify-start" 
                size="sm"
                data-testid="button-view-history"
              >
                <User className="h-4 w-4 mr-2" />
                View Patient History
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-start" 
                size="sm"
                data-testid="button-schedule-appointment"
              >
                <Clock className="h-4 w-4 mr-2" />
                Schedule Appointment
              </Button>
            </CardContent>
          </Card>

          {/* Process Escalation */}
          <div className="space-y-2">
            <Button 
              onClick={handleProcessEscalation}
              className="w-full"
              data-testid="button-process-escalation"
            >
              <Send className="h-4 w-4 mr-2" />
              Process Escalation
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