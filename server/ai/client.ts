import { ChatOpenAI } from "@langchain/openai";

// This is using Replit's AI Integrations service, which provides OpenAI-compatible API access 
// without requiring your own OpenAI API key. Charges are billed to your Replit credits.

// the newest OpenAI model is "gpt-5" which was released August 7, 2025. do not change this unless explicitly requested by the user
export const chatModel = new ChatOpenAI({
  modelName: "gpt-5",
  temperature: 1, // gpt-5 defaults to 1 and cannot be changed
  maxTokens: 8192,
  configuration: {
    baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL,
    apiKey: process.env.AI_INTEGRATIONS_OPENAI_API_KEY,
  },
});

// Model for structured outputs and confidence scoring
// Temperature 0 for deterministic safety assessments
export const structuredModel = new ChatOpenAI({
  modelName: "gpt-5",
  temperature: 0, // Deterministic for consistent safety/quality evaluations
  maxTokens: 8192,
  configuration: {
    baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL,
    apiKey: process.env.AI_INTEGRATIONS_OPENAI_API_KEY,
  },
});
