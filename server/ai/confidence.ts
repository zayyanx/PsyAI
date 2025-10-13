import { z } from "zod";
import { structuredModel } from "./client";
import { confidenceScoringPrompt } from "./prompts";

/**
 * Schema for individual metric evaluation
 */
export const MetricEvaluationSchema = z.object({
  name: z.string().describe("Name of the metric"),
  passed: z.boolean().describe("Whether the metric passed (≥90%)"),
  reason: z.string().describe("Brief explanation for the score"),
});

/**
 * Schema for overall confidence assessment
 */
export const ConfidenceAssessmentSchema = z.object({
  metrics: z.array(MetricEvaluationSchema).describe("Individual metric evaluations"),
  overallScore: z.number().min(0).max(100).describe("Overall confidence score (0-100)"),
  needsExpertReview: z.boolean().describe("Whether expert review is needed"),
  crisisDetected: z.boolean().describe("Whether a crisis situation was detected"),
  escalationRequired: z.boolean().describe("Whether immediate escalation is required"),
  summary: z.string().describe("Brief summary of the assessment"),
});

export type ConfidenceAssessment = z.infer<typeof ConfidenceAssessmentSchema>;

/**
 * Evaluate AI response quality and generate confidence score
 */
export async function evaluateConfidence(
  patientMessage: string,
  aiResponse: string
): Promise<ConfidenceAssessment> {
  try {
    // Create structured output model
    const structuredLLM = structuredModel.withStructuredOutput(
      ConfidenceAssessmentSchema,
      { name: "confidence_assessment" }
    );

    // Format prompt
    const prompt = await confidenceScoringPrompt.format({
      patient_message: patientMessage,
      ai_response: aiResponse,
    });

    // Get structured evaluation
    const assessment = await structuredLLM.invoke(prompt);

    return assessment as ConfidenceAssessment;
  } catch (error) {
    console.error("Error evaluating confidence:", error);
    
    // Return conservative fallback assessment
    return {
      metrics: [
        { name: "Empathy & Validation", passed: false, reason: "Evaluation failed" },
        { name: "Safety & Appropriateness", passed: false, reason: "Evaluation failed" },
        { name: "Clarity & Coherence", passed: false, reason: "Evaluation failed" },
        { name: "Actionability", passed: false, reason: "Evaluation failed" },
        { name: "Professional Boundaries", passed: false, reason: "Evaluation failed" },
      ],
      overallScore: 0,
      needsExpertReview: true,
      crisisDetected: false,
      escalationRequired: true,
      summary: "Unable to evaluate response - defaulting to expert review",
    };
  }
}

/**
 * Detect crisis keywords in patient messages
 */
export function detectCrisisKeywords(message: string): boolean {
  const crisisKeywords = [
    "suicide", "kill myself", "end my life", "want to die",
    "self-harm", "cut myself", "hurt myself",
    "harm others", "hurt someone", "kill someone",
    "no reason to live", "better off dead",
  ];

  const lowerMessage = message.toLowerCase();
  return crisisKeywords.some(keyword => lowerMessage.includes(keyword));
}
