import AppSidebar from '../AppSidebar';
import { SidebarProvider } from '@/components/ui/sidebar';

export default function AppSidebarExample() {
  const style = {
    "--sidebar-width": "16rem",
    "--sidebar-width-icon": "3rem",
  };

  return (
    <SidebarProvider style={style as React.CSSProperties}>
      <div className="flex h-screen w-full">
        <AppSidebar userRole="expert" userName="Dr. Sarah Wilson" />
        <main className="flex-1 p-6 overflow-auto">
          <div className="max-w-2xl">
            <h2 className="text-2xl font-bold mb-4">Expert Sidebar Demo</h2>
            <p className="text-muted-foreground mb-6">
              This shows the expert view of the sidebar with dashboard access and case management.
            </p>
            
            <div className="space-y-4">
              <div className="p-4 border rounded-lg">
                <h3 className="font-medium mb-2">Expert Features:</h3>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Dashboard with pending reviews (3)</li>
                  <li>• Patient case management</li>
                  <li>• AI conversation monitoring (12 active)</li>
                  <li>• Settings and profile management</li>
                </ul>
              </div>
              
              <div className="p-4 border rounded-lg">
                <h3 className="font-medium mb-2">Patient View:</h3>
                <p className="text-sm text-muted-foreground">
                  Switch to patient role to see the simplified interface with chat access and session history.
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}