import { type User, type InsertUser, type Conversation, type InsertConversation, type Message, type InsertMessage, type MedicalReview, type InsertMedicalReview } from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  // User operations
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Conversation operations
  getConversation(id: string): Promise<Conversation | undefined>;
  getConversationsByPatientId(patientId: string): Promise<Conversation[]>;
  getAllConversations(): Promise<Conversation[]>;
  createConversation(conversation: InsertConversation): Promise<Conversation>;
  updateConversation(id: string, updates: Partial<Conversation>): Promise<Conversation | undefined>;
  
  // Message operations
  getConversationMessages(conversationId: string): Promise<Message[]>;
  createMessage(message: InsertMessage): Promise<Message>;
  updateMessage(id: string, updates: Partial<Message>): Promise<Message | undefined>;
  
  // Medical review operations
  getMedicalReview(conversationId: string): Promise<MedicalReview | undefined>;
  createMedicalReview(review: InsertMedicalReview): Promise<MedicalReview>;
  updateMedicalReview(id: string, updates: Partial<MedicalReview>): Promise<MedicalReview | undefined>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private conversations: Map<string, Conversation>;
  private messages: Map<string, Message>;
  private medicalReviews: Map<string, MedicalReview>;

  constructor() {
    this.users = new Map();
    this.conversations = new Map();
    this.messages = new Map();
    this.medicalReviews = new Map();
    
    // Initialize with sample data
    this.initializeSampleData();
  }

  private initializeSampleData() {
    // Create sample users
    const nurse: User = {
      id: 'nurse-1',
      username: 'jadams',
      password: 'hashedpass',
      role: 'nurse',
      name: 'Jennifer Adams',
      specialization: 'Mental Health',
      createdAt: new Date()
    };

    const doctor: User = {
      id: 'doctor-1',
      username: 'swilson',
      password: 'hashedpass',
      role: 'doctor',
      name: 'Dr. Sarah Wilson',
      specialization: 'Psychiatry',
      createdAt: new Date()
    };

    const patient: User = {
      id: 'patient-1',
      username: 'sjohnson',
      password: 'hashedpass',
      role: 'patient',
      name: 'Sarah Johnson',
      specialization: null,
      createdAt: new Date()
    };

    this.users.set(nurse.id, nurse);
    this.users.set(doctor.id, doctor);
    this.users.set(patient.id, patient);

    // Create sample conversations
    const conv1: Conversation = {
      id: 'conv-1',
      patientId: 'patient-1',
      title: 'Work-related anxiety support',
      status: 'pending_review',
      confidenceScore: 20, // 1 out of 5 metrics pass (only Safety Assessment >= 90%)
      avgDecisionAlignment: 75,
      avgClinicalAccuracy: 82,
      avgSafetyAssessment: 90,
      avgContextUnderstanding: 68,
      avgResponseAppropriateness: 72,
      needsNurseReview: true,
      needsDoctorReview: false,
      nurseReviewedBy: null,
      doctorReviewedBy: null,
      escalatedToDoctor: false,
      escalationReason: null,
      createdAt: new Date('2024-01-15T14:30:00'),
      updatedAt: new Date('2024-01-15T15:15:00')
    };

    const conv2: Conversation = {
      id: 'conv-2',
      patientId: 'patient-1',
      title: 'Panic attack management',
      status: 'reviewed',
      confidenceScore: 0, // 0 out of 5 metrics pass
      avgDecisionAlignment: 35,
      avgClinicalAccuracy: 42,
      avgSafetyAssessment: 65,
      avgContextUnderstanding: 25,
      avgResponseAppropriateness: 20,
      needsNurseReview: false,
      needsDoctorReview: true,
      nurseReviewedBy: 'nurse-1',
      doctorReviewedBy: null,
      escalatedToDoctor: true,
      escalationReason: 'Complex anxiety presentation requires clinical evaluation for potential therapy referral',
      createdAt: new Date('2024-01-16T10:00:00'),
      updatedAt: new Date('2024-01-16T11:30:00')
    };

    this.conversations.set(conv1.id, conv1);
    this.conversations.set(conv2.id, conv2);

    // Create sample messages
    const messages: Message[] = [
      {
        id: 'msg-1',
        conversationId: 'conv-1',
        sender: 'patient',
        content: 'I\'ve been feeling really anxious lately, especially about work deadlines. It\'s starting to affect my sleep and I find myself worrying constantly.',
        confidenceScore: null,
        decisionAlignment: null,
        clinicalAccuracy: null,
        safetyAssessment: null,
        contextUnderstanding: null,
        responseAppropriateness: null,
        nurseAnnotation: null,
        doctorAnnotation: null,
        timestamp: new Date('2024-01-15T14:31:45')
      },
      {
        id: 'msg-2',
        conversationId: 'conv-1',
        sender: 'ai',
        content: 'It sounds like you\'re experiencing perfectionism-related anxiety, which often stems from fear of disappointment or criticism. This is a very treatable condition. Let me suggest some cognitive behavioral techniques that can help you manage these thoughts and reduce the physical symptoms of anxiety.',
        confidenceScore: 20, // 1 out of 5 metrics pass (only Safety Assessment >= 90%)
        decisionAlignment: 75,
        clinicalAccuracy: 82,
        safetyAssessment: 90,
        contextUnderstanding: 68,
        responseAppropriateness: 72,
        nurseAnnotation: 'Low confidence response - needs professional review for CBT recommendation appropriateness',
        doctorAnnotation: null,
        timestamp: new Date('2024-01-15T14:34:45')
      },
      {
        id: 'msg-3',
        conversationId: 'conv-2',
        sender: 'patient',
        content: 'I\'ve been having panic attacks at work, especially when deadlines approach. Yesterday I had to leave a meeting because I couldn\'t breathe properly. This is affecting my performance and I\'m worried about losing my job.',
        confidenceScore: null,
        decisionAlignment: null,
        clinicalAccuracy: null,
        safetyAssessment: null,
        contextUnderstanding: null,
        responseAppropriateness: null,
        nurseAnnotation: null,
        doctorAnnotation: null,
        timestamp: new Date('2024-01-16T10:01:45')
      },
      {
        id: 'msg-4',
        conversationId: 'conv-2',
        sender: 'ai',
        content: 'I understand this must be very distressing. Panic attacks are a treatable condition. Let me guide you through some immediate coping techniques and then we can work on longer-term strategies.',
        confidenceScore: 0, // 0 out of 5 metrics pass
        decisionAlignment: 35,
        clinicalAccuracy: 42,
        safetyAssessment: 65,
        contextUnderstanding: 25,
        responseAppropriateness: 20,
        nurseAnnotation: null,
        doctorAnnotation: null,
        timestamp: new Date('2024-01-16T10:02:30')
      }
    ];

    messages.forEach(msg => this.messages.set(msg.id, msg));

    // Create sample medical reviews
    const review1: MedicalReview = {
      id: 'review-1',
      conversationId: 'conv-2',
      reviewerId: 'nurse-1',
      reviewerRole: 'nurse',
      status: 'escalated_to_doctor',
      feedback: 'Patient presenting with severe panic attacks affecting work performance. AI confidence very low. Recommend immediate clinical assessment.',
      modifications: null,
      escalationReason: 'Complex anxiety presentation requires clinical evaluation for potential therapy referral',
      createdAt: new Date('2024-01-16T11:30:00')
    };

    this.medicalReviews.set(review1.id, review1);
  }

  // User operations
  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { 
      ...insertUser, 
      id, 
      createdAt: new Date(),
      role: insertUser.role || 'patient',
      specialization: insertUser.specialization || null
    };
    this.users.set(id, user);
    return user;
  }

  // Conversation operations
  async getConversation(id: string): Promise<Conversation | undefined> {
    return this.conversations.get(id);
  }

  async getConversationsByPatientId(patientId: string): Promise<Conversation[]> {
    return Array.from(this.conversations.values()).filter(
      (conv) => conv.patientId === patientId
    );
  }

  async getAllConversations(): Promise<Conversation[]> {
    return Array.from(this.conversations.values());
  }

  async createConversation(conversation: InsertConversation): Promise<Conversation> {
    const id = randomUUID();
    // Generate realistic detailed confidence scores
    const detailedScores = {
      avgDecisionAlignment: Math.floor(Math.random() * 40) + 60, // 60-99%
      avgClinicalAccuracy: Math.floor(Math.random() * 30) + 70, // 70-99%  
      avgSafetyAssessment: Math.floor(Math.random() * 20) + 80, // 80-99%
      avgContextUnderstanding: Math.floor(Math.random() * 50) + 50, // 50-99%
      avgResponseAppropriateness: Math.floor(Math.random() * 40) + 60, // 60-99%
    };
    
    // Calculate overall score as percentage of metrics that pass (>= 90%)
    const scores = [
      detailedScores.avgDecisionAlignment,
      detailedScores.avgClinicalAccuracy,
      detailedScores.avgSafetyAssessment,
      detailedScores.avgContextUnderstanding,
      detailedScores.avgResponseAppropriateness
    ];
    const passingMetrics = scores.filter(score => score >= 90).length;
    const overallScore = Math.round((passingMetrics / scores.length) * 100);
    
    const newConversation: Conversation = {
      ...conversation,
      id,
      status: 'active',
      confidenceScore: overallScore,
      ...detailedScores,
      needsNurseReview: false,
      needsDoctorReview: false,
      nurseReviewedBy: null,
      doctorReviewedBy: null,
      escalatedToDoctor: false,
      escalationReason: null,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    this.conversations.set(id, newConversation);
    return newConversation;
  }

  async updateConversation(id: string, updates: Partial<Conversation>): Promise<Conversation | undefined> {
    const existing = this.conversations.get(id);
    if (!existing) return undefined;
    
    const updated: Conversation = { ...existing, ...updates, updatedAt: new Date() };
    this.conversations.set(id, updated);
    return updated;
  }

  // Message operations
  async getConversationMessages(conversationId: string): Promise<Message[]> {
    return Array.from(this.messages.values())
      .filter((msg) => msg.conversationId === conversationId)
      .sort((a, b) => {
        const timeA = a.timestamp?.getTime() || 0;
        const timeB = b.timestamp?.getTime() || 0;
        return timeA - timeB;
      });
  }

  async createMessage(message: InsertMessage): Promise<Message> {
    const id = randomUUID();
    const newMessage: Message = {
      ...message,
      id,
      confidenceScore: message.confidenceScore || null,
      decisionAlignment: null,
      clinicalAccuracy: null,
      safetyAssessment: null,
      contextUnderstanding: null,
      responseAppropriateness: null,
      nurseAnnotation: null,
      doctorAnnotation: null,
      timestamp: new Date()
    };
    this.messages.set(id, newMessage);
    return newMessage;
  }

  async updateMessage(id: string, updates: Partial<Message>): Promise<Message | undefined> {
    const existing = this.messages.get(id);
    if (!existing) return undefined;
    
    const updated: Message = { ...existing, ...updates };
    this.messages.set(id, updated);
    return updated;
  }

  // Medical review operations
  async getMedicalReview(conversationId: string): Promise<MedicalReview | undefined> {
    return Array.from(this.medicalReviews.values()).find(
      (review) => review.conversationId === conversationId
    );
  }

  async createMedicalReview(review: InsertMedicalReview): Promise<MedicalReview> {
    const id = randomUUID();
    const newReview: MedicalReview = {
      ...review,
      id,
      status: review.status || 'pending',
      feedback: review.feedback || null,
      modifications: review.modifications || null,
      escalationReason: review.escalationReason || null,
      createdAt: new Date()
    };
    this.medicalReviews.set(id, newReview);
    return newReview;
  }

  async updateMedicalReview(id: string, updates: Partial<MedicalReview>): Promise<MedicalReview | undefined> {
    const existing = this.medicalReviews.get(id);
    if (!existing) return undefined;
    
    const updated: MedicalReview = { ...existing, ...updates };
    this.medicalReviews.set(id, updated);
    return updated;
  }
}

export const storage = new MemStorage();