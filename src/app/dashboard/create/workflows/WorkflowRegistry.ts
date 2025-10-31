"use client";

import { WorkflowConfig } from '@/types/workflow';
import { workflowLoader } from './utils/workflowLoader';

export interface WorkflowMetadata {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  version: string;
  author?: string;
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
}

export interface WorkflowRegistryEntry {
  metadata: WorkflowMetadata;
  config: WorkflowConfig;
  loadConfig: () => Promise<WorkflowConfig>;
}

class WorkflowRegistry {
  private workflows: Map<string, WorkflowRegistryEntry> = new Map();
  private loadingPromises: Map<string, Promise<WorkflowConfig>> = new Map();
  private static instance: WorkflowRegistry;

  private constructor() {
    this.registerDefaultWorkflows();
  }

  public static getInstance(): WorkflowRegistry {
    if (!WorkflowRegistry.instance) {
      WorkflowRegistry.instance = new WorkflowRegistry();
    }
    return WorkflowRegistry.instance;
  }

  private async registerDefaultWorkflows(): Promise<void> {
    // Register music clip workflow
    this.register({
      id: 'music_clip_workflow',
      name: 'Music Video Clip',
      description: 'Create a music video clip with AI-generated visuals',
      category: 'video',
      tags: ['music', 'video', 'ai', 'generation'],
      version: '1.0.0',
      author: 'Clipizy Team',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isActive: true
    }, () => workflowLoader.loadFromJSON('music-clip-workflow.json'));

    // Register video clip workflow
    this.register({
      id: 'video_clip_workflow',
      name: 'Video Clip',
      description: 'Create a short video clip with AI-generated content',
      category: 'video',
      tags: ['video', 'ai', 'generation', 'short-form'],
      version: '1.0.0',
      author: 'Clipizy Team',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isActive: true
    }, () => workflowLoader.loadFromJSON('video-clip-workflow.json'));

    // Register business ad workflow
    this.register({
      id: 'business_ad_workflow',
      name: 'Business Advertisement',
      description: 'Create a professional business advertisement',
      category: 'marketing',
      tags: ['business', 'advertisement', 'marketing', 'professional'],
      version: '1.0.0',
      author: 'Clipizy Team',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isActive: true
    }, () => workflowLoader.loadFromJSON('business-ad-workflow.json'));

    // Register automate workflow
    this.register({
      id: 'automate_workflow_workflow',
      name: 'Automate Workflow',
      description: 'Automate your content creation workflow',
      category: 'automation',
      tags: ['automation', 'workflow', 'efficiency', 'productivity'],
      version: '1.0.0',
      author: 'Clipizy Team',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      isActive: true
    }, () => workflowLoader.loadFromJSON('automate-workflow.json'));
  }

  public register(metadata: WorkflowMetadata, loadConfig: () => Promise<WorkflowConfig>): void {
    this.workflows.set(metadata.id, {
      metadata,
      config: null as any, // Will be loaded on demand
      loadConfig
    });
  }

  public async getWorkflow(id: string): Promise<WorkflowConfig | null> {
    const entry = this.workflows.get(id);
    if (!entry) {
      return null;
    }

    // Return cached config if available
    if (entry.config) {
      return entry.config;
    }

    // Check if already loading
    if (this.loadingPromises.has(id)) {
      return await this.loadingPromises.get(id)!;
    }

    // Start loading
    const loadPromise = entry.loadConfig()
      .then(config => {
        entry.config = config;
        return config;
      })
      .catch(error => {
        console.error(`Failed to load workflow ${id}:`, error);
        return null;
      })
      .finally(() => {
        this.loadingPromises.delete(id);
      });

    this.loadingPromises.set(id, loadPromise);
    return await loadPromise;
  }

  public getWorkflowMetadata(id: string): WorkflowMetadata | null {
    const entry = this.workflows.get(id);
    return entry?.metadata || null;
  }

  public getAllWorkflows(): WorkflowMetadata[] {
    return Array.from(this.workflows.values())
      .map(entry => entry.metadata)
      .filter(metadata => metadata.isActive);
  }

  public getWorkflowsByCategory(category: string): WorkflowMetadata[] {
    return this.getAllWorkflows()
      .filter(metadata => metadata.category === category);
  }

  public getWorkflowsByTag(tag: string): WorkflowMetadata[] {
    return this.getAllWorkflows()
      .filter(metadata => metadata.tags.includes(tag));
  }

  public searchWorkflows(query: string): WorkflowMetadata[] {
    const lowercaseQuery = query.toLowerCase();
    return this.getAllWorkflows()
      .filter(metadata => 
        metadata.name.toLowerCase().includes(lowercaseQuery) ||
        metadata.description.toLowerCase().includes(lowercaseQuery) ||
        metadata.tags.some(tag => tag.toLowerCase().includes(lowercaseQuery))
      );
  }

  public hasWorkflow(id: string): boolean {
    return this.workflows.has(id);
  }

  public unregister(id: string): boolean {
    return this.workflows.delete(id);
  }

  public clear(): void {
    this.workflows.clear();
  }

  public getCategories(): string[] {
    const categories = new Set<string>();
    this.getAllWorkflows().forEach(metadata => {
      categories.add(metadata.category);
    });
    return Array.from(categories).sort();
  }

  public getTags(): string[] {
    const tags = new Set<string>();
    this.getAllWorkflows().forEach(metadata => {
      metadata.tags.forEach(tag => tags.add(tag));
    });
    return Array.from(tags).sort();
  }
}

export const workflowRegistry = WorkflowRegistry.getInstance();
