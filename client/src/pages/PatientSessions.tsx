import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MessageSquare, Clock, Calendar, TrendingUp } from 'lucide-react';
import { useLocation } from 'wouter';

export default function PatientSessions() {
  const [, navigate] = useLocation();

  // Mock session data 
  const sessions = [
    {
      id: '1',
      title: 'Anxiety Management Session',
      date: 'Today, 2:30 PM',
      duration: '45 minutes',
      status: 'active',
      messages: 18,
      aiConfidence: 85,
      expertReviewed: true,
    },
    {
      id: '2', 
      title: 'Sleep Pattern Discussion',
      date: 'Yesterday, 10:00 AM',
      duration: '32 minutes',
      status: 'completed',
      messages: 24,
      aiConfidence: 92,
      expertReviewed: true,
    },
    {
      id: '3',
      title: 'Work Stress Consultation',
      date: '3 days ago, 4:15 PM',
      duration: '28 minutes',
      status: 'completed',
      messages: 15,
      aiConfidence: 76,
      expertReviewed: false,
    },
  ];

  const handleStartNewSession = () => {
    navigate('/chat');
  };

  const handleContinueSession = (sessionId: string) => {
    console.log('Continuing session:', sessionId);
    navigate('/chat');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">My Sessions</h1>
          <p className="text-muted-foreground">
            Track your mental health journey and access your conversation history
          </p>
        </div>
        <Button onClick={handleStartNewSession} data-testid="button-new-session">
          <MessageSquare className="h-4 w-4 mr-2" />
          Start New Session
        </Button>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-chart-1/10 rounded-lg">
                <MessageSquare className="h-5 w-5 text-chart-1" />
              </div>
              <div>
                <p className="text-2xl font-bold">3</p>
                <p className="text-xs text-muted-foreground">Total Sessions</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-success/10 rounded-lg">
                <Clock className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-2xl font-bold">105</p>
                <p className="text-xs text-muted-foreground">Minutes Total</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-warning/10 rounded-lg">
                <TrendingUp className="h-5 w-5 text-warning" />
              </div>
              <div>
                <p className="text-2xl font-bold">84%</p>
                <p className="text-xs text-muted-foreground">Avg AI Confidence</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Session History */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Session History</h2>
        
        {sessions.map((session) => (
          <Card key={session.id} className="hover-elevate">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-base">{session.title}</CardTitle>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      <span>{session.date}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{session.duration}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <MessageSquare className="h-3 w-3" />
                      <span>{session.messages} messages</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Badge 
                    variant="outline" 
                    className={session.status === 'active' 
                      ? 'bg-chart-1/10 text-chart-1 border-chart-1/20' 
                      : 'bg-muted/50 text-muted-foreground'
                    }
                  >
                    {session.status === 'active' ? 'Active' : 'Completed'}
                  </Badge>
                  
                  {session.expertReviewed && (
                    <Badge variant="outline" className="bg-success/10 text-success border-success/20">
                      Expert Reviewed
                    </Badge>
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="pt-0">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">
                    AI Confidence: <span className="font-medium">{session.aiConfidence}%</span>
                  </p>
                </div>
                
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    data-testid={`button-view-session-${session.id}`}
                  >
                    View Details
                  </Button>
                  
                  {session.status === 'active' && (
                    <Button 
                      size="sm" 
                      onClick={() => handleContinueSession(session.id)}
                      data-testid={`button-continue-session-${session.id}`}
                    >
                      Continue
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}