import ChatMessage from '../ChatMessage';

export default function ChatMessageExample() {
  return (
    <div className="p-4 space-y-4 max-w-2xl">
      <div className="mb-4 p-3 bg-muted/50 rounded-lg">
        <h3 className="font-medium text-sm mb-1">Expert View - Full Information</h3>
        <p className="text-xs text-muted-foreground">Experts see confidence scores and annotations</p>
      </div>
      
      {/* Patient message */}
      <ChatMessage
        id="1"
        sender="patient"
        content="I've been feeling really anxious lately, especially at work. It's affecting my sleep and concentration. What should I do?"
        timestamp="2:30 PM"
        viewerRole="expert"
      />

      {/* AI response with high confidence */}
      <ChatMessage
        id="2"
        sender="ai"
        content="Thank you for sharing that with me. Workplace anxiety is very common and there are several effective strategies we can explore. First, let's work on some immediate coping techniques like deep breathing exercises and grounding methods. I'd also recommend establishing a consistent sleep routine, as better sleep can significantly improve your ability to manage anxiety during the day."
        timestamp="2:31 PM"
        confidenceScore={92}
        isReviewed={true}
        viewerRole="expert"
      />

      {/* AI response with low confidence and expert annotation */}
      <ChatMessage
        id="3"
        sender="ai"
        content="Based on your symptoms, you might want to consider medication options. However, I'd recommend discussing this with a healthcare professional first."
        timestamp="2:35 PM"
        confidenceScore={45}
        expertAnnotation="This response correctly suggests professional consultation but lacks specificity about therapy options. Consider recommending cognitive behavioral therapy (CBT) as a first-line treatment before medication."
        viewerRole="expert"
      />

      {/* Expert message */}
      <ChatMessage
        id="4"
        sender="expert"
        content="I'd like to add that Cognitive Behavioral Therapy (CBT) has shown excellent results for workplace anxiety. We can start with identifying specific triggers in your work environment and developing personalized coping strategies. Would you like to schedule a session to explore this further?"
        timestamp="3:45 PM"
      />
    </div>
  );
}