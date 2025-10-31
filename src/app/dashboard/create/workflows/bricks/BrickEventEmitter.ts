import { BrickMessage } from '@/types/bricks';

export interface BrickEventCallback {
  (data: any): void;
}

export interface BrickEventSubscription {
  id: string;
  event: string;
  callback: BrickEventCallback;
  once: boolean;
}

export class BrickEventEmitter {
  private subscriptions: Map<string, BrickEventSubscription[]> = new Map();
  private subscriptionIdCounter = 0;
  private static instance: BrickEventEmitter;

  private constructor() {}

  public static getInstance(): BrickEventEmitter {
    if (!BrickEventEmitter.instance) {
      BrickEventEmitter.instance = new BrickEventEmitter();
    }
    return BrickEventEmitter.instance;
  }

  public on(event: string, callback: BrickEventCallback): string {
    const subscriptionId = this.generateSubscriptionId();
    const subscription: BrickEventSubscription = {
      id: subscriptionId,
      event,
      callback,
      once: false
    };

    if (!this.subscriptions.has(event)) {
      this.subscriptions.set(event, []);
    }

    this.subscriptions.get(event)!.push(subscription);
    return subscriptionId;
  }

  public once(event: string, callback: BrickEventCallback): string {
    const subscriptionId = this.generateSubscriptionId();
    const subscription: BrickEventSubscription = {
      id: subscriptionId,
      event,
      callback,
      once: true
    };

    if (!this.subscriptions.has(event)) {
      this.subscriptions.set(event, []);
    }

    this.subscriptions.get(event)!.push(subscription);
    return subscriptionId;
  }

  public off(event: string, callback?: BrickEventCallback): void {
    if (!this.subscriptions.has(event)) {
      return;
    }

    const eventSubscriptions = this.subscriptions.get(event)!;
    
    if (callback) {
      // Remove specific callback
      const filteredSubscriptions = eventSubscriptions.filter(
        sub => sub.callback !== callback
      );
      this.subscriptions.set(event, filteredSubscriptions);
    } else {
      // Remove all callbacks for this event
      this.subscriptions.delete(event);
    }
  }

  public offById(subscriptionId: string): void {
    for (const [event, subscriptions] of this.subscriptions.entries()) {
      const filteredSubscriptions = subscriptions.filter(
        sub => sub.id !== subscriptionId
      );
      
      if (filteredSubscriptions.length === 0) {
        this.subscriptions.delete(event);
      } else {
        this.subscriptions.set(event, filteredSubscriptions);
      }
    }
  }

  public emit(event: string, data: any): void {
    if (!this.subscriptions.has(event)) {
      return;
    }

    const eventSubscriptions = this.subscriptions.get(event)!;
    const subscriptionsToRemove: string[] = [];

    eventSubscriptions.forEach(subscription => {
      try {
        subscription.callback(data);
        
        if (subscription.once) {
          subscriptionsToRemove.push(subscription.id);
        }
      } catch (error) {
        console.error(`Error in event callback for '${event}':`, error);
      }
    });

    // Remove once subscriptions
    subscriptionsToRemove.forEach(id => this.offById(id));
  }

  public emitMessage(message: BrickMessage): void {
    this.emit(`message:${message.type}`, message);
    this.emit('message', message);
  }

  public emitData(source: string, target: string | undefined, data: any): void {
    const message: BrickMessage = {
      type: 'data',
      source,
      target,
      payload: data,
      timestamp: new Date()
    };
    this.emit(`data:${source}`, data);
    this.emitMessage(message);
  }

  public emitError(source: string, target: string | undefined, error: Error): void {
    const message: BrickMessage = {
      type: 'error',
      source,
      target,
      payload: error,
      timestamp: new Date()
    };
    this.emit(`error:${source}`, error);
    this.emitMessage(message);
  }

  public emitComplete(source: string, target: string | undefined, result: any): void {
    const message: BrickMessage = {
      type: 'complete',
      source,
      target,
      payload: result,
      timestamp: new Date()
    };
    this.emit(`complete:${source}`, result);
    this.emitMessage(message);
  }

