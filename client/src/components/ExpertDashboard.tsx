import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AlertTriangle, CheckCircle, Clock, Search, Filter, TrendingDown } from "lucide-react";
import ConversationCard, { type ConversationCardProps } from "./ConversationCard";
import { cn } from "@/lib/utils";

export interface ExpertDashboardProps {
  expertName?: string;
  conversations?: ConversationCardProps[];
  onViewConversation?: (id: string) => void;
  onReviewConversation?: (id: string) => void;
  className?: string;
}

export default function ExpertDashboard({
  expertName = "Dr. Sarah Wilson",
  conversations = [],
  onViewConversation,
  onReviewConversation,
  className,
}: ExpertDashboardProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState("by-confidence");

  // Filter and sort conversations based on search and tab
  const getFilteredConversations = () => {
    let filtered = conversations.filter(conv => {
      const matchesSearch = conv.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           conv.patientName.toLowerCase().includes(searchQuery.toLowerCase());
      
      switch (activeTab) {
        case "pending":
          return matchesSearch && (conv.status === "pending_review" || conv.needsExpertReview);
        case "active":
          return matchesSearch && conv.status === "active";
        case "reviewed":
          return matchesSearch && conv.status === "reviewed";
        case "by-confidence":
          return matchesSearch; // Show all for confidence ranking
        default:
          return matchesSearch;
      }
    });

    // Sort by confidence score if in confidence tab (lowest first)
    if (activeTab === "by-confidence") {
      filtered = filtered.sort((a, b) => (a.confidenceScore || 100) - (b.confidenceScore || 100));
    }

    return filtered;
  };

  const filteredConversations = getFilteredConversations();

  // Get counts for each tab
  const getCounts = () => {
    const pending = conversations.filter(c => c.status === "pending_review" || c.needsExpertReview).length;
    const active = conversations.filter(c => c.status === "active").length;
    const reviewed = conversations.filter(c => c.status === "reviewed").length;
    return { pending, active, reviewed };
  };

  const counts = getCounts();

  // Get priority conversations (low confidence or expert review needed)
  const priorityConversations = conversations.filter(c => c.confidenceScore < 60 || c.needsExpertReview);

  return (
    <div className={cn("space-y-6", className)} data-testid="expert-dashboard">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold" data-testid="dashboard-title">
              Expert Dashboard
            </h1>
            <p className="text-muted-foreground" data-testid="expert-name">
              Welcome back, {expertName}
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" data-testid="button-filter">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-warning/10 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-warning" />
                </div>
                <div>
                  <p className="text-2xl font-bold" data-testid="stat-pending">{counts.pending}</p>
                  <p className="text-xs text-muted-foreground">Pending Review</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-chart-1/10 rounded-lg">
                  <Clock className="h-5 w-5 text-chart-1" />
                </div>
                <div>
                  <p className="text-2xl font-bold" data-testid="stat-active">{counts.active}</p>
                  <p className="text-xs text-muted-foreground">Active Cases</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-success/10 rounded-lg">
                  <CheckCircle className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="text-2xl font-bold" data-testid="stat-reviewed">{counts.reviewed}</p>
                  <p className="text-xs text-muted-foreground">Reviewed</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-destructive/10 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-destructive" />
                </div>
                <div>
                  <p className="text-2xl font-bold" data-testid="stat-priority">{priorityConversations.length}</p>
                  <p className="text-xs text-muted-foreground">High Priority</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search conversations or patients..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
          data-testid="input-search"
        />
      </div>

      {/* Conversation Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="by-confidence" className="relative" data-testid="tab-by-confidence">
            <TrendingDown className="h-4 w-4 mr-1" />
            By Confidence
          </TabsTrigger>
          <TabsTrigger value="pending" className="relative" data-testid="tab-pending">
            Pending Review
            {counts.pending > 0 && (
              <Badge variant="destructive" className="ml-2 h-5 w-5 p-0 text-xs">
                {counts.pending}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="active" data-testid="tab-active">
            Active ({counts.active})
          </TabsTrigger>
          <TabsTrigger value="reviewed" data-testid="tab-reviewed">
            Reviewed ({counts.reviewed})
          </TabsTrigger>
          <TabsTrigger value="all" data-testid="tab-all">
            All ({conversations.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-6">
          {activeTab === "by-confidence" && (
            <div className="mb-4 p-3 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Cases ranked by confidence score (lowest first). Cases below 90% require expert review.
                </p>
              </div>
            </div>
          )}
          <ScrollArea className="h-[600px]" data-testid="conversations-scroll">
            <div className="space-y-4 pr-4">
              {filteredConversations.length === 0 ? (
                <div className="text-center py-12">
                  <Clock className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-medium">No conversations found</h3>
                  <p className="text-muted-foreground mt-2">
                    {searchQuery ? "Try adjusting your search criteria" : "No conversations match this filter"}
                  </p>
                </div>
              ) : (
                filteredConversations.map((conversation) => (
                  <ConversationCard
                    key={conversation.id}
                    {...conversation}
                    onView={() => onViewConversation?.(conversation.id)}
                    onReview={() => onReviewConversation?.(conversation.id)}
                  />
                ))
              )}
            </div>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  );
}