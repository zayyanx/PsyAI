import ExpertDashboard from '../ExpertDashboard';
import { type ConversationCardProps } from '../ConversationCard';

export default function ExpertDashboardExample() {
  // Mock conversation data
  const mockConversations: ConversationCardProps[] = [
    {
      id: '1',
      title: 'Anxiety and Panic Attacks',
      patientName: 'Sarah Johnson',
      status: 'pending_review',
      confidenceScore: 45,
      needsExpertReview: true,
      lastMessage: 'I\'m having trouble breathing during these episodes. The AI suggested some techniques but I\'m not sure if they\'re right for me.',
      timestamp: '2 hours ago',
      messageCount: 8,
    },
    {
      id: '2',
      title: 'Depression Medication Consultation',
      patientName: 'Michael Chen',
      status: 'pending_review',
      confidenceScore: 35,
      needsExpertReview: true,
      lastMessage: 'Should I increase my dosage? I\'ve been on 20mg for 6 weeks now but still feel the same.',
      timestamp: '4 hours ago',
      messageCount: 12,
    },
    {
      id: '3',
      title: 'Work-Life Balance Therapy',
      patientName: 'Emily Rodriguez',
      status: 'active',
      confidenceScore: 87,
      needsExpertReview: false,
      lastMessage: 'The mindfulness exercises have been helping. I\'ve been doing them every morning before work.',
      timestamp: '1 day ago',
      messageCount: 15,
    },
    {
      id: '4',
      title: 'Sleep Disorder Assessment',
      patientName: 'David Kim',
      status: 'reviewed',
      confidenceScore: 92,
      needsExpertReview: false,
      lastMessage: 'Thank you for the sleep hygiene recommendations. I\'ve been sleeping much better.',
      timestamp: '2 days ago',
      messageCount: 18,
    },
    {
      id: '5',
      title: 'Relationship Counseling',
      patientName: 'Lisa Thompson',
      status: 'active',
      confidenceScore: 78,
      needsExpertReview: false,
      lastMessage: 'The communication strategies we discussed are working well with my partner.',
      timestamp: '3 hours ago',
      messageCount: 25,
    },
    {
      id: '6',
      title: 'PTSD Support Session',
      patientName: 'James Wilson',
      status: 'pending_review',
      confidenceScore: 52,
      needsExpertReview: true,
      lastMessage: 'The flashbacks are getting worse. I need professional help beyond what the AI can provide.',
      timestamp: '1 hour ago',
      messageCount: 6,
    },
  ];

  const handleViewConversation = (id: string) => {
    console.log('Viewing conversation:', id);
  };

  const handleReviewConversation = (id: string) => {
    console.log('Reviewing conversation:', id);
  };

  return (
    <div className="p-6 min-h-screen bg-background">
      <ExpertDashboard
        expertName="Dr. Sarah Wilson"
        conversations={mockConversations}
        onViewConversation={handleViewConversation}
        onReviewConversation={handleReviewConversation}
      />
    </div>
  );
}