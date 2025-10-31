import { BrickConfig, BrickContext, BrickInstance } from '@/types/bricks';

export interface BrickRegistryEntry {
  type: string;
  creator: (config: BrickConfig, context: BrickContext) => BrickInstance;
  metadata?: {
    name: string;
    description: string;
    version: string;
    author?: string;
    category?: string;
  };
}

export class BrickRegistry {
  private entries: Map<string, BrickRegistryEntry> = new Map();
  private static instance: BrickRegistry;

  private constructor() {}

  public static getInstance(): BrickRegistry {
    if (!BrickRegistry.instance) {
      BrickRegistry.instance = new BrickRegistry();
    }
    return BrickRegistry.instance;
  }

  public register(entry: BrickRegistryEntry): void {
    if (this.entries.has(entry.type)) {
      console.warn(`Brick type '${entry.type}' is already registered. Overwriting...`);
    }
    
    this.entries.set(entry.type, entry);
  }

  public unregister(type: string): boolean {
    return this.entries.delete(type);
  }

  public get(type: string): BrickRegistryEntry | undefined {
    return this.entries.get(type);
  }

  public has(type: string): boolean {
    return this.entries.has(type);
  }

  public list(): BrickRegistryEntry[] {
    return Array.from(this.entries.values());
  }

  public listByCategory(category: string): BrickRegistryEntry[] {
    return this.list().filter(entry => entry.metadata?.category === category);
  }

  public getTypes(): string[] {
    return Array.from(this.entries.keys());
  }

  public getCategories(): string[] {
    const categories = new Set<string>();
    this.entries.forEach(entry => {
      if (entry.metadata?.category) {
        categories.add(entry.metadata.category);
      }
    });
    return Array.from(categories);
  }

  public clear(): void {
    this.entries.clear();
  }

  public getMetadata(type: string): BrickRegistryEntry['metadata'] | undefined {
    return this.entries.get(type)?.metadata;
  }

  public search(query: string): BrickRegistryEntry[] {
    const lowercaseQuery = query.toLowerCase();
    return this.list().filter(entry => {
      const name = entry.metadata?.name?.toLowerCase() || '';
      const description = entry.metadata?.description?.toLowerCase() || '';
      const type = entry.type.toLowerCase();
      
      return name.includes(lowercaseQuery) || 
             description.includes(lowercaseQuery) || 
             type.includes(lowercaseQuery);
    });
  }

  public validate(entry: BrickRegistryEntry): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!entry.type || typeof entry.type !== 'string') {
      errors.push('Type is required and must be a string');
    }

    if (!entry.creator || typeof entry.creator !== 'function') {
      errors.push('Creator is required and must be a function');
    }

    if (entry.metadata) {
      if (entry.metadata.name && typeof entry.metadata.name !== 'string') {
        errors.push('Metadata name must be a string');
      }
      
      if (entry.metadata.description && typeof entry.metadata.description !== 'string') {
        errors.push('Metadata description must be a string');
      }
      
      if (entry.metadata.version && typeof entry.metadata.version !== 'string') {
        errors.push('Metadata version must be a string');
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  public export(): Record<string, any> {
    const exportData: Record<string, any> = {};
    
    this.entries.forEach((entry, type) => {
      exportData[type] = {
        type: entry.type,
        metadata: entry.metadata,
        // Note: We don't export the creator function as it can't be serialized
        hasCreator: !!entry.creator
      };
    });
    
    return exportData;
  }

  public import(data: Record<string, any>): { success: boolean; errors: string[] } {
    const errors: string[] = [];
    
    try {
      Object.entries(data).forEach(([type, entryData]) => {
        if (typeof entryData === 'object' && entryData !== null) {
          const entry: Partial<BrickRegistryEntry> = {
            type,
            metadata: entryData.metadata
          };
          
          // Note: Creator functions cannot be imported from JSON
          if (!entryData.hasCreator) {
            errors.push(`Cannot import brick type '${type}': Creator function not available`);
          }
        } else {
          errors.push(`Invalid entry data for type '${type}'`);
        }
      });
    } catch (error) {
      errors.push(`Failed to import registry data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
    
    return {
      success: errors.length === 0,
      errors
    };
  }
}

export const brickRegistry = BrickRegistry.getInstance();
