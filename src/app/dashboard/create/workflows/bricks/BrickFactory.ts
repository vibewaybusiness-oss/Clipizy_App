import { BrickInstance } from '@/types/bricks';
import type { BrickConfig, BrickContext } from '@/types/workflow';

export interface BrickCreator {
  (config: BrickConfig, context: BrickContext): BrickInstance | Promise<BrickInstance>;
}

export class BrickFactory {
  private registry: Map<string, BrickCreator> = new Map();
  private static instance: BrickFactory;
  private bricksLoaded = false;

  private constructor() {}

  public static getInstance(): BrickFactory {
    if (!BrickFactory.instance) {
      BrickFactory.instance = new BrickFactory();
    }
    return BrickFactory.instance;
  }

  private async loadDefaultBricks(): Promise<void> {
    if (this.bricksLoaded) return;

    // Load existing bricks
    const { LLMBrick } = await import('./LLMBrick');
    const { UserInputBrick } = await import('./UserInputBrick');
    const { BackgroundBrick } = await import('./BackgroundBrick');

    // Load generic bricks
    const { JSONDisplayBrick } = await import('./JSONDisplayBrick');
    const { BackendCallBrick } = await import('./BackendCallBrick');
    const { WaitingDisplayBrick } = await import('./WaitingDisplayBrick');
    const { MediaDisplayBrick } = await import('./MediaDisplayBrick');
    const { ConfirmationBrick } = await import('./ConfirmationBrick');
    const { BatchMediaDisplayBrick } = await import('./BatchMediaDisplayBrick');

    // Register bricks
    this.register('llm', (config, context) => new LLMBrick(config, context));
    this.register('user_input', (config, context) => new UserInputBrick(config, context));
    this.register('api_call', (config, context) => new BackendCallBrick(config, context));
    this.register('background', (config, context) => new BackgroundBrick(config, context));

    // Register generic bricks
    this.register('json_display', (config, context) => new JSONDisplayBrick(config, context));
    this.register('waiting_display', (config, context) => new WaitingDisplayBrick(config, context));
    this.register('media_display', (config, context) => new MediaDisplayBrick(config, context));
    this.register('confirmation', (config, context) => new ConfirmationBrick(config, context));
    this.register('batch_media_display', (config, context) => new BatchMediaDisplayBrick(config, context));

    this.bricksLoaded = true;
  }

  public register(type: string, creator: BrickCreator): void {
    this.registry.set(type, creator);
  }

  public unregister(type: string): void {
    this.registry.delete(type);
  }

  public async create(config: BrickConfig, context: BrickContext): Promise<BrickInstance> {
    await this.loadDefaultBricks();

    const creator = this.registry.get(config.type);
    if (!creator) {
      throw new Error(`Unknown brick type: ${config.type}`);
    }
    
    try {
      const result = creator(config, context);
      return result instanceof Promise ? await result : result;
    } catch (error) {
      throw new Error(`Failed to create brick of type ${config.type}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  public getSupportedTypes(): string[] {
    return Array.from(this.registry.keys());
  }

  public hasType(type: string): boolean {
    return this.registry.has(type);
  }

  public clear(): void {
    this.registry.clear();
    this.bricksLoaded = false;
  }
}

export const brickFactory = BrickFactory.getInstance();
