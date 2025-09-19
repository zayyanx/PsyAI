import ExpertDashboard from '@/components/ExpertDashboard';
import { type ConversationCardProps } from '@/components/ConversationCard';
import { useState } from 'react';

export default function ExpertDashboardPage() {
  const [conversations] = useState<ConversationCardProps[]>([
    {
      id: '1',
      title: 'Severe Anxiety and Panic Disorder',
      patientName: 'Sarah Johnson',
      status: 'pending_review',
      confidenceScore: 42,
      needsExpertReview: true,
      lastMessage: 'I\'m having panic attacks multiple times a day now. The breathing exercises aren\'t helping anymore. I feel like I\'m losing control.',
      timestamp: '30 minutes ago',
      messageCount: 15,
    },
    {
      id: '2',
      title: 'Medication Dosage Consultation',
      patientName: 'Michael Chen',
      status: 'pending_review',
      confidenceScore: 38,
      needsExpertReview: true,
      lastMessage: 'I\'ve been on sertraline 50mg for 8 weeks. Should I increase to 100mg? I still feel depressed and the side effects are manageable.',
      timestamp: '1 hour ago',
      messageCount: 22,
    },
    {
      id: '3',
      title: 'PTSD Therapy Support',
      patientName: 'James Wilson',
      status: 'pending_review',
      confidenceScore: 55,
      needsExpertReview: true,
      lastMessage: 'The nightmares are getting worse. I think I need specialized PTSD treatment beyond what we\'ve discussed.',
      timestamp: '2 hours ago',
      messageCount: 8,
    },
    {
      id: '4',
      title: 'Workplace Stress Management',
      patientName: 'Emily Rodriguez',
      status: 'active',
      confidenceScore: 87,
      needsExpertReview: false,
      lastMessage: 'The mindfulness techniques are really helping with my work stress. I\'ve been practicing them daily.',
      timestamp: '3 hours ago',
      messageCount: 18,
    },
    {
      id: '5',
      title: 'Sleep Hygiene Improvement',
      patientName: 'David Kim',
      status: 'reviewed',
      confidenceScore: 91,
      needsExpertReview: false,
      lastMessage: 'My sleep has improved dramatically with the routine we established. Thank you for the guidance.',
      timestamp: '1 day ago',
      messageCount: 25,
    },
    {
      id: '6',
      title: 'Relationship Communication Issues',
      patientName: 'Lisa Thompson',
      status: 'active',
      confidenceScore: 76,
      needsExpertReview: false,
      lastMessage: 'The communication strategies we discussed are working well. My partner and I are having better conversations.',
      timestamp: '4 hours ago',
      messageCount: 32,
    },
    {
      id: '7',
      title: 'Bipolar Mood Tracking',
      patientName: 'Robert Martinez',
      status: 'pending_review',
      confidenceScore: 61,
      needsExpertReview: true,
      lastMessage: 'I think I\'m entering a manic phase. My mood tracking shows significant changes over the past week.',
      timestamp: '45 minutes ago',
      messageCount: 12,
    },
    {
      id: '8',
      title: 'Generalized Anxiety Treatment',
      patientName: 'Amanda Foster',
      status: 'reviewed',
      confidenceScore: 89,
      needsExpertReview: false,
      lastMessage: 'The CBT exercises have been incredibly helpful. I feel more in control of my anxiety now.',
      timestamp: '2 days ago',
      messageCount: 45,
    },
    {
      id: '9',
      title: 'Eating Disorder Recovery',
      patientName: 'Jessica Park',
      status: 'pending_review',
      confidenceScore: 28,
      needsExpertReview: true,
      lastMessage: 'I had a relapse yesterday. I\'m scared and need professional guidance immediately.',
      timestamp: '15 minutes ago',
      messageCount: 5,
    },
    {
      id: '10',
      title: 'Social Anxiety Success',
      patientName: 'Alex Thompson',
      status: 'active',
      confidenceScore: 94,
      needsExpertReview: false,
      lastMessage: 'I successfully attended my first social event in months! The exposure therapy techniques worked.',
      timestamp: '6 hours ago',
      messageCount: 28,
    },
    {
      id: '11',
      title: 'Substance Abuse Crisis',
      patientName: 'Mark Davis',
      status: 'pending_review',
      confidenceScore: 15,
      needsExpertReview: true,
      lastMessage: 'I relapsed last night. I need immediate help and possibly inpatient treatment.',
      timestamp: '5 minutes ago',
      messageCount: 3,
    },
    {
      id: '12',
      title: 'Teen Depression Support',
      patientName: 'Jordan Smith',
      status: 'pending_review',
      confidenceScore: 47,
      needsExpertReview: true,
      lastMessage: 'I\'m 16 and have been feeling really dark thoughts. My parents don\'t understand.',
      timestamp: '45 minutes ago',
      messageCount: 7,
    },
    {
      id: '13',
      title: 'General Wellness Check',
      patientName: 'Taylor Brown',
      status: 'reviewed',
      confidenceScore: 96,
      needsExpertReview: false,
      lastMessage: 'Everything is going well with my mental health routine. Just wanted to check in.',
      timestamp: '3 days ago',
      messageCount: 12,
    },
    {
      id: '14',
      title: 'Medication Side Effects',
      patientName: 'Chris Johnson',
      status: 'pending_review',
      confidenceScore: 33,
      needsExpertReview: true,
      lastMessage: 'The new antidepressant is causing severe nausea and dizziness. Should I stop taking it?',
      timestamp: '20 minutes ago',
      messageCount: 4,
    },
    {
      id: '15',
      title: 'Grief Counseling Progress',
      patientName: 'Maria Garcia',
      status: 'active',
      confidenceScore: 73,
      needsExpertReview: false,
      lastMessage: 'The grief support resources have been helpful. I\'m slowly learning to cope with the loss.',
      timestamp: '8 hours ago',
      messageCount: 19,
    },
  ]);

  const handleViewConversation = (id: string) => {
    console.log('Opening conversation view for ID:', id);
    // In a real app, this would navigate to a detailed conversation view
    alert(`Opening detailed view for conversation ${id}`);
  };

  const handleReviewConversation = (id: string) => {
    console.log('Starting expert review for ID:', id);
    // In a real app, this would open the expert review interface
    alert(`Starting expert review process for conversation ${id}`);
  };

  return (
    <ExpertDashboard
      expertName="Dr. Sarah Wilson"
      conversations={conversations}
      onViewConversation={handleViewConversation}
      onReviewConversation={handleReviewConversation}
    />
  );
}