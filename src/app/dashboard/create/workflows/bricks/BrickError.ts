import { BrickError, BrickValidationError, BrickExecutionError } from '@/types/bricks';

export class BrickErrorHandler {
  private static instance: BrickErrorHandler;
  private errorCallbacks: Map<string, (error: BrickError) => void> = new Map();

  private constructor() {}

  public static getInstance(): BrickErrorHandler {
    if (!BrickErrorHandler.instance) {
      BrickErrorHandler.instance = new BrickErrorHandler();
    }
    return BrickErrorHandler.instance;
  }

  public handleError(error: Error, brickId: string, brickType: string, context?: any): BrickError {
    let brickError: BrickError;

    if (error instanceof BrickError) {
      brickError = error;
    } else if (error.name === 'ValidationError' || error.message.includes('validation')) {
      brickError = new BrickValidationError(
        error.message,
        brickId,
        brickType,
        [error.message]
      );
    } else {
      brickError = new BrickExecutionError(
        error.message,
        brickId,
        brickType,
        error
      );
    }

    // Add context information if provided
    if (context) {
      brickError.details = {
        ...brickError.details,
        context
      };
    }

    // Log the error
    console.error('Brick Error:', {
      brickId,
      brickType,
      error: brickError,
      context
    });

    // Notify registered callbacks
    this.notifyErrorCallbacks(brickError);

    return brickError;
  }

  public registerErrorCallback(brickId: string, callback: (error: BrickError) => void): void {
    this.errorCallbacks.set(brickId, callback);
  }

  public unregisterErrorCallback(brickId: string): void {
    this.errorCallbacks.delete(brickId);
  }

  private notifyErrorCallbacks(error: BrickError): void {
    this.errorCallbacks.forEach((callback, brickId) => {
      try {
        callback(error);
      } catch (callbackError) {
        console.error('Error in error callback:', callbackError);
      }
    });
  }

  public createValidationError(
    message: string,
    brickId: string,
    brickType: string,
    validationErrors: string[]
  ): BrickValidationError {
    return new BrickValidationError(message, brickId, brickType, validationErrors);
  }

  public createExecutionError(
    message: string,
    brickId: string,
    brickType: string,
    originalError?: Error
  ): BrickExecutionError {
    return new BrickExecutionError(message, brickId, brickType, originalError);
  }

  public createGenericError(
    message: string,
    brickId: string,
    brickType: string,
    code?: string,
    details?: any
  ): BrickError {
    return new BrickError(message, brickId, brickType, code, details);
  }

  public isBrickError(error: any): error is BrickError {
    return error instanceof BrickError;
  }

  public isValidationError(error: any): error is BrickValidationError {
    return error instanceof BrickValidationError;
  }

  public isExecutionError(error: any): error is BrickExecutionError {
    return error instanceof BrickExecutionError;
  }

  public getErrorCode(error: BrickError): string | undefined {
    return error.code;
  }

  public getErrorDetails(error: BrickError): any {
    return error.details;
  }

  public getValidationErrors(error: BrickValidationError): string[] {
    return error.validationErrors;
  }

  public getOriginalError(error: BrickExecutionError): Error | undefined {
    return error.originalError;
  }

  public formatErrorForUser(error: BrickError): string {
    if (this.isValidationError(error)) {
      return error.validationErrors.join(', ');
    }
    
    if (this.isExecutionError(error)) {
      return `Execution failed: ${error.message}`;
    }
    
    return error.message;
  }

  public formatErrorForLogging(error: BrickError): string {
    const details = this.getErrorDetails(error);
    const context = details?.context ? `\nContext: ${JSON.stringify(details.context, null, 2)}` : '';
    
    return `[${error.brickType}] ${error.brickId}: ${error.message}${context}`;
  }

  public clear(): void {
    this.errorCallbacks.clear();
  }
}

export const brickErrorHandler = BrickErrorHandler.getInstance();

// Utility functions for common error scenarios
export const createValidationError = (
  message: string,
  brickId: string,
  brickType: string,
  validationErrors: string[]
) => brickErrorHandler.createValidationError(message, brickId, brickType, validationErrors);

export const createExecutionError = (
  message: string,
  brickId: string,
  brickType: string,
  originalError?: Error
) => brickErrorHandler.createExecutionError(message, brickId, brickType, originalError);

export const createGenericError = (
  message: string,
  brickId: string,
  brickType: string,
  code?: string,
  details?: any
) => brickErrorHandler.createGenericError(message, brickId, brickType, code, details);

export const handleBrickError = (
  error: Error,
  brickId: string,
  brickType: string,
  context?: any
) => brickErrorHandler.handleError(error, brickId, brickType, context);
