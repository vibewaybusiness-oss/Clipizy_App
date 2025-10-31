"use client";

import React from 'react';
import { BrickInstance } from '@/types/bricks';
import type { WorkflowContext } from '@/types/workflow';

export interface BrickComponentProps {
  brick: any;
  onComplete: (result: any) => void;
  onError: (error: Error) => void;
  context: WorkflowContext;
}

export type BrickComponent = React.ComponentType<BrickComponentProps>;

class ComponentRegistry {
  private components: Map<string, BrickComponent> = new Map();
  private static instance: ComponentRegistry;

  private constructor() {
    this.registerDefaultComponents();
  }

  public static getInstance(): ComponentRegistry {
    if (!ComponentRegistry.instance) {
      ComponentRegistry.instance = new ComponentRegistry();
    }
    return ComponentRegistry.instance;
  }

  private async registerDefaultComponents(): Promise<void> {
    // Dynamic imports to avoid circular dependencies
    const { LLMBrickComponent } = await import('../bricks/LLMBrick');
    const { UserInputBrickComponent } = await import('../bricks/UserInputBrick');
    const { APICallBrickComponent } = await import('../bricks/APICallBrick');
    const { BackgroundBrickComponent } = await import('../bricks/BackgroundBrick');

    this.register('llm', LLMBrickComponent);
    this.register('user_input', UserInputBrickComponent);
    this.register('api_call', APICallBrickComponent);
    this.register('background', BackgroundBrickComponent);
  }

  public register(type: string, component: BrickComponent): void {
    this.components.set(type, component);
  }

  public unregister(type: string): void {
    this.components.delete(type);
  }

  public getComponent(type: string): BrickComponent | undefined {
    return this.components.get(type);
  }

  public hasComponent(type: string): boolean {
    return this.components.has(type);
  }

  public getRegisteredTypes(): string[] {
    return Array.from(this.components.keys());
  }

  public clear(): void {
    this.components.clear();
  }
}

export const componentRegistry = ComponentRegistry.getInstance();
