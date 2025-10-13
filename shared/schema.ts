import { sql } from "drizzle-orm";
import { pgTable, text, varchar, timestamp, integer, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Users table for both patients and experts
export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  role: text("role", { enum: ["patient", "nurse", "doctor", "admin"] }).notNull().default("patient"),
  name: text("name").notNull(),
  specialization: text("specialization"), // For nurses and doctors
  createdAt: timestamp("created_at").defaultNow(),
});

// Conversations between patients and AI agents
export const conversations = pgTable("conversations", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  patientId: varchar("patient_id").notNull().references(() => users.id),
  title: text("title").notNull(),
  status: text("status", { enum: ["active", "pending_review", "reviewed", "closed"] }).default("active"),
  confidenceScore: integer("confidence_score").default(85), // Overall composite score (0-100)
  // Average confidence breakdown across all AI messages in conversation
  avgDecisionAlignment: integer("avg_decision_alignment"),
  avgClinicalAccuracy: integer("avg_clinical_accuracy"), 
  avgSafetyAssessment: integer("avg_safety_assessment"),
  avgContextUnderstanding: integer("avg_context_understanding"),
  avgResponseAppropriateness: integer("avg_response_appropriateness"),
  needsNurseReview: boolean("needs_nurse_review").default(false),
  needsDoctorReview: boolean("needs_doctor_review").default(false),
  nurseReviewedBy: varchar("nurse_reviewed_by").references(() => users.id),
  doctorReviewedBy: varchar("doctor_reviewed_by").references(() => users.id),
  escalatedToDoctor: boolean("escalated_to_doctor").default(false),
  escalationReason: text("escalation_reason"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Messages within conversations
export const messages = pgTable("messages", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  conversationId: varchar("conversation_id").notNull().references(() => conversations.id),
  sender: text("sender", { enum: ["patient", "ai", "nurse", "doctor"] }).notNull(),
  content: text("content").notNull(),
  confidenceScore: integer("confidence_score"), // Overall composite score (0-100)
  // Detailed confidence breakdown (0-100 each)
  decisionAlignment: integer("decision_alignment"), // How well aligned with clinical protocols
  clinicalAccuracy: integer("clinical_accuracy"), // Medical soundness of the response
  safetyAssessment: integer("safety_assessment"), // Safety of recommendations
  contextUnderstanding: integer("context_understanding"), // AI's grasp of patient context
  responseAppropriateness: integer("response_appropriateness"), // Tone and approach suitability
  nurseAnnotation: text("nurse_annotation"), // Nurse feedback on AI responses
  doctorAnnotation: text("doctor_annotation"), // Doctor feedback on AI responses
  timestamp: timestamp("timestamp").defaultNow(),
});

// Medical staff reviews and feedback
export const medicalReviews = pgTable("medical_reviews", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  conversationId: varchar("conversation_id").notNull().references(() => conversations.id),
  reviewerId: varchar("reviewer_id").notNull().references(() => users.id), // nurse or doctor
  reviewerRole: text("reviewer_role", { enum: ["nurse", "doctor"] }).notNull(),
  status: text("status", { enum: ["pending", "approved", "modified", "escalated_to_doctor", "completed"] }).default("pending"),
  feedback: text("feedback"),
  modifications: text("modifications"), // JSON string of suggested changes
  escalationReason: text("escalation_reason"), // Why escalated to doctor
  createdAt: timestamp("created_at").defaultNow(),
});

// Zod schemas
export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
  name: true,
  role: true,
  specialization: true,
});

export const insertConversationSchema = createInsertSchema(conversations).pick({
  patientId: true,
  title: true,
});

export const insertMessageSchema = createInsertSchema(messages).pick({
  conversationId: true,
  sender: true,
  content: true,
  confidenceScore: true,
  decisionAlignment: true,
  clinicalAccuracy: true,
  safetyAssessment: true,
  contextUnderstanding: true,
  responseAppropriateness: true,
  nurseAnnotation: true,
  doctorAnnotation: true,
});

export const insertMedicalReviewSchema = createInsertSchema(medicalReviews).pick({
  conversationId: true,
  reviewerId: true,
  reviewerRole: true,
  feedback: true,
  status: true,
  modifications: true,
  escalationReason: true,
});

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type Conversation = typeof conversations.$inferSelect;
export type InsertConversation = z.infer<typeof insertConversationSchema>;
export type Message = typeof messages.$inferSelect;
export type InsertMessage = z.infer<typeof insertMessageSchema>;
export type MedicalReview = typeof medicalReviews.$inferSelect;
export type InsertMedicalReview = z.infer<typeof insertMedicalReviewSchema>;
