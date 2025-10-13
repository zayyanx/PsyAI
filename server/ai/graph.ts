import { StateGraph, Annotation, START, END } from "@langchain/langgraph";
import { AIMessage, HumanMessage, BaseMessage } from "@langchain/core/messages";
import { chatModel } from "./client";
import { therapeuticPrompt } from "./prompts";
import { evaluateConfidence, detectCrisisKeywords, type ConfidenceAssessment } from "./confidence";

/**
 * State definition for therapeutic conversation flow
 */
export const ConversationState = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: (current, update) => current.concat(update),
    default: () => [],
  }),
  patientMessage: Annotation<string>({
    reducer: (_, update) => update,
    default: () => "",
  }),
  aiResponse: Annotation<string>({
    reducer: (_, update) => update,
    default: () => "",
  }),
  confidenceAssessment: Annotation<ConfidenceAssessment | null>({
    reducer: (_, update) => update,
    default: () => null,
  }),
  crisisDetected: Annotation<boolean>({
    reducer: (_, update) => update,
    default: () => false,
  }),
  conversationId: Annotation<string>({
    reducer: (_, update) => update,
    default: () => "",
  }),
});

/**
 * Node: Check for crisis keywords in patient message
 */
async function checkCrisis(state: typeof ConversationState.State) {
  const crisisDetected = detectCrisisKeywords(state.patientMessage);
  return { crisisDetected };
}

/**
 * Node: Generate AI therapeutic response
 */
async function generateResponse(state: typeof ConversationState.State) {
  try {
    // Format chat history for prompt
    const chatHistory = state.messages.slice(-10); // Keep last 10 messages for context

    // Generate response using therapeutic prompt
    const prompt = await therapeuticPrompt.format({
      chat_history: chatHistory,
      input: state.patientMessage,
    });

    const response = await chatModel.invoke(prompt);
    const aiResponse = response.content.toString();

    // Add messages to history
    const newMessages = [
      new HumanMessage(state.patientMessage),
      new AIMessage(aiResponse),
    ];

    return {
      aiResponse,
      messages: newMessages,
    };
  } catch (error) {
    console.error("Error generating AI response:", error);
    const fallbackResponse = "I'm having trouble processing your message right now. This is important - please consider reaching out to a mental health professional who can provide immediate support.";
    
    return {
      aiResponse: fallbackResponse,
      messages: [
        new HumanMessage(state.patientMessage),
        new AIMessage(fallbackResponse),
      ],
    };
  }
}

/**
 * Node: Generate crisis response when crisis is detected
 */
async function generateCrisisResponse(state: typeof ConversationState.State) {
  const crisisResponse = `I'm really concerned about what you've shared. Your safety is the top priority right now. Please reach out to:

• **National Suicide Prevention Lifeline**: 988 (call or text)
• **Crisis Text Line**: Text HOME to 741741
• **Emergency Services**: 911

A trained professional can provide immediate support. You don't have to go through this alone - help is available 24/7.`;

  const newMessages = [
    new HumanMessage(state.patientMessage),
    new AIMessage(crisisResponse),
  ];

  return {
    aiResponse: crisisResponse,
    messages: newMessages,
  };
}

/**
 * Node: Evaluate confidence of AI response
 */
async function evaluateResponse(state: typeof ConversationState.State) {
  try {
    const assessment = await evaluateConfidence(
      state.patientMessage,
      state.aiResponse
    );

    return { confidenceAssessment: assessment };
  } catch (error) {
    console.error("Error evaluating response:", error);
    // Return conservative assessment on error
    return {
      confidenceAssessment: {
        metrics: [],
        overallScore: 0,
        needsExpertReview: true,
        crisisDetected: state.crisisDetected,
        escalationRequired: true,
        summary: "Evaluation failed - flagging for expert review",
      },
    };
  }
}

/**
 * Conditional edge: Route based on crisis detection
 */
function routeAfterCrisisCheck(state: typeof ConversationState.State): string {
  return state.crisisDetected ? "crisis_response" : "generate_response";
}

/**
 * Build the therapeutic conversation graph
 */
export function buildConversationGraph() {
  const workflow = new StateGraph(ConversationState)
    // Add nodes
    .addNode("check_crisis", checkCrisis)
    .addNode("generate_response", generateResponse)
    .addNode("crisis_response", generateCrisisResponse)
    .addNode("evaluate_response", evaluateResponse)
    
    // Define edges
    .addEdge(START, "check_crisis")
    .addConditionalEdges("check_crisis", routeAfterCrisisCheck, {
      crisis_response: "crisis_response",
      generate_response: "generate_response",
    })
    .addEdge("generate_response", "evaluate_response")
    .addEdge("crisis_response", "evaluate_response")
    .addEdge("evaluate_response", END);

  return workflow.compile();
}

/**
 * Main function to process a patient message through the conversation graph
 */
export async function processPatientMessage(
  conversationId: string,
  patientMessage: string,
  chatHistory: BaseMessage[] = []
) {
  const graph = buildConversationGraph();

  const result = await graph.invoke({
    conversationId,
    patientMessage,
    messages: chatHistory,
  });

  return {
    aiResponse: result.aiResponse,
    confidenceAssessment: result.confidenceAssessment,
    crisisDetected: result.crisisDetected,
    messages: result.messages,
  };
}
