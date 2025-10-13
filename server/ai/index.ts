/**
 * Pimm AI Service - LangChain & LangGraph Implementation
 * 
 * This module provides AI-powered therapeutic conversations with:
 * - Empathetic, supportive responses using LangChain
 * - Confidence scoring for quality assurance
 * - Crisis detection and safety guardrails
 * - State management via LangGraph
 */

export { chatModel, structuredModel } from "./client";
export { 
  therapeuticPrompt, 
  confidenceScoringPrompt,
  THERAPEUTIC_SYSTEM_PROMPT,
  CONFIDENCE_SCORING_PROMPT,
} from "./prompts";
export {
  evaluateConfidence,
  detectCrisisKeywords,
  type ConfidenceAssessment,
  MetricEvaluationSchema,
  ConfidenceAssessmentSchema,
} from "./confidence";
export {
  buildConversationGraph,
  processPatientMessage,
  ConversationState,
} from "./graph";
