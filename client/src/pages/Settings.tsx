import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Settings as SettingsIcon, Bell, Shield, Moon } from "lucide-react";

export default function Settings() {
  return (
    <div className="space-y-6" data-testid="settings-page">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2" data-testid="settings-title">
          <SettingsIcon className="h-6 w-6" />
          Settings
        </h1>
        <p className="text-muted-foreground mt-1">
          Manage your preferences and account settings
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="email-notifications" className="text-sm">Email Notifications</Label>
              <Switch id="email-notifications" data-testid="switch-email-notifications" />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="session-reminders" className="text-sm">Session Reminders</Label>
              <Switch id="session-reminders" data-testid="switch-session-reminders" />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="expert-updates" className="text-sm">Expert Updates</Label>
              <Switch id="expert-updates" data-testid="switch-expert-updates" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Privacy & Security
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="data-sharing" className="text-sm">Anonymous Data Sharing</Label>
              <Switch id="data-sharing" data-testid="switch-data-sharing" />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="two-factor" className="text-sm">Two-Factor Authentication</Label>
              <Switch id="two-factor" data-testid="switch-two-factor" />
            </div>
            <Button variant="outline" size="sm" className="w-full mt-4">
              Download My Data
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Moon className="h-4 w-4" />
              Appearance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="dark-mode" className="text-sm">Dark Mode</Label>
              <Switch id="dark-mode" data-testid="switch-dark-mode" />
            </div>
            <div className="space-y-2">
              <Label className="text-sm">Theme Color</Label>
              <div className="flex gap-2">
                <div className="w-6 h-6 bg-blue-500 rounded-full cursor-pointer border-2 border-white shadow-md" data-testid="color-blue"></div>
                <div className="w-6 h-6 bg-green-500 rounded-full cursor-pointer border-2 border-white shadow-md" data-testid="color-green"></div>
                <div className="w-6 h-6 bg-purple-500 rounded-full cursor-pointer border-2 border-white shadow-md" data-testid="color-purple"></div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Account</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label className="text-sm">Current Plan</Label>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Professional</span>
                <Button variant="outline" size="sm">
                  Upgrade
                </Button>
              </div>
            </div>
            <div className="pt-4 border-t">
              <Button variant="destructive" size="sm" className="w-full">
                Delete Account
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}