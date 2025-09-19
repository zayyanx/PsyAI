import { sql } from "drizzle-orm";
import { pgTable, text, varchar, timestamp, integer, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Users table for both patients and experts
export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  role: text("role", { enum: ["patient", "expert", "admin"] }).notNull().default("patient"),
  name: text("name").notNull(),
  specialization: text("specialization"), // For experts
  createdAt: timestamp("created_at").defaultNow(),
});

// Conversations between patients and AI agents
export const conversations = pgTable("conversations", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  patientId: varchar("patient_id").notNull().references(() => users.id),
  title: text("title").notNull(),
  status: text("status", { enum: ["active", "pending_review", "reviewed", "closed"] }).default("active"),
  confidenceScore: integer("confidence_score").default(85), // 0-100
  needsExpertReview: boolean("needs_expert_review").default(false),
  reviewedBy: varchar("reviewed_by").references(() => users.id),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Messages within conversations
export const messages = pgTable("messages", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  conversationId: varchar("conversation_id").notNull().references(() => conversations.id),
  sender: text("sender", { enum: ["patient", "ai", "expert"] }).notNull(),
  content: text("content").notNull(),
  confidenceScore: integer("confidence_score"), // For AI messages
  expertAnnotation: text("expert_annotation"), // Expert feedback on AI responses
  timestamp: timestamp("timestamp").defaultNow(),
});

// Expert reviews and feedback
export const expertReviews = pgTable("expert_reviews", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  conversationId: varchar("conversation_id").notNull().references(() => conversations.id),
  expertId: varchar("expert_id").notNull().references(() => users.id),
  status: text("status", { enum: ["pending", "approved", "modified", "escalated"] }).default("pending"),
  feedback: text("feedback"),
  modifications: text("modifications"), // JSON string of suggested changes
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
});

export const insertExpertReviewSchema = createInsertSchema(expertReviews).pick({
  conversationId: true,
  expertId: true,
  feedback: true,
  status: true,
  modifications: true,
});

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type Conversation = typeof conversations.$inferSelect;
export type InsertConversation = z.infer<typeof insertConversationSchema>;
export type Message = typeof messages.$inferSelect;
export type InsertMessage = z.infer<typeof insertMessageSchema>;
export type ExpertReview = typeof expertReviews.$inferSelect;
export type InsertExpertReview = z.infer<typeof insertExpertReviewSchema>;
