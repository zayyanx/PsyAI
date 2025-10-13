import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertMedicalReviewSchema } from "@shared/schema";
import { processPatientMessage } from "./ai";
import { HumanMessage, AIMessage } from "@langchain/core/messages";

export async function registerRoutes(app: Express): Promise<Server> {
  // Conversations API
  app.get("/api/conversations", async (req, res) => {
    try {
      const conversations = await storage.getAllConversations();
      res.json(conversations);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch conversations" });
    }
  });

  app.get("/api/conversations/:id", async (req, res) => {
    try {
      const conversation = await storage.getConversation(req.params.id);
      if (!conversation) {
        return res.status(404).json({ error: "Conversation not found" });
      }
      res.json(conversation);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch conversation" });
    }
  });

  app.patch("/api/conversations/:id", async (req, res) => {
    try {
      const updated = await storage.updateConversation(req.params.id, req.body);
      if (!updated) {
        return res.status(404).json({ error: "Conversation not found" });
      }
      res.json(updated);
    } catch (error) {
      res.status(500).json({ error: "Failed to update conversation" });
    }
  });

  // Messages API
  app.get("/api/conversations/:id/messages", async (req, res) => {
    try {
      const messages = await storage.getConversationMessages(req.params.id);
      res.json(messages);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch messages" });
    }
  });

  // AI Chat API - Process patient messages through LangGraph
  app.post("/api/conversations/:id/chat", async (req, res) => {
    try {
      const conversationId = req.params.id;
      const { message: patientMessage } = req.body;

      if (!patientMessage || typeof patientMessage !== 'string') {
        return res.status(400).json({ error: "Message is required" });
      }

      // Get conversation and existing messages for context
      const conversation = await storage.getConversation(conversationId);
      if (!conversation) {
        return res.status(404).json({ error: "Conversation not found" });
      }

      const existingMessages = await storage.getConversationMessages(conversationId);
      
      // Convert existing messages to LangChain format for context
      const chatHistory = existingMessages.map(msg => 
        msg.sender === 'patient' 
          ? new HumanMessage(msg.content)
          : new AIMessage(msg.content)
      );

      // Process through LangGraph
      const result = await processPatientMessage(
        conversationId,
        patientMessage,
        chatHistory
      );

      // Save patient message
      const patientMsg = await storage.createMessage({
        conversationId,
        sender: 'patient',
        content: patientMessage,
        confidenceScore: null,
        decisionAlignment: null,
        clinicalAccuracy: null,
        safetyAssessment: null,
        contextUnderstanding: null,
        responseAppropriateness: null,
        nurseAnnotation: null,
        doctorAnnotation: null,
      });

      // Save AI response with confidence metrics
      const assessment = result.confidenceAssessment;
      const metrics = assessment?.metrics || [];
      
      // Map metrics by name to avoid ordering issues
      const getMetricScore = (name: string) => {
        const metric = metrics.find(m => m.name.toLowerCase().includes(name.toLowerCase()));
        return metric?.passed ? 90 : 80;
      };
      
      const aiMsg = await storage.createMessage({
        conversationId,
        sender: 'ai',
        content: result.aiResponse,
        confidenceScore: assessment?.overallScore || 0,
        // Map metrics by name for reliability
        decisionAlignment: getMetricScore('empathy'),
        clinicalAccuracy: getMetricScore('safety'),
        safetyAssessment: getMetricScore('clarity'),
        contextUnderstanding: getMetricScore('actionability'),
        responseAppropriateness: getMetricScore('boundaries'),
        nurseAnnotation: assessment?.summary || null,
        doctorAnnotation: null,
      });

      // Update conversation with latest confidence score and review flags
      const needsReview = assessment?.needsExpertReview || (assessment?.overallScore ?? 0) < 90;
      const escalationNeeded = assessment?.escalationRequired || result.crisisDetected;

      await storage.updateConversation(conversationId, {
        confidenceScore: assessment?.overallScore || 0,
        needsNurseReview: needsReview,
        needsDoctorReview: escalationNeeded,
        status: needsReview ? 'pending_review' : 'active',
        updatedAt: new Date(),
      });

      res.json({
        patientMessage: patientMsg,
        aiMessage: aiMsg,
        confidenceAssessment: assessment,
        crisisDetected: result.crisisDetected,
      });
    } catch (error) {
      console.error("Error processing chat message:", error);
      res.status(500).json({ error: "Failed to process message" });
    }
  });

  // Medical Reviews API
  app.get("/api/conversations/:id/review", async (req, res) => {
    try {
      const review = await storage.getMedicalReview(req.params.id);
      res.json(review);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch review" });
    }
  });

  app.post("/api/medical-reviews", async (req, res) => {
    try {
      const validatedData = insertMedicalReviewSchema.parse(req.body);
      const review = await storage.createMedicalReview(validatedData);
      
      // Update conversation status based on review
      if (validatedData.status === 'escalated_to_doctor') {
        await storage.updateConversation(validatedData.conversationId, {
          escalatedToDoctor: true,
          needsDoctorReview: true,
          escalationReason: validatedData.escalationReason || undefined
        });
      }
      
      res.json(review);
    } catch (error) {
      res.status(400).json({ error: "Failed to create review", details: error });
    }
  });

  app.patch("/api/medical-reviews/:id", async (req, res) => {
    try {
      const updated = await storage.updateMedicalReview(req.params.id, req.body);
      if (!updated) {
        return res.status(404).json({ error: "Review not found" });
      }
      res.json(updated);
    } catch (error) {
      res.status(500).json({ error: "Failed to update review" });
    }
  });

  // Combined endpoint for message detail view
  app.get("/api/messages/:conversationId/detail", async (req, res) => {
    try {
      const conversation = await storage.getConversation(req.params.conversationId);
      if (!conversation) {
        return res.status(404).json({ error: "Conversation not found" });
      }

      const messages = await storage.getConversationMessages(req.params.conversationId);
      const patient = await storage.getUser(conversation.patientId);
      const review = await storage.getMedicalReview(req.params.conversationId);

      const nurseReviewer = conversation.nurseReviewedBy ? 
        await storage.getUser(conversation.nurseReviewedBy) : null;
      const doctorReviewer = conversation.doctorReviewedBy ? 
        await storage.getUser(conversation.doctorReviewedBy) : null;

      res.json({
        conversation,
        messages,
        patient,
        review,
        nurseReviewer,
        doctorReviewer
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch message details" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}