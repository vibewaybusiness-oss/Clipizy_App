"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Music, AlertCircle, CheckCircle, Loader2 } from "lucide-react";

interface TestResult {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
}

export default function TestPage() {
  const [authToken, setAuthToken] = useState("");
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Test form state
  const [testPrompt, setTestPrompt] = useState("Create a happy upbeat pop song");
  const [isInstrumental, setIsInstrumental] = useState(false);

  // Get auth token from environment variable or localStorage on component mount
  React.useEffect(() => {
    console.log("🔧 TestPage: Component mounted");
    
    // First try environment variable
    const envToken = process.env.NEXT_PUBLIC_AUTH_TOKEN;
    if (envToken) {
      console.log("🔧 TestPage: Using token from environment variable");
      setAuthToken(envToken);
      return;
    }
    
    // Fallback to localStorage
    const token = localStorage.getItem('access_token');
    if (token) {
      console.log("🔧 TestPage: Using token from localStorage");
      setAuthToken(token);
    } else {
      console.log("🔧 TestPage: No token found");
    }
  }, []);

  const getBackendUrl = () => {
    const url = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    console.log("🔧 TestPage: Backend URL:", url);
    return url;
  };

  const testProducerAIGenerate = async () => {
    console.log("🎵 TestPage: Starting ProducerAI generation test");
    console.log("🎵 TestPage: Prompt:", testPrompt);
    console.log("🎵 TestPage: Is Instrumental:", isInstrumental);
    console.log("🎵 TestPage: Auth Token:", authToken ? "Available" : "Missing");
    
    setIsLoading(true);
    setTestResult(null);
    
    const payload = {
      prompt: testPrompt,
      title: "Test Song",
      is_instrumental: isInstrumental
    };

    console.log("🎵 TestPage: Request payload:", payload);

    try {
      const url = `${getBackendUrl()}/api/ai/producer/music-clip/generate`;
      console.log("🎵 TestPage: Making request to:", url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(payload)
      });

      console.log("🎵 TestPage: Response status:", response.status);
      console.log("🎵 TestPage: Response headers:", Object.fromEntries(response.headers.entries()));

      const data = await response.json();
      console.log("🎵 TestPage: Response data:", data);
      
      if (response.ok) {
        console.log("✅ TestPage: Generation successful");
        setTestResult({
          success: true,
          message: 'ProducerAI generation successful',
          data: data
        });
      } else {
        console.log("❌ TestPage: Generation failed");
        setTestResult({
          success: false,
          message: 'ProducerAI generation failed',
          error: data.detail || data.message || `HTTP ${response.status}`
        });
      }
    } catch (error) {
      console.log("❌ TestPage: Request error:", error);
      setTestResult({
        success: false,
        message: 'ProducerAI generation failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      console.log("🎵 TestPage: Request completed");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">🎵 ProducerAI Music Generation Test</h1>
          <p className="text-muted-foreground">
            Simple test interface for ProducerAI music generation with detailed console logging
          </p>
        </div>

        {/* Auth Token Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Authentication
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Auth Token</label>
              <Input
                type="password"
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
                placeholder="Enter your auth token or it will be loaded from environment variables"
                className="mt-1"
              />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="auto-load"
                checked={!!process.env.NEXT_PUBLIC_AUTH_TOKEN || (typeof window !== 'undefined' && !!window.localStorage?.getItem('access_token'))}
                disabled
              />
              <label htmlFor="auto-load" className="text-sm">
                {process.env.NEXT_PUBLIC_AUTH_TOKEN ? 'Auto-loaded from .env' : 'Auto-loaded from localStorage'}
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Test Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Music className="w-5 h-5" />
              Test Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Music Prompt</label>
              <Textarea
                value={testPrompt}
                onChange={(e) => setTestPrompt(e.target.value)}
                placeholder="Enter your music generation prompt"
                className="mt-1"
                rows={3}
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="instrumental"
                checked={isInstrumental}
                onCheckedChange={(checked) => setIsInstrumental(!!checked)}
              />
              <label htmlFor="instrumental" className="text-sm">
                Generate instrumental music (no lyrics)
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Generate Button */}
        <Card>
          <CardHeader>
            <CardTitle>Generate Music</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              onClick={testProducerAIGenerate}
              disabled={!authToken || isLoading}
              className="w-full bg-purple-600 hover:bg-purple-700"
              size="lg"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              {isLoading ? 'Generating Music...' : '🎵 Generate Music with ProducerAI'}
            </Button>
            <p className="text-sm text-muted-foreground mt-2 text-center">
              Check the browser console for detailed logs
            </p>
          </CardContent>
        </Card>

        {/* Test Result */}
        {testResult && (
          <Card>
            <CardHeader>
              <CardTitle>Test Result</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium">Generation Test</h3>
                  <Badge variant={testResult.success ? "default" : "destructive"}>
                    {testResult.success ? (
                      <><CheckCircle className="w-3 h-3 mr-1" /> Success</>
                    ) : (
                      <><AlertCircle className="w-3 h-3 mr-1" /> Failed</>
                    )}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground mb-2">{testResult.message}</p>
                {testResult.error && (
                  <p className="text-sm text-red-600 mb-2">Error: {testResult.error}</p>
                )}
                {testResult.data && (
                  <details className="text-xs">
                    <summary className="cursor-pointer text-muted-foreground">
                      View Response Data
                    </summary>
                    <pre className="mt-2 p-2 bg-muted rounded overflow-auto">
                      {JSON.stringify(testResult.data, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* API Status */}
        <Card>
          <CardHeader>
            <CardTitle>API Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div>
                <h3 className="font-medium">Backend Server</h3>
                <p className="text-sm text-muted-foreground">{getBackendUrl()}</p>
              </div>
              <div>
                <h3 className="font-medium">ProducerAI API</h3>
                <p className="text-sm text-muted-foreground">/api/ai/producer/music-clip/*</p>
              </div>
              <div>
                <h3 className="font-medium">Authentication</h3>
                <p className="text-sm text-muted-foreground">
                  {authToken ? 'Token Available' : 'No Token'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
