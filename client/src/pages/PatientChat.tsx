import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiRequest, queryClient } from '@/lib/queryClient';
import PatientChatInterface from '@/components/PatientChatInterface';
import { type ChatMessageProps } from '@/components/ChatMessage';

// Fixed conversation ID for this demo - in production, this would be dynamic per patient
const CONVERSATION_ID = 'conv-1';

export default function PatientChat() {
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<ChatMessageProps[]>([
    {
      id: 'welcome-msg',
      sender: 'ai',
      content: 'Hello! I\'m Pimm, your AI mental health assistant. I\'m here to provide supportive therapeutic conversations with expert oversight to ensure you receive quality care. How are you feeling today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  // Fetch existing messages when component loads
  const { data: existingMessages } = useQuery({
    queryKey: ['/api/conversations', CONVERSATION_ID, 'messages'],
    queryFn: () => fetch(`/api/conversations/${CONVERSATION_ID}/messages`).then(r => r.json()),
  });

  // Load existing messages into state
  useEffect(() => {
    if (existingMessages && existingMessages.length > 0) {
      const formattedMessages: ChatMessageProps[] = existingMessages.map((msg: any) => ({
        id: msg.id,
        sender: msg.sender,
        content: msg.content,
        timestamp: new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }));
      setMessages(formattedMessages);
    }
  }, [existingMessages]);

  // Mutation to send messages to AI
  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await apiRequest('POST', `/api/conversations/${CONVERSATION_ID}/chat`, { message });
      return response.json();
    },
    onSuccess: (data: any) => {
      // Add AI response to messages
      const aiMessage: ChatMessageProps = {
        id: data.aiMessage.id,
        sender: 'ai',
        content: data.aiMessage.content,
        timestamp: new Date(data.aiMessage.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
      
      // Invalidate queries to refresh conversation data
      queryClient.invalidateQueries({ queryKey: ['/api/conversations'] });
      queryClient.invalidateQueries({ queryKey: ['/api/conversations', CONVERSATION_ID, 'messages'] });
    },
    onError: (error) => {
      console.error('Error sending message:', error);
      setIsTyping(false);
      
      // Show error message to user
      const errorMessage: ChatMessageProps = {
        id: Date.now().toString(),
        sender: 'ai',
        content: 'I\'m having trouble processing your message right now. Please try again or reach out to a mental health professional if you need immediate support.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, errorMessage]);
    },
  });

  const handleSendMessage = async (content: string) => {
    console.log('Sending message to AI:', content);
    
    // Add patient message immediately
    const patientMessage: ChatMessageProps = {
      id: Date.now().toString(),
      sender: 'patient',
      content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    
    setMessages(prev => [...prev, patientMessage]);
    setIsTyping(true);
    
    // Send to AI via LangGraph
    await chatMutation.mutateAsync(content);
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