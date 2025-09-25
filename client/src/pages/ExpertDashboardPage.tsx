import MedicalDashboard from '@/components/ExpertDashboard';
import { type ConversationCardProps } from '@/components/ConversationCard';
import { useState } from 'react';
import { useLocation } from 'wouter';

export default function ExpertDashboardPage() {
  // In a real app, this would come from auth context or props
  const [userRole] = useState<"nurse" | "doctor">("nurse"); // Default to nurse for demo
  const [conversations] = useState<ConversationCardProps[]>([
    {
      id: 'conv-1',
      title: 'Work-related anxiety support',
      patientName: 'Sarah Johnson',
      status: 'pending_review',
      confidenceScore: 73,
      needsNurseReview: true,
      escalatedToDoctor: false,
      lastMessage: 'I\'ve been feeling really anxious lately, especially about work deadlines. It\'s starting to affect my sleep and I find myself worrying constantly.',
      timestamp: '30 minutes ago',
      messageCount: 2,
    },
    {
      id: 'conv-2',
      title: 'Panic attack management',
      patientName: 'Sarah Johnson',
      status: 'reviewed',
      confidenceScore: 28,
      needsDoctorReview: true,
      escalatedToDoctor: true,
      escalationReason: 'Complex anxiety presentation requires clinical evaluation for potential therapy referral',
      lastMessage: 'I\'ve been having panic attacks at work, especially when deadlines approach. Yesterday I had to leave a meeting because I couldn\'t breathe properly.',
      timestamp: '1 hour ago',
      messageCount: 2,
    }
  ]);

  const [, setLocation] = useLocation();

  const handleViewConversation = (id: string) => {
    console.log('Opening conversation view for ID:', id);
    setLocation(`/view/${id}`);
  };

  const handleReviewConversation = (id: string) => {
    console.log('Starting medical review for ID:', id);
    setLocation(`/review/${id}`);
  };

  const handleEscalateToDoctor = (id: string) => {
    console.log('Escalating to doctor for ID:', id);
    setLocation(`/escalation/${id}`);
  };

  return (
    <MedicalDashboard
      userRole={userRole}
      userName={userRole === "doctor" ? "Dr. Sarah Wilson" : "Nurse Jennifer Adams"}
      conversations={conversations}
      onViewConversation={handleViewConversation}
      onReviewConversation={handleReviewConversation}
      onEscalateToDoctor={handleEscalateToDoctor}
    />
  );
}