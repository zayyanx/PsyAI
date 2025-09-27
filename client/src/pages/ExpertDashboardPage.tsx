import MedicalDashboard from '@/components/ExpertDashboard';
import { type ConversationCardProps } from '@/components/ConversationCard';
import { useState } from 'react';
import { useLocation } from 'wouter';
import { useQuery } from '@tanstack/react-query';

export default function ExpertDashboardPage() {
  // In a real app, this would come from auth context or props
  const [userRole] = useState<"nurse" | "doctor">("nurse"); // Default to nurse for demo
  const [location] = useLocation();
  // Helper function to format timestamps
  const formatTimestamp = (updatedAt: string) => {
    const diff = Date.now() - new Date(updatedAt).getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    if (hours <= 1) return '1 hour ago';
    if (hours <= 24) return `${hours} hours ago`;
    return '1 day ago';
  };

  // Fetch conversations from API instead of using hardcoded data
  const { data: apiConversations = [], isLoading } = useQuery({
    queryKey: ['/api/conversations'],
  });

  // Transform API conversations to match ConversationCardProps format
  const conversations: ConversationCardProps[] = apiConversations.map((conv: any) => ({
    id: conv.id,
    title: conv.title,
    patientName: conv.patientId === 'patient-1' ? 'Sarah Johnson' : 'Unknown Patient',
    status: conv.status,
    confidenceScore: conv.confidenceScore,
    needsNurseReview: conv.needsNurseReview,
    needsDoctorReview: conv.needsDoctorReview,
    escalatedToDoctor: conv.escalatedToDoctor,
    escalationReason: conv.escalationReason,
    lastMessage: conv.title, // Using title as placeholder for last message
    timestamp: formatTimestamp(conv.updatedAt),
    messageCount: 2, // Placeholder message count
  }));

  const [, setLocation] = useLocation();

  const handleViewConversation = (id: string) => {
    console.log('Opening conversation view for ID:', id);
    setLocation(`/messages/${id}`);
  };

  const handleReviewConversation = (id: string) => {
    console.log('Starting medical review for ID:', id);
    setLocation(`/review/${id}`);
  };

  const handleEscalateToDoctor = (id: string) => {
    console.log('Escalating to doctor for ID:', id);
    setLocation(`/escalation/${id}`);
  };

  // Filter conversations based on current route
  const getFilteredConversations = () => {
    switch (location) {
      case '/cases':
        // Show only cases that need medical attention
        return conversations.filter(conv => 
          conv.status === 'pending_review' || 
          conv.needsNurseReview || 
          conv.needsDoctorReview ||
          conv.escalatedToDoctor
        );
      case '/conversations':
        // Show all conversations, especially active ones
        return conversations.sort((a, b) => {
          // Prioritize active conversations
          if (a.status === 'active' && b.status !== 'active') return -1;
          if (b.status === 'active' && a.status !== 'active') return 1;
          return b.messageCount - a.messageCount; // Then by message count
        });
      default:
        // Dashboard shows everything
        return conversations;
    }
  };

  const getPageTitle = () => {
    switch (location) {
      case '/cases':
        return 'Patient Cases';
      case '/conversations':
        return 'AI Conversations';
      default:
        return userRole === "doctor" ? 'Doctor Dashboard' : 'Nurse Dashboard';
    }
  };

  const getPageSubtitle = () => {
    switch (location) {
      case '/cases':
        return 'Review patient cases requiring medical attention';
      case '/conversations':
        return 'Monitor and manage AI-assisted conversations';
      default:
        return `Welcome back, ${userRole === "doctor" ? "Dr. Sarah Wilson" : "Nurse Jennifer Adams"}`;
    }
  };

  return (
    <MedicalDashboard
      userRole={userRole}
      userName={userRole === "doctor" ? "Dr. Sarah Wilson" : "Nurse Jennifer Adams"}
      conversations={getFilteredConversations()}
      onViewConversation={handleViewConversation}
      onReviewConversation={handleReviewConversation}
      onEscalateToDoctor={handleEscalateToDoctor}
      pageTitle={getPageTitle()}
      pageSubtitle={getPageSubtitle()}
    />
  );
}