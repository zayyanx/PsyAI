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
      confidenceScore: 95,
      isReviewed: true,
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
      confidence: 92,
    },
    {
      content: 'Based on what you\'ve shared, it sounds like you might benefit from some cognitive behavioral techniques. However, I\'d recommend discussing this with a licensed therapist for personalized guidance.',
      confidence: 67,
    },
    {
      content: 'I\'m here to support you through this difficult time. Remember that seeking help is a sign of strength, not weakness. Would you like me to provide some immediate coping strategies while we work on a longer-term plan?',
      confidence: 78,
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
      const aiResponse: ChatMessageProps = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: randomResponse.content,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        confidenceScore: randomResponse.confidence,
        // Randomly add expert annotations for low confidence responses
        ...(randomResponse.confidence < 70 && Math.random() > 0.5 ? {
          expertAnnotation: 'This response has been reviewed by Dr. Sarah Wilson. Consider scheduling a follow-up session to discuss personalized treatment options.'
        } : {})
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