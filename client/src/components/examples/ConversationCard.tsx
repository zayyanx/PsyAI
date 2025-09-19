import ConversationCard from '../ConversationCard';

export default function ConversationCardExample() {
  const handleView = () => {
    console.log('View conversation clicked');
  };

  const handleReview = () => {
    console.log('Review conversation clicked');
  };

  return (
    <div className="p-6 space-y-4 max-w-md">
      {/* Active conversation with high confidence */}
      <ConversationCard
        id="1"
        title="Anxiety Management Discussion"
        patientName="Sarah Johnson"
        status="active"
        confidenceScore={87}
        needsExpertReview={false}
        lastMessage="Thank you for the breathing exercises. I've been practicing them daily and they seem to help with my morning anxiety."
        timestamp="2 hours ago"
        messageCount={12}
        onView={handleView}
        onReview={handleReview}
      />
      
      {/* Pending review with low confidence */}
      <ConversationCard
        id="2"
        title="Depression Symptoms Assessment"
        patientName="Michael Chen"
        status="pending_review"
        confidenceScore={45}
        needsExpertReview={true}
        lastMessage="I'm not sure if the medication is working. Should I increase the dosage or try something different?"
        timestamp="1 day ago"
        messageCount={8}
        onView={handleView}
        onReview={handleReview}
      />
      
      {/* Reviewed conversation */}
      <ConversationCard
        id="3"
        title="Sleep Pattern Improvement"
        patientName="Emily Rodriguez"
        status="reviewed"
        confidenceScore={92}
        needsExpertReview={false}
        lastMessage="My sleep has improved significantly with the new routine. Thank you for the guidance."
        timestamp="3 days ago"
        messageCount={15}
        onView={handleView}
      />
    </div>
  );
}