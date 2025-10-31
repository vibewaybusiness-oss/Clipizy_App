import { BrickConfig, BrickContext, BrickInstance } from '@/types/bricks';
import { brickFactory } from '../bricks/BrickFactory';
import { brickRegistry } from '../bricks/BrickRegistry';

export class BrickFactoryUtils {
  private static instance: BrickFactoryUtils;
  private brickInstances: Map<string, BrickInstance> = new Map();

  private constructor() {}

  public static getInstance(): BrickFactoryUtils {
    if (!BrickFactoryUtils.instance) {
      BrickFactoryUtils.instance = new BrickFactoryUtils();
    }
    return BrickFactoryUtils.instance;
  }

  public createBrick(config: BrickConfig, context: BrickContext): BrickInstance {
    try {
      const brick = brickFactory.create(config, context);
      this.brickInstances.set(brick.id, brick);
      return brick;
    } catch (error) {
      throw new Error(`Failed to create brick '${config.id}': ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  public createBricks(configs: BrickConfig[], context: BrickContext): BrickInstance[] {
    return configs.map(config => this.createBrick(config, context));
  }

  public getBrick(id: string): BrickInstance | undefined {
    return this.brickInstances.get(id);
  }

  public getAllBricks(): BrickInstance[] {
    return Array.from(this.brickInstances.values());
  }

  public destroyBrick(id: string): boolean {
    const brick = this.brickInstances.get(id);
    if (brick) {
      brick.destroy();
      return this.brickInstances.delete(id);
    }
    return false;
  }

  public destroyAllBricks(): void {
    this.brickInstances.forEach(brick => brick.destroy());
    this.brickInstances.clear();
  }

  public executeBrick(id: string): Promise<any> {
    const brick = this.brickInstances.get(id);
    if (!brick) {
      throw new Error(`Brick '${id}' not found`);
    }
    return brick.execute();
  }

  public executeBricks(ids: string[]): Promise<any[]> {
    return Promise.all(ids.map(id => this.executeBrick(id)));
  }

  public executeAllBricks(): Promise<any[]> {
    const ids = Array.from(this.brickInstances.keys());
    return this.executeBricks(ids);
  }

  public validateBrick(id: string): boolean | string {
    const brick = this.brickInstances.get(id);
    if (!brick) {
      return `Brick '${id}' not found`;
    }
    return brick.validate();
  }

  public validateAllBricks(): { id: string; valid: boolean; error?: string }[] {
    return Array.from(this.brickInstances.entries()).map(([id, brick]) => {
      const validation = brick.validate();
      return {
        id,
        valid: validation === true,
        error: typeof validation === 'string' ? validation : undefined
      };
    });
  }

  public resetBrick(id: string): boolean {
    const brick = this.brickInstances.get(id);
    if (brick) {
      brick.reset();
      return true;
    }
    return false;
  }

  public resetAllBricks(): void {
    this.brickInstances.forEach(brick => brick.reset());
  }

  public getBrickState(id: string): any {
    const brick = this.brickInstances.get(id);
    if (!brick) {
      throw new Error(`Brick '${id}' not found`);
    }
    return brick.getState ? brick.getState() : null;
  }

  public getAllBrickStates(): Record<string, any> {
    const states: Record<string, any> = {};
    this.brickInstances.forEach((brick, id) => {
      states[id] = brick.getState ? brick.getState() : null;
    });
    return states;
  }

  public getBrickActions(id: string): any {
    const brick = this.brickInstances.get(id);
    if (!brick) {
      throw new Error(`Brick '${id}' not found`);
    }
    return brick.getActions ? brick.getActions() : null;
  }

  public getAllBrickActions(): Record<string, any> {
    const actions: Record<string, any> = {};
    this.brickInstances.forEach((brick, id) => {
      actions[id] = brick.getActions ? brick.getActions() : null;
    });
    return actions;
  }

  public getBrickCount(): number {
    return this.brickInstances.size;
  }

  public getBrickTypes(): string[] {
    const types = new Set<string>();
    this.brickInstances.forEach(brick => {
      types.add(brick.type);
    });
    return Array.from(types);
  }

  public getBricksByType(type: string): BrickInstance[] {
    return Array.from(this.brickInstances.values()).filter(brick => brick.type === type);
  }

  public hasBrick(id: string): boolean {
    return this.brickInstances.has(id);
  }

  public clear(): void {
    this.destroyAllBricks();
  }

  public exportBrickConfigs(): BrickConfig[] {
    return Array.from(this.brickInstances.values()).map(brick => ({
      id: brick.id,
      type: brick.type,
      // Note: This is a simplified export - in practice you'd want to export the full config
    } as BrickConfig));
  }

  public createBrickFromTemplate(
    templateId: string,
    overrides: Partial<BrickConfig>,
    context: BrickContext
  ): BrickInstance {
    // This would load a brick template and apply overrides
    // For now, we'll just create a basic config
    const config: BrickConfig = {
      id: overrides.id || `brick_${Date.now()}`,
      type: overrides.type || 'user_input',
      ...overrides
    };
    
    return this.createBrick(config, context);
  }

  public cloneBrick(id: string, newId: string, context: BrickContext): BrickInstance {
    const originalBrick = this.brickInstances.get(id);
    if (!originalBrick) {
      throw new Error(`Brick '${id}' not found`);
    }

    const config: BrickConfig = {
      id: newId,
      type: originalBrick.type,
      // In a real implementation, you'd copy the full config
    };

    return this.createBrick(config, context);
  }

  public getBrickDependencies(id: string): string[] {
    // This would analyze brick configurations to find dependencies
    // For now, return empty array
    return [];
  }

  public validateBrickDependencies(): { id: string; missing: string[] }[] {
    const results: { id: string; missing: string[] }[] = [];
    
    this.brickInstances.forEach((brick, id) => {
      const dependencies = this.getBrickDependencies(id);
      const missing = dependencies.filter(dep => !this.hasBrick(dep));
      
      if (missing.length > 0) {
        results.push({ id, missing });
      }
    });
    
    return results;
  }
}

export const brickFactoryUtils = BrickFactoryUtils.getInstance();
