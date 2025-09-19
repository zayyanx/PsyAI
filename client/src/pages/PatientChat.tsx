import { useState } from 'react';
import PatientChatInterface from '@/components/PatientChatInterface';
import { type ChatMessageProps } from '@/components/ChatMessage';

export default function PatientChat() {
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<ChatMessageProps[]>([
    {
      id: '1',
      sender: 'ai',
      content: 'Hello! I\'m your AI mental health assistant. I\'m here to provide personalized support and guidance, with expert oversight to ensure you receive the best care possible. How are you feeling today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  // Mock AI responses for demo
  const aiResponses = [
    {
      content: 'Thank you for sharing that with me. It\'s completely normal to feel this way, and I\'m here to help. Can you tell me more about what specific situations trigger these feelings?',
      confidence: 85,
    },
    {
      content: 'I understand how challenging that must be. Let\'s work together on some coping strategies. First, let\'s try a simple breathing exercise that you can use whenever you feel overwhelmed.',
      confidence: 94,
    },
    {
      content: 'I\'m here to support you through this difficult time. Remember that seeking help is a sign of strength, not weakness. Would you like me to provide some immediate coping strategies while we work on a longer-term plan?',
      confidence: 91,
    },
    {
      content: 'These feelings are completely valid. Let\'s focus on some grounding techniques that can help you feel more centered when you\'re overwhelmed.',
      confidence: 93,
    },
  ];

  const handleSendMessage = (content: string) => {
    console.log('Sending message:', content);
    
    // Add patient message
    const patientMessage: ChatMessageProps = {
      id: Date.now().toString(),
      sender: 'patient',
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    
    setMessages(prev => [...prev, patientMessage]);
    setIsTyping(true);
    
    // Simulate AI response with random delay and response
    setTimeout(() => {
      const randomResponse = aiResponses[Math.floor(Math.random() * aiResponses.length)];
      // For patient view, only show responses with 90%+ confidence
      // Lower confidence responses would be escalated to experts first
      const aiResponse: ChatMessageProps = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: randomResponse.confidence >= 90 ? randomResponse.content : 
          'Let me provide you with some general guidance while I consult with our expert team for more personalized recommendations.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        // Don't include confidence scores for patient view
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500 + Math.random() * 2000);
  };

  return (
    <div className="h-full">
      <PatientChatInterface
        conversationTitle="Mental Health Support Session"
        messages={messages}
        isTyping={isTyping}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}