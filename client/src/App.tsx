import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { ThemeProvider } from "@/components/ThemeProvider";
import AppSidebar from "@/components/AppSidebar";
import ThemeToggle from "@/components/ThemeToggle";
import PatientChat from "@/pages/PatientChat";
import ExpertDashboardPage from "@/pages/ExpertDashboardPage";
import PatientSessions from "@/pages/PatientSessions";
import Settings from "@/pages/Settings";
import NotFound from "@/pages/not-found";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { UserCheck, Stethoscope } from "lucide-react";

function Router({ userRole }: { userRole: "patient" | "expert" }) {
  return (
    <Switch>
      <Route path="/" component={() => 
        userRole === "patient" ? <PatientChat /> : <ExpertDashboardPage />
      } />
      <Route path="/chat" component={PatientChat} />
      <Route path="/sessions" component={PatientSessions} />
      <Route path="/dashboard" component={ExpertDashboardPage} />
      <Route path="/cases" component={() => <ExpertDashboardPage />} />
      <Route path="/conversations" component={() => <ExpertDashboardPage />} />
      <Route path="/settings" component={Settings} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  const [userRole, setUserRole] = useState<"patient" | "expert">("expert");
  
  const sidebarStyle = {
    "--sidebar-width": "16rem",
    "--sidebar-width-icon": "3rem",
  };

  const toggleRole = () => {
    setUserRole(prev => prev === "patient" ? "expert" : "patient");
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <SidebarProvider style={sidebarStyle as React.CSSProperties}>
            <div className="flex h-screen w-full">
              <AppSidebar 
                userRole={userRole} 
                userName={userRole === "patient" ? "Sarah Johnson" : "Dr. Sarah Wilson"}
              />
              <div className="flex flex-col flex-1">
                <header className="flex items-center justify-between p-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                  <div className="flex items-center gap-4">
                    <SidebarTrigger data-testid="button-sidebar-toggle" />
                    <div className="flex items-center gap-2">
                      <h2 className="font-semibold text-sm text-muted-foreground">PsyAI Demo</h2>
                      <div className="h-4 w-px bg-border" />
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={toggleRole}
                        data-testid="button-toggle-role"
                        className="h-7 px-2 text-xs"
                      >
                        {userRole === "patient" ? (
                          <>
                            <Stethoscope className="h-3 w-3 mr-1" />
                            Switch to Expert
                          </>
                        ) : (
                          <>
                            <UserCheck className="h-3 w-3 mr-1" />
                            Switch to Patient
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                  <ThemeToggle />
                </header>
                <main className="flex-1 overflow-auto p-6">
                  <Router userRole={userRole} />
                </main>
              </div>
            </div>
          </SidebarProvider>
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