  public emitProgress(source: string, target: string | undefined, progress: number): void {
    const message: BrickMessage = {
      type: 'progress',
      source,
      target,
      payload: { progress },
      timestamp: new Date()
    };
    this.emit(`progress:${source}`, progress);
    this.emitMessage(message);
  }

  public emitStatus(source: string, target: string | undefined, status: string): void {
    const message: BrickMessage = {
      type: 'status',
      source,
      target,
      payload: { status },
      timestamp: new Date()
    };
    this.emit(`status:${source}`, status);
    this.emitMessage(message);
  }

  public getEventNames(): string[] {
    return Array.from(this.subscriptions.keys());
  }

  public getSubscriptionCount(event?: string): number {
    if (event) {
      return this.subscriptions.get(event)?.length || 0;
    }
    
    let total = 0;
    for (const subscriptions of this.subscriptions.values()) {
      total += subscriptions.length;
    }
    return total;
  }

  public hasSubscriptions(event: string): boolean {
    return this.subscriptions.has(event) && this.subscriptions.get(event)!.length > 0;
  }

  public clear(): void {
    this.subscriptions.clear();
  }

  public clearEvent(event: string): void {
    this.subscriptions.delete(event);
  }

  private generateSubscriptionId(): string {
    return `sub_${Date.now()}_${++this.subscriptionIdCounter}`;
  }

  public createScopedEmitter(scope: string): ScopedBrickEventEmitter {
    return new ScopedBrickEventEmitter(this, scope);
  }

  // GENERIC OVERLAY (POPUP) REQUEST/RESPONSE API
  public requestOverlay<T = any>(componentId: string, props?: any): Promise<T> {
    const requestId = this.generateSubscriptionId();
    return new Promise<T>((resolve, reject) => {
      const resolveEvent = `overlay:resolve:${requestId}`;
      const rejectEvent = `overlay:reject:${requestId}`;

      const resolveSub = this.once(resolveEvent, (data) => {
        resolve(data as T);
      });
      const rejectSub = this.once(rejectEvent, (err) => {
        this.offById(resolveSub);
        reject(err instanceof Error ? err : new Error(String(err)));
      });

      this.emit('overlay:open', {
        requestId,
        componentId,
        props: props || {}
      });
    });
  }

  public resolveOverlay(requestId: string, data?: any): void {
    this.emit(`overlay:resolve:${requestId}`, data);
  }

  public rejectOverlay(requestId: string, error?: any): void {
    this.emit(`overlay:reject:${requestId}`, error || new Error('Overlay cancelled'));
  }
}

export class ScopedBrickEventEmitter {
  constructor(
    private parent: BrickEventEmitter,
    private scope: string
  ) {}

  public on(event: string, callback: BrickEventCallback): string {
    return this.parent.on(`${this.scope}:${event}`, callback);
  }

  public once(event: string, callback: BrickEventCallback): string {
    return this.parent.once(`${this.scope}:${event}`, callback);
  }

  public off(event: string, callback?: BrickEventCallback): void {
    this.parent.off(`${this.scope}:${event}`, callback);
  }

  public emit(event: string, data: any): void {
    this.parent.emit(`${this.scope}:${event}`, data);
  }

  public emitMessage(message: BrickMessage): void {
    const scopedMessage = {
      ...message,
      source: `${this.scope}:${message.source}`
    };
    this.parent.emitMessage(scopedMessage);
  }

  public emitData(target: string | undefined, data: any): void {
    this.parent.emitData(this.scope, target, data);
  }

  public emitError(target: string | undefined, error: Error): void {
    this.parent.emitError(this.scope, target, error);
  }

  public emitComplete(target: string | undefined, result: any): void {
    this.parent.emitComplete(this.scope, target, result);
  }

  public emitProgress(target: string | undefined, progress: number): void {
    this.parent.emitProgress(this.scope, target, progress);
  }

  public emitStatus(target: string | undefined, status: string): void {
    this.parent.emitStatus(this.scope, target, status);
  }
}

export const brickEventEmitter = BrickEventEmitter.getInstance();
