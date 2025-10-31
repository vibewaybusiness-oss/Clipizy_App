import { BrickValidationRule, BrickValidationResult } from '@/types/bricks';
import { BrickUtils } from './BrickUtils';

export class BrickValidator {
  private static instance: BrickValidator;
  private customValidators: Map<string, (value: any) => boolean | string> = new Map();

  private constructor() {}

  public static getInstance(): BrickValidator {
    if (!BrickValidator.instance) {
      BrickValidator.instance = new BrickValidator();
    }
    return BrickValidator.instance;
  }

  public validate<T>(
    value: T,
    rules: BrickValidationRule<T>
  ): BrickValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Required validation
    if (rules.required && this.isEmpty(value)) {
      errors.push(rules.message || 'This field is required');
      return { valid: false, errors, warnings };
    }

    // Skip other validations if value is empty and not required
    if (this.isEmpty(value) && !rules.required) {
      return { valid: true, errors, warnings };
    }

    // String validations
    if (typeof value === 'string') {
      if (rules.minLength !== undefined && value.length < rules.minLength) {
        errors.push(rules.message || `Minimum length is ${rules.minLength}`);
      }

      if (rules.maxLength !== undefined && value.length > rules.maxLength) {
        errors.push(rules.message || `Maximum length is ${rules.maxLength}`);
      }

      if (rules.pattern && !rules.pattern.test(value)) {
        errors.push(rules.message || 'Value does not match required pattern');
      }
    }

    // Number validations
    if (typeof value === 'number') {
      if (rules.min !== undefined && value < rules.min) {
        errors.push(rules.message || `Minimum value is ${rules.min}`);
      }

      if (rules.max !== undefined && value > rules.max) {
        errors.push(rules.message || `Maximum value is ${rules.max}`);
      }
    }

    // Array validations
    if (Array.isArray(value)) {
      if (rules.minLength !== undefined && value.length < rules.minLength) {
        errors.push(rules.message || `Minimum items is ${rules.minLength}`);
      }

      if (rules.maxLength !== undefined && value.length > rules.maxLength) {
        errors.push(rules.message || `Maximum items is ${rules.maxLength}`);
      }
    }

