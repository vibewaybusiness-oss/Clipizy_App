"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/ui/use-toast';
import { Loader2, Copy, Check, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface PromptResult {
  promptType: string;
  originalPrompt: string;
  sentToLLM: string;
  generatedPrompt: string;
  scenePlanningResult?: string; // For multi-scene videos: the initial scene planning result
  timestamp: string;
  success: boolean;
  error?: string;
  status: 'waiting' | 'completed' | 'error';
  // For image/video generation results
  generatedImage?: string;
  generatedVideo?: string;
  outputPath?: string;
}

export default function TestPromptGenerationPage() {
  const [userInput, setUserInput] = useState('A beautiful sunset over a mountain landscape with birds flying');
  const [style, setStyle] = useState('none');
  const [numScenes, setNumScenes] = useState(3);
  const [projectId, setProjectId] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [results, setResults] = useState<PromptResult[]>([]);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>("");
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const { toast } = useToast();

  const generateUUID = () => {
    return crypto.randomUUID();
  };

  const isValidUUID = (uuid: string): boolean => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
  };

  const promptTypes = [
    { value: 'image', label: 'Image (Static Loop)', description: 'Generate image prompt for static looped video' },
    { value: 'video', label: 'Video (Animated Loop)', description: 'Generate video prompt for animated looped video' },
    { value: 'video-scenes', label: 'Video (Multiple Scenes)', description: 'Generate video prompts for multiple scenes' },
    { value: 'text-to-image', label: 'Text-to-Image', description: 'Generate image from text prompt using Qwen' },
    { value: 'image-to-image', label: 'Image-to-Image', description: 'Transform image using text prompt' },
    { value: 'image-to-video', label: 'Image-to-Video', description: 'Generate video from image using WAN' },
    { value: 'image-description', label: 'Image Description', description: 'Generate detailed description from reference image using vision LLM' },
  ];

  const styles = [
    { value: 'none', label: 'None' },
    { value: 'modern', label: 'Modern' },
    { value: 'vintage', label: 'Vintage' },
    { value: 'minimalist', label: 'Minimalist' },
    { value: 'cinematic', label: 'Cinematic' },
  ];

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const uploadImageToBackend = async (file: File, projectType: string = 'music-clip'): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_type', projectType);
    
    const token = localStorage.getItem('access_token');
    const response = await fetch(`/api/storage/projects/${projectId}/files/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to upload image: ${response.status} ${errorText}`);
    }

    const result = await response.json();
    // Backend returns standard response with data.key (S3 key) and optionally data.presigned_url
    const key = result?.data?.key;
    if (!key) {
      throw new Error('Upload succeeded but no file key returned');
    }
    return key;
  };

  const generatePrompt = async (promptType: string, isLooped: boolean = false) => {
    setIsGenerating(true);
    const timestamp = new Date().toLocaleTimeString();
    
    // Build the prompt that will be sent
    const sentToLLM = promptType === 'image-description' 
      ? 'Vision LLM prompt: Analyze and describe reference image'
      : userInput + (style !== 'none' ? `\n\nStyle: ${style}` : '');
    
    // Create waiting result immediately
    const waitingResult: PromptResult = {
      promptType: promptType,
      originalPrompt: promptType === 'image-description' ? 'Image description generation' : userInput,
      sentToLLM: sentToLLM,
      generatedPrompt: '',
      timestamp,
      success: false,
      status: 'waiting',
    };

    setResults(prev => [waitingResult, ...prev]);
    
    try {
      // Get the auth token from localStorage
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No authentication token found. Please log in.');
      }

      let endpoint: string;
      let requestBody: any;

      // Handle different test types
      if (promptType === 'video-scenes') {
        endpoint = '/api/v1/integrations/ai-providers/llm/create_dynamic_scenes_script';
        requestBody = {
          prompt: userInput,
          numScenes: numScenes,
          style: style === 'none' ? '' : style,
          promptType: 'video'
        };
      } else if (promptType === 'text-to-image') {
        endpoint = '/api/v1/integrations/ai-providers/text-to-image';
        requestBody = {
          prompt: userInput,
          width: 1328,
          height: 1328,
          negative_prompt: style === 'none' ? '' : `Not ${style} style`
        };
      } else if (promptType === 'image-to-image') {
        if (!uploadedImage) {
          throw new Error('Please upload an image for image-to-image generation');
        }
        if (!projectId || !isValidUUID(projectId)) {
          throw new Error('Valid Project ID (UUID) is required for image upload');
        }
        const imagePath = await uploadImageToBackend(uploadedImage);
        endpoint = '/api/v1/integrations/ai-providers/image-to-image';
        requestBody = {
          prompt: userInput,
          reference_image_path: imagePath,
          width: 1328,
          height: 1328,
          negative_prompt: style === 'none' ? '' : `Not ${style} style`
        };
      } else if (promptType === 'image-to-video') {
        if (!uploadedImage) {
          throw new Error('Please upload an image for image-to-video generation');
        }
        if (!projectId || !isValidUUID(projectId)) {
          throw new Error('Valid Project ID (UUID) is required for image upload');
        }
        const imagePath = await uploadImageToBackend(uploadedImage);
        endpoint = '/api/v1/integrations/ai-providers/image-to-video';
        requestBody = {
          prompt: userInput,
          input_image_path: imagePath,
          width: 1280,
          height: 720,
          num_frames: 81,
          frame_rate: 16,
          negative_prompt: style === 'none' ? '' : `Not ${style} style`
        };
      } else if (promptType === 'image-description') {
        if (!uploadedImage) {
          throw new Error('Please upload an image to generate description');
        }
        if (!projectId) {
          throw new Error('Project ID (UUID) is required for image description generation');
        }
        if (!isValidUUID(projectId)) {
          throw new Error('Invalid UUID format. Please enter a valid UUID or generate one.');
        }
        await uploadImageToBackend(uploadedImage, 'music-clip');
        endpoint = '/api/ai/generate-image-description';
        requestBody = {
          project_id: projectId
        };
      } else {
        // Original LLM prompt generation
        endpoint = '/api/v1/integrations/ai-providers/llm';
        requestBody = {
          prompt: userInput,
          projectId,
          promptType: promptType,
          style: style === 'none' ? '' : style,
          isLooped: isLooped,
          numScenes: undefined,
        };
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`HTTP ${response.status}: ${errorData.detail || errorData.error || response.statusText}`);
      }

      const result = await response.json();
      
      // Capture debug information
      const debugData = {
        requestData: {
          prompt: userInput,
          projectId,
          promptType: promptType === 'video-scenes' ? 'video' : promptType,
          style: style === 'none' ? '' : style,
          isLooped: promptType === 'video-scenes' ? false : isLooped,
          numScenes: promptType === 'video-scenes' ? numScenes : undefined,
          uploadedImage: uploadedImage ? uploadedImage.name : undefined,
        },
        responseData: result,
        timestamp: new Date().toISOString()
      };
      
      setDebugInfo(JSON.stringify(debugData, null, 2));
      
      // Update the waiting result with success
      const successResult: PromptResult = {
        promptType: promptType,
        originalPrompt: userInput,
        sentToLLM: sentToLLM,
        generatedPrompt: promptType === 'image-description' 
          ? result.description || result.generated_prompt || 'Description generated'
          : result.generated_prompt || result.generatedPrompt || result.output_path || 'Generation completed',
        scenePlanningResult: result.scene_planning_result || result.scenePlanningResult || undefined,
        generatedImage: result.output_path || result.image_path,
        generatedVideo: result.output_path || result.video_path,
        outputPath: result.output_path,
        timestamp,
        success: true,
        status: 'completed',
      };

      setResults(prev => [successResult, ...prev.slice(1)]);
      
      toast({
        title: "Generation Completed Successfully",
        description: `Generated ${promptType} using AI services`,
      });

    } catch (error: any) {
      // Update the waiting result with error
      const errorResult: PromptResult = {
        promptType: promptType,
        originalPrompt: userInput,
        sentToLLM: sentToLLM,
        generatedPrompt: '',
        timestamp,
        success: false,
        error: error.message,
        status: 'error',
      };

      setResults(prev => [errorResult, ...prev.slice(1)]);
      
      toast({
        variant: "destructive",
        title: "Generation Failed",
        description: error.message,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
      toast({
        title: "Copied to Clipboard",
        description: "Prompt copied successfully",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Copy Failed",
        description: "Failed to copy to clipboard",
      });
    }
  };

  const clearResults = () => {
    setResults([]);
  };

  const testApiConnection = async () => {
    try {
      // Get the auth token from localStorage
      const token = localStorage.getItem('access_token');
      if (!token) {
        toast({
          variant: "destructive",
          title: "Authentication Required",
          description: "Please log in to test the API",
        });
        return;
      }

        // Test the LLM route with authentication
        const response = await fetch('/api/v1/integrations/ai-providers/llm', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        toast({
          title: "API Connection Test",
          description: `✅ LLM API is working! Backend: ${data.backendUrl}`,
        });
      } else {
        const errorData = await response.json();
        toast({
          variant: "destructive",
          title: "API Connection Test",
          description: `❌ LLM API returned ${response.status}: ${errorData.detail || 'Unknown error'}`,
        });
      }
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "API Connection Test",
        description: `❌ Connection failed: ${error.message}`,
      });
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <Link href="/dashboard">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
        </div>
        <h1 className="text-3xl font-bold mb-2">AI Generation Test Suite</h1>
        <p className="text-muted-foreground">
          Test various AI generation capabilities including LLM prompts, text-to-image, image-to-image, image-to-video, and image description generation.
          <br />
          <strong>Note:</strong> This test requires authentication and will use your logged-in account.
          <br />
          <strong>Timeout:</strong> AI generation requests may take up to 10 minutes due to pod allocation and processing time.
          <br />
          <strong>Image Description:</strong> Uploads image as reference type and generates detailed description using vision LLM (qwen3-vl).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <Card>
          <CardHeader>
            <CardTitle>Test Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="userInput">User Input Prompt</Label>
              <Textarea
                id="userInput"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Enter your prompt here..."
                className="min-h-[100px]"
              />
            </div>

            <div>
              <Label htmlFor="style">Style</Label>
              <Select value={style} onValueChange={setStyle}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a style" />
                </SelectTrigger>
                <SelectContent>
                  {styles.map((s) => (
                    <SelectItem key={s.value} value={s.value}>
                      {s.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="numScenes">Number of Scenes (for Multi-Scene Video)</Label>
              <Input
                id="numScenes"
                type="number"
                min="1"
                max="10"
                value={numScenes}
                onChange={(e) => setNumScenes(parseInt(e.target.value) || 3)}
                placeholder="Number of scenes"
              />
            </div>

            <div>
              <Label htmlFor="projectId">Project ID (UUID)</Label>
              <div className="flex gap-2">
                <Input
                  id="projectId"
                  value={projectId}
                  onChange={(e) => setProjectId(e.target.value)}
                  placeholder="Enter UUID (e.g., 123e4567-e89b-12d3-a456-426614174000)"
                  className={projectId && !isValidUUID(projectId) ? 'border-red-500' : ''}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setProjectId(generateUUID())}
                  title="Generate new UUID"
                >
                  Generate
                </Button>
              </div>
              {projectId && !isValidUUID(projectId) && (
                <p className="text-sm text-red-500 mt-1">Invalid UUID format</p>
              )}
              {!projectId && (
                <p className="text-sm text-muted-foreground mt-1">
                  A valid UUID is required for file uploads. Click "Generate" to create one.
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="imageUpload">Upload Image (for Image-to-Image, Image-to-Video, and Image Description)</Label>
              <Input
                id="imageUpload"
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="cursor-pointer"
              />
              {imagePreview && (
                <div className="mt-2">
                  <img 
                    src={imagePreview} 
                    alt="Preview" 
                    className="max-w-xs max-h-48 object-contain border rounded"
                  />
                </div>
              )}
            </div>

            {uploadedImage && projectId && isValidUUID(projectId) && (
              <div className="space-y-2 mb-4 p-4 border border-blue-200 rounded-lg bg-blue-50">
                <h3 className="font-semibold text-blue-900">Step-by-Step Testing (Image Description)</h3>
                <div className="space-y-2">
                  <Button
                    onClick={async () => {
                      try {
                        setIsGenerating(true);
                        const token = localStorage.getItem('access_token');
                        const response = await fetch('/api/ai/test-image-s3-url', {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`,
                          },
                          body: JSON.stringify({ project_id: projectId }),
                        });
                        const result = await response.json();
                        if (result.success) {
                          toast({
                            title: "Step 1: S3 URL Generated",
                            description: `URL length: ${result.url_length} chars. Check console for details.`,
                          });
                          console.log('Step 1 Result:', result);
                          // Store for next step
                          (window as any).testImageUrl = result.presigned_url;
                        } else {
                          throw new Error(result.error?.message || 'Failed');
                        }
                      } catch (error: any) {
                        toast({
                          variant: "destructive",
                          title: "Step 1 Failed",
                          description: error.message,
                        });
                      } finally {
                        setIsGenerating(false);
                      }
                    }}
                    disabled={isGenerating}
                    size="sm"
                    variant="outline"
                    className="w-full"
                  >
                    Test Step 1: Generate S3 URL
                  </Button>
                  <Button
                    onClick={async () => {
                      try {
                        setIsGenerating(true);
                        const imageUrl = (window as any).testImageUrl;
                        if (!imageUrl) {
                          toast({
                            variant: "destructive",
                            title: "No Image URL",
                            description: "Run Step 1 first to generate S3 URL",
                          });
                          return;
                        }
                        const token = localStorage.getItem('access_token');
                        const response = await fetch('/api/ai/test-base64-conversion', {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`,
                          },
                          body: JSON.stringify({ image_url: imageUrl }),
                        });
                        const result = await response.json();
                        if (result.success) {
                          toast({
                            title: "Step 2: Base64 Conversion",
                            description: `Base64 length: ${result.result.base64_length} chars. Check console for details.`,
                          });
                          console.log('Step 2 Result:', result);
                        } else {
                          throw new Error(result.error?.message || 'Failed');
                        }
                      } catch (error: any) {
                        toast({
                          variant: "destructive",
                          title: "Step 2 Failed",
                          description: error.message,
                        });
                      } finally {
                        setIsGenerating(false);
                      }
                    }}
                    disabled={isGenerating}
                    size="sm"
                    variant="outline"
                    className="w-full"
                  >
                    Test Step 2: Convert to Base64
                  </Button>
                  <Button
                    onClick={async () => {
                      try {
                        setIsGenerating(true);
                        const imageUrl = (window as any).testImageUrl;
                        if (!imageUrl) {
                          toast({
                            variant: "destructive",
                            title: "No Image URL",
                            description: "Run Step 1 first to generate S3 URL",
                          });
                          return;
                        }
                        const token = localStorage.getItem('access_token');
                        const response = await fetch('/api/ai/test-llm-call', {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`,
                          },
                          body: JSON.stringify({ 
                            image_url: imageUrl,
                            prompt: "Describe this image in detail.",
                            model: "qwen3-vl",
                            use_queue: false
                          }),
                        });
                        
                        // Handle response - check if it's JSON
                        let result;
                        const contentType = response.headers.get('content-type');
                        if (contentType && contentType.includes('application/json')) {
                          const text = await response.text();
                          try {
                            result = JSON.parse(text);
                          } catch (parseError: any) {
                            console.error('Failed to parse JSON:', text.substring(0, 200));
                            throw new Error(`Invalid JSON response: ${parseError.message}. Response preview: ${text.substring(0, 200)}`);
                          }
                        } else {
                          const text = await response.text();
                          throw new Error(`Expected JSON but got ${contentType || 'unknown type'}. Response: ${text.substring(0, 200)}`);
                        }
                        if (result.success) {
                          toast({
                            title: "Step 3a: LLM Call Success (Direct)",
                            description: `Response length: ${result.response_length} chars. Check console for details.`,
                          });
                          console.log('Step 3a Result (Direct):', result);
                        } else {
                          const errorMsg = result.error?.message || 'Failed';
                          const podInfo = result.pod_health ? `\nPod accessible: ${result.pod_health.accessible}` : '';
                          throw new Error(errorMsg + podInfo);
                        }
                      } catch (error: any) {
                        toast({
                          variant: "destructive",
                          title: "Step 3a Failed",
                          description: error.message,
                        });
                        console.error('Step 3a Error:', error);
                      } finally {
                        setIsGenerating(false);
                      }
                    }}
                    disabled={isGenerating}
                    size="sm"
                    variant="outline"
                    className="w-full"
                  >
                    Test Step 3a: LLM Call (Direct - Bypasses Queue)
                  </Button>
                  <Button
                    onClick={async () => {
                      try {
                        setIsGenerating(true);
                        const imageUrl = (window as any).testImageUrl;
                        if (!imageUrl) {
                          toast({
                            variant: "destructive",
                            title: "No Image URL",
                            description: "Run Step 1 first to generate S3 URL",
                          });
                          return;
                        }
                        const token = localStorage.getItem('access_token');
                        const response = await fetch('/api/ai/test-llm-call', {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`,
                          },
                          body: JSON.stringify({ 
                            image_url: imageUrl,
                            prompt: "Describe this image in detail.",
                            model: "qwen3-vl",
                            use_queue: true
                          }),
                        });
                        
                        // Handle response - check if it's JSON
                        let result;
                        const contentType = response.headers.get('content-type');
                        if (contentType && contentType.includes('application/json')) {
                          result = await response.json();
                        } else {
                          // Try to parse as JSON anyway, but if it fails, get text
                          const text = await response.text();
                          try {
                            result = JSON.parse(text);
                          } catch (parseError) {
                            throw new Error(`Server returned non-JSON response: ${text.substring(0, 200)}`);
                          }
                        }
                        
                        if (!response.ok) {
                          const errorMsg = result?.error?.message || result?.error || `HTTP ${response.status}`;
                          const podInfo = result?.pod_health ? `\nPod accessible: ${result.pod_health.accessible}` : '';
                          throw new Error(errorMsg + podInfo);
                        }
                        
                        if (result.success) {
                          toast({
                            title: "Step 3b: LLM Call Success (Queue)",
                            description: `Response length: ${result.response_length} chars. Uses queue system.`,
                          });
                          console.log('Step 3b Result (Queue):', result);
                        } else {
                          const errorMsg = result.error?.message || result.error || 'Failed';
                          const podInfo = result.pod_health ? `\nPod accessible: ${result.pod_health.accessible}` : '';
                          throw new Error(errorMsg + podInfo);
                        }
                      } catch (error: any) {
                        toast({
                          variant: "destructive",
                          title: "Step 3b Failed",
                          description: error.message || 'Unknown error occurred',
                        });
                        console.error('Step 3b Error:', error);
                      } finally {
                        setIsGenerating(false);
                      }
                    }}
                    disabled={isGenerating}
                    size="sm"
                    variant="outline"
                    className="w-full"
                  >
                    Test Step 3b: LLM Call (Queue System - Recommended)
                  </Button>
                </div>
              </div>
            )}

            <div className="space-y-3">
              <h3 className="font-semibold">AI Generation Tests</h3>
              {promptTypes.map((type) => (
                <div key={type.value} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{type.label}</div>
                    <div className="text-sm text-muted-foreground">{type.description}</div>
                  </div>
                  <Button
                    onClick={() => generatePrompt(type.value, type.value !== 'video-scenes')}
                    disabled={
                      isGenerating || 
                      (type.value !== 'image-description' && !userInput.trim()) || 
                      (type.value === 'image-description' && (!uploadedImage || !projectId || !isValidUUID(projectId))) ||
                      ((type.value === 'image-to-image' || type.value === 'image-to-video') && (!projectId || !isValidUUID(projectId)))
                    }
                    size="sm"
                  >
                    {isGenerating ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      'Generate'
                    )}
                  </Button>
                </div>
              ))}
            </div>

            <div className="space-y-2">
              <Button onClick={testApiConnection} variant="secondary" className="w-full">
                Test API Connection
              </Button>
              {results.length > 0 && (
                <Button onClick={clearResults} variant="outline" className="w-full">
                  Clear Results
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardHeader>
            <CardTitle>Generated Prompts</CardTitle>
            <p className="text-sm text-muted-foreground">
              {results.length} result{results.length !== 1 ? 's' : ''} generated
            </p>
          </CardHeader>
          <CardContent>
            {results.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No prompts generated yet. Click a generate button to start testing.
              </div>
            ) : (
              <div className="space-y-4 max-h-[600px] overflow-y-auto">
                {results.map((result, index) => (
                  <div
                    key={index}
                    className={`p-4 border rounded-lg ${
                      result.status === 'waiting' 
                        ? 'border-yellow-200 bg-yellow-50' 
                        : result.success 
                          ? 'border-green-200 bg-green-50' 
                          : 'border-red-200 bg-red-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge variant={
                          result.status === 'waiting' 
                            ? 'secondary' 
                            : result.success 
                              ? 'default' 
                              : 'destructive'
                        }>
                          {result.promptType}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {result.status === 'waiting' ? '⏳ Waiting' : 
                           result.status === 'completed' ? '✅ Completed' : '❌ Error'}
                        </Badge>
                        <span className="text-sm text-muted-foreground">{result.timestamp}</span>
                      </div>
                      {result.success && result.generatedPrompt && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => copyToClipboard(result.generatedPrompt, index)}
                        >
                          {copiedIndex === index ? (
                            <Check className="h-4 w-4" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                      )}
                    </div>
                    
                    {result.status === 'waiting' ? (
                      <div className="space-y-2">
                        <div className="text-sm font-medium text-yellow-700">
                          {result.promptType === 'image-description' 
                            ? '⏳ Waiting for Vision LLM (qwen3-vl) to analyze image...'
                            : '⏳ Waiting for LLM (qwen-omni)...'}
                        </div>
                        {result.promptType === 'image-description' && imagePreview && (
                          <div className="p-3 bg-white border rounded">
                            <div className="text-sm font-medium text-gray-700 mb-2">Analyzing Image:</div>
                            <img 
                              src={imagePreview} 
                              alt="Image being analyzed" 
                              className="max-w-xs max-h-48 object-contain border rounded"
                            />
                          </div>
                        )}
                        <div className="p-3 bg-white border rounded text-sm">
                          <div className="mb-2">
                            <div className="font-medium text-gray-700">Original Prompt:</div>
                            <div className="text-gray-600 whitespace-pre-wrap">{result.originalPrompt || (result.promptType === 'image-description' ? 'Image description generation' : result.originalPrompt)}</div>
                          </div>
                          {result.promptType !== 'image-description' && (
                            <div>
                              <div className="font-medium text-gray-700">Sent to LLM (qwen-omni):</div>
                              <div className="text-gray-600 whitespace-pre-wrap">{result.sentToLLM}</div>
                            </div>
                          )}
                        </div>
                      </div>
                    ) : result.success ? (
                      <div className="space-y-3">
                        <div className="text-sm font-medium text-green-700">✅ Generation Completed:</div>
                        
                        {/* Show generated image */}
                        {result.generatedImage && (
                          <div className="space-y-2">
                            <div className="text-sm font-medium text-blue-700">🖼️ Generated Image:</div>
                            <div className="p-3 bg-blue-50 border border-blue-200 rounded">
                              <img 
                                src={result.generatedImage} 
                                alt="Generated" 
                                className="max-w-full max-h-64 object-contain"
                              />
                            </div>
                          </div>
                        )}
                        
                        {/* Show generated video */}
                        {result.generatedVideo && (
                          <div className="space-y-2">
                            <div className="text-sm font-medium text-purple-700">🎬 Generated Video:</div>
                            <div className="p-3 bg-purple-50 border border-purple-200 rounded">
                              <video 
                                src={result.generatedVideo} 
                                controls 
                                className="max-w-full max-h-64"
                              />
                            </div>
                          </div>
                        )}
                        
                        {/* Show text result */}
                        {result.generatedPrompt && (
                          <div className="p-3 bg-white border rounded text-sm whitespace-pre-wrap">
                            {result.generatedPrompt}
                          </div>
                        )}
                        
                        {/* Show scene planning result for multi-scene videos */}
                        {result.scenePlanningResult && (
                          <div className="space-y-2">
                              <div className="text-sm font-medium text-blue-700">🎬 Scene Planning (First LLM Call):</div>
                            <div className="p-3 bg-blue-50 border border-blue-200 rounded text-sm whitespace-pre-wrap">
                              {result.scenePlanningResult}
                            </div>
                          </div>
                        )}
                        
                        <details className="text-xs">
                          <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                            Show prompt details
                          </summary>
                          <div className="mt-2 space-y-2">
                            <div>
                              <div className="font-medium text-gray-700">Original Prompt:</div>
                              <div className="text-gray-600 whitespace-pre-wrap">{result.originalPrompt}</div>
                            </div>
                            <div>
                              <div className="font-medium text-gray-700">Sent to LLM (qwen-omni):</div>
                              <div className="text-gray-600 whitespace-pre-wrap">{result.sentToLLM}</div>
                            </div>
                          </div>
                        </details>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <div className="text-sm font-medium text-red-700">❌ Error:</div>
                        <div className="p-3 bg-white border rounded text-sm text-red-600">
                          {result.error}
                        </div>
                        <details className="text-xs">
                          <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
                            Show prompt details
                          </summary>
                          <div className="mt-2 space-y-2">
                            <div>
                              <div className="font-medium text-gray-700">Original Prompt:</div>
                              <div className="text-gray-600 whitespace-pre-wrap">{result.originalPrompt}</div>
                            </div>
                            <div>
                              <div className="font-medium text-gray-700">Sent to LLM (qwen-omni):</div>
                              <div className="text-gray-600 whitespace-pre-wrap">{result.sentToLLM}</div>
                            </div>
                          </div>
                        </details>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Debug Information */}
      {debugInfo && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Debug Information</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-100 p-4 rounded text-xs overflow-auto max-h-96">
              {debugInfo}
            </pre>
          </CardContent>
        </Card>
      )}

      {/* API Status */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>API Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
             <div>
               <div className="font-medium">Frontend API Route</div>
               <div className="text-muted-foreground">/api/v1/integrations/ai-providers/llm</div>
             </div>
             <div>
               <div className="font-medium">Backend Endpoint</div>
               <div className="text-muted-foreground">/api/v1/integrations/ai-providers/llm</div>
             </div>
            <div>
              <div className="font-medium">Authentication</div>
              <div className="text-muted-foreground">Bearer Token Required</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
