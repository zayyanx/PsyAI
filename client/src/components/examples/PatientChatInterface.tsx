import { useState } from 'react';
import PatientChatInterface from '../PatientChatInterface';
import { type ChatMessageProps } from '../ChatMessage';

export default function PatientChatInterfaceExample() {
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<ChatMessageProps[]>([
    {
      id: '1',
      sender: 'ai',
      content: 'Hello! I\'m your AI mental health assistant. I\'m here to provide support and guidance, with expert oversight to ensure you receive the best care. How are you feeling today?',
      timestamp: '10:30 AM',
    },
    {
      id: '2', 
      sender: 'patient',
      content: 'Hi, I\'ve been struggling with anxiety lately, especially around work deadlines. It\'s been affecting my sleep.',
      timestamp: '10:32 AM',
    },
    {
      id: '3',
      sender: 'ai',
      content: 'Thank you for sharing that with me. Workplace anxiety is very common, and I want to help you develop some effective coping strategies. Can you tell me more about when these feelings are strongest? Is it throughout the workday, or mainly when deadlines approach?',
      timestamp: '10:33 AM',
    },
  ]);

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
    
    // Simulate AI response after delay
    setTimeout(() => {
      const aiResponse: ChatMessageProps = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        content: 'I understand. Let me help you with some strategies for managing work-related anxiety. Based on what you\'ve shared, I\'d recommend starting with some grounding techniques that you can use during stressful moments at work.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        // Patient view doesn't show confidence scores - responses below 90% confidence are filtered by proxy agent
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 2000);
  };

  return (
    <div className="h-[600px] max-w-4xl p-4">
      <PatientChatInterface
        conversationTitle="Anxiety Management Session"
        messages={messages}
        isTyping={isTyping}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}