    // Custom validation
    if (rules.custom) {
      const customResult = rules.custom(value);
      if (customResult === false) {
        errors.push(rules.message || 'Value is invalid');
      } else if (typeof customResult === 'string') {
        errors.push(customResult);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  public validateMultiple<T>(
    value: T,
    rules: BrickValidationRule<T>[]
  ): BrickValidationResult {
    const allErrors: string[] = [];
    const allWarnings: string[] = [];

    for (const rule of rules) {
      const result = this.validate(value, rule);
      allErrors.push(...result.errors);
      allWarnings.push(...result.warnings);
    }

    return {
      valid: allErrors.length === 0,
      errors: allErrors,
      warnings: allWarnings
    };
  }

  public registerCustomValidator(
    name: string,
    validator: (value: any) => boolean | string
  ): void {
    this.customValidators.set(name, validator);
  }

  public unregisterCustomValidator(name: string): void {
    this.customValidators.delete(name);
  }

  public getCustomValidator(name: string): ((value: any) => boolean | string) | undefined {
    return this.customValidators.get(name);
  }

  public validateWithCustomValidator(
    value: any,
    validatorName: string
  ): { valid: boolean; message?: string } {
    const validator = this.customValidators.get(validatorName);
    if (!validator) {
      return { valid: false, message: `Custom validator '${validatorName}' not found` };
    }

    const result = validator(value);
    if (typeof result === 'boolean') {
      return { valid: result };
    } else {
      return { valid: false, message: result };
    }
  }

  private isEmpty(value: any): boolean {
    if (value === null || value === undefined) {
      return true;
    }

    if (typeof value === 'string') {
      return value.trim().length === 0;
    }

    if (Array.isArray(value)) {
      return value.length === 0;
    }

    if (typeof value === 'object') {
      return Object.keys(value).length === 0;
    }

    return false;
  }

  public createRule<T>(rule: Partial<BrickValidationRule<T>>): BrickValidationRule<T> {
    return {
      required: false,
      ...rule
    } as BrickValidationRule<T>;
  }

  public createRequiredRule<T>(message?: string): BrickValidationRule<T> {
    return this.createRule({
      required: true,
      message: message || 'This field is required'
    });
  }

  public createLengthRule<T>(
    minLength?: number,
    maxLength?: number,
    message?: string
  ): BrickValidationRule<T> {
    return this.createRule({
      minLength,
      maxLength,
      message: message || `Length must be between ${minLength || 0} and ${maxLength || '∞'} characters`
    });
  }

  public createRangeRule<T>(
    min?: number,
    max?: number,
    message?: string
  ): BrickValidationRule<T> {
    return this.createRule({
      min,
      max,
      message: message || `Value must be between ${min || '-∞'} and ${max || '∞'}`
    });
  }

  public createPatternRule<T>(
    pattern: RegExp,
    message?: string
  ): BrickValidationRule<T> {
    return this.createRule({
      pattern,
      message: message || 'Value does not match required pattern'
    });
  }

  public createEmailRule<T>(message?: string): BrickValidationRule<T> {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return this.createPatternRule(emailPattern, message || 'Please enter a valid email address');
  }

  public createUrlRule<T>(message?: string): BrickValidationRule<T> {
    const urlPattern = /^https?:\/\/.+/;
    return this.createPatternRule(urlPattern, message || 'Please enter a valid URL');
  }

  public createFileTypeRule<T>(
    allowedTypes: string[],
    message?: string
  ): BrickValidationRule<T> {
    return this.createRule({
      custom: (value: any) => {
        if (value instanceof File) {
          return BrickUtils.isValidFileType(value, allowedTypes);
        }
        if (Array.isArray(value)) {
          return value.every(file => 
            file instanceof File && BrickUtils.isValidFileType(file, allowedTypes)
          );
        }
        return false;
      },
      message: message || `File type must be one of: ${allowedTypes.join(', ')}`
    });
  }

  public createFileSizeRule<T>(
    maxSizeBytes: number,
    message?: string
  ): BrickValidationRule<T> {
    return this.createRule({
      custom: (value: any) => {
        if (value instanceof File) {
          return value.size <= maxSizeBytes;
        }
        if (Array.isArray(value)) {
          return value.every(file => 
            file instanceof File && file.size <= maxSizeBytes
          );
        }
        return false;
      },
      message: message || `File size must be less than ${BrickUtils.formatFileSize(maxSizeBytes)}`
    });
  }

  public validateAsync<T>(
    value: T,
    rules: BrickValidationRule<T>,
    asyncValidator?: (value: T) => Promise<boolean | string>
  ): Promise<BrickValidationResult> {
    return new Promise(async (resolve) => {
      const syncResult = this.validate(value, rules);
      
      if (!syncResult.valid || !asyncValidator) {
        resolve(syncResult);
        return;
      }

      try {
        const asyncResult = await asyncValidator(value);
        if (asyncResult === true) {
          resolve(syncResult);
        } else {
          resolve({
            valid: false,
            errors: [typeof asyncResult === 'string' ? asyncResult : 'Async validation failed'],
            warnings: syncResult.warnings
          });
        }
      } catch (error) {
        resolve({
          valid: false,
          errors: ['Async validation error'],
          warnings: syncResult.warnings
        });
      }
    });
  }

  public clear(): void {
    this.customValidators.clear();
  }
}

export const brickValidator = BrickValidator.getInstance();

// Utility functions for common validation scenarios
export const validateRequired = <T>(value: T, message?: string): BrickValidationResult => {
  return brickValidator.validate(value, brickValidator.createRequiredRule(message));
};

export const validateLength = <T>(
  value: T,
  minLength?: number,
  maxLength?: number,
  message?: string
): BrickValidationResult => {
  return brickValidator.validate(value, brickValidator.createLengthRule(minLength, maxLength, message));
};

export const validateRange = <T>(
  value: T,
  min?: number,
  max?: number,
  message?: string
): BrickValidationResult => {
  return brickValidator.validate(value, brickValidator.createRangeRule(min, max, message));
};

export const validateEmail = <T>(value: T, message?: string): BrickValidationResult => {
  return brickValidator.validate(value, brickValidator.createEmailRule(message));
};

export const validateUrl = <T>(value: T, message?: string): BrickValidationResult => {
  return brickValidator.validate(value, brickValidator.createUrlRule(message));
};

export const validateFileType = <T>(
  value: T,
  allowedTypes: string[],
  message?: string
): BrickValidationResult => {
  return brickValidator.validate(value, brickValidator.createFileTypeRule(allowedTypes, message));
};

export const validateFileSize = <T>(
  value: T,
  maxSizeBytes: number,
  message?: string
): BrickValidationResult => {
  return brickValidator.validate(value, brickValidator.createFileSizeRule(maxSizeBytes, message));
};
