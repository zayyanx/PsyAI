import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Send, Bot, Shield, Loader2 } from "lucide-react";
import ChatMessage, { type ChatMessageProps } from "./ChatMessage";
import { cn } from "@/lib/utils";

export interface PatientChatInterfaceProps {
  patientName?: string;
  conversationTitle?: string;
  isTyping?: boolean;
  messages?: ChatMessageProps[];
  onSendMessage?: (message: string) => void;
  className?: string;
}

export default function PatientChatInterface({
  patientName = "You",
  conversationTitle = "Mental Health Consultation",
  isTyping = false,
  messages = [],
  onSendMessage,
  className,
}: PatientChatInterfaceProps) {
  const [inputValue, setInputValue] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSendMessage = () => {
    if (inputValue.trim() && onSendMessage) {
      onSendMessage(inputValue.trim());
      setInputValue("");
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card className={cn("flex flex-col h-full", className)} data-testid="chat-interface">
      {/* Header */}
      <CardHeader className="border-b pb-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg" data-testid="conversation-title">
              {conversationTitle}
            </CardTitle>
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                <span>AI Assistant</span>
              </div>
              <Badge variant="outline" className="bg-success/10 text-success border-success/20">
                <Shield className="h-3 w-3 mr-1" />
                Expert Monitored
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>

      {/* Messages Area */}
      <CardContent className="flex-1 p-0">
        <ScrollArea className="h-full" ref={scrollAreaRef} data-testid="messages-scroll-area">
          <div className="p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Bot className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p className="text-lg font-medium">Welcome to PsyAI</p>
                <p className="text-sm mt-1">
                  I'm here to provide mental health support with expert oversight.
                  How are you feeling today?
                </p>
              </div>
            ) : (
              messages.map((message, index) => (
                <ChatMessage
                  key={`${message.id}-${index}`}
                  {...message}
                />
              ))
            )}
            
            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex gap-3 mb-4">
                <div className="h-8 w-8 rounded-full bg-chart-1 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <Card className="p-4 bg-card border-chart-1/20">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">AI is thinking...</span>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1"
            disabled={isTyping}
            data-testid="input-message"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            size="icon"
            data-testid="button-send-message"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <div className="flex items-center gap-2">
            <Shield className="h-3 w-3" />
            <span>Secure & confidential</span>
          </div>
        </div>
      </div>
    </Card>
  );
}