"use client";

import React, { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/ui/use-toast';
import { Send, Loader2, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

// =========================
// CONTACT FORM SCHEMA
// =========================

const contactFormSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  subject: z.string().min(5, 'Subject must be at least 5 characters'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
  topic: z.string().min(1, 'Please select a topic'),
  priority: z.enum(['low', 'medium', 'high']).optional()
});

type ContactFormData = z.infer<typeof contactFormSchema>;

// =========================
// CONTACT FORM PROPS
// =========================

interface ContactFormProps {
  onSubmit?: (data: ContactFormData) => Promise<void>;
  className?: string;
  showTopic?: boolean;
  showPriority?: boolean;
  defaultTopic?: string;
  topics?: Array<{ value: string; label: string; description?: string }>;
}

// =========================
// DEFAULT TOPICS
// =========================

const DEFAULT_TOPICS = [
  {
    value: 'general',
    label: 'General Support',
    description: 'Questions about features, billing, or account issues'
  },
  {
    value: 'technical',
    label: 'Technical Support',
    description: 'Help with technical issues or bug reports'
  },
  {
    value: 'enterprise',
    label: 'Enterprise Sales',
    description: 'Custom solutions for teams and organizations'
  },
  {
    value: 'feature',
    label: 'Feature Requests',
    description: 'Suggest new features or improvements'
  },
  {
    value: 'billing',
    label: 'Billing & Payments',
    description: 'Questions about pricing, payments, or refunds'
  }
];

// =========================
// CONTACT FORM COMPONENT
// =========================

export function ContactForm({
  onSubmit,
  className,
  showTopic = true,
  showPriority = false,
  defaultTopic = 'general',
  topics = DEFAULT_TOPICS
}: ContactFormProps) {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
    setValue,
    watch
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactFormSchema),
    defaultValues: {
      topic: defaultTopic,
      priority: 'medium'
    },
    mode: 'onChange'
  });

  const watchedTopic = watch('topic');
  const selectedTopic = topics.find(topic => topic.value === watchedTopic);

  const handleFormSubmit = useCallback(async (data: ContactFormData) => {
    try {
      setIsSubmitting(true);
      
      if (onSubmit) {
        await onSubmit(data);
      } else {
        // Default submission logic
        await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      }
      
      setIsSubmitted(true);
      reset();
      
      toast({
        title: "Message Sent!",
        description: "We'll get back to you within 24 hours.",
      });
      
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send message",
        variant: "destructive"
      });
    } finally {
      setIsSubmitting(false);
    }
  }, [onSubmit, reset, toast]);

  if (isSubmitted) {
    return (
      <Card className={cn("max-w-2xl mx-auto", className)}>
        <CardContent className="p-8 text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h3 className="text-2xl font-bold mb-2">Message Sent Successfully!</h3>
          <p className="text-muted-foreground mb-6">
            Thank you for contacting us. We'll get back to you within 24 hours.
          </p>
          <Button onClick={() => setIsSubmitted(false)} variant="outline">
            Send Another Message
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("max-w-2xl mx-auto", className)}>
      <CardHeader>
        <CardTitle>Get in Touch</CardTitle>
        <CardDescription>
          Have a question or need help? We're here to assist you.
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          {/* Name and Email */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                {...register('name')}
                placeholder="Your full name"
                className={cn(errors.name && "border-red-500")}
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name.message}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                {...register('email')}
                placeholder="your@email.com"
                className={cn(errors.email && "border-red-500")}
              />
              {errors.email && (
                <p className="text-sm text-red-500">{errors.email.message}</p>
              )}
            </div>
          </div>

          {/* Topic Selection */}
          {showTopic && (
            <div className="space-y-2">
              <Label htmlFor="topic">Topic *</Label>
              <Select
                value={watch('topic')}
                onValueChange={(value) => setValue('topic', value)}
              >
                <SelectTrigger className={cn(errors.topic && "border-red-500")}>
                  <SelectValue placeholder="Select a topic" />
                </SelectTrigger>
                <SelectContent>
                  {topics.map((topic) => (
                    <SelectItem key={topic.value} value={topic.value}>
                      <div>
                        <div className="font-medium">{topic.label}</div>
                        {topic.description && (
                          <div className="text-sm text-muted-foreground">
                            {topic.description}
                          </div>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.topic && (
                <p className="text-sm text-red-500">{errors.topic.message}</p>
              )}
              {selectedTopic?.description && (
                <p className="text-sm text-muted-foreground">
                  {selectedTopic.description}
                </p>
              )}
            </div>
          )}

          {/* Priority Selection */}
          {showPriority && (
            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <Select
                value={watch('priority')}
                onValueChange={(value: 'low' | 'medium' | 'high') => setValue('priority', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low - General inquiry</SelectItem>
                  <SelectItem value="medium">Medium - Standard support</SelectItem>
                  <SelectItem value="high">High - Urgent issue</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Subject */}
          <div className="space-y-2">
            <Label htmlFor="subject">Subject *</Label>
            <Input
              id="subject"
              {...register('subject')}
              placeholder="Brief description of your inquiry"
              className={cn(errors.subject && "border-red-500")}
            />
            {errors.subject && (
              <p className="text-sm text-red-500">{errors.subject.message}</p>
            )}
          </div>

          {/* Message */}
          <div className="space-y-2">
            <Label htmlFor="message">Message *</Label>
            <Textarea
              id="message"
              {...register('message')}
              placeholder="Please provide as much detail as possible..."
              rows={6}
              className={cn(errors.message && "border-red-500")}
            />
            {errors.message && (
              <p className="text-sm text-red-500">{errors.message.message}</p>
            )}
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={!isValid || isSubmitting}
            className="w-full"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Send Message
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
