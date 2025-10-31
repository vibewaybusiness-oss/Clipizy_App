import { BrickValidationRule, BrickValidationResult } from '@/types/bricks';
import type { BrickConfig } from '@/types/workflow';

export class BrickUtils {
  private static idCounter = 0;

  public static generateId(prefix: string = 'brick'): string {
    return `${prefix}_${Date.now()}_${++this.idCounter}`;
  }

  public static validateConfig(config: BrickConfig): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!config.id || typeof config.id !== 'string') {
      errors.push('Brick ID is required and must be a string');
    }

    if (!config.type || typeof config.type !== 'string') {
      errors.push('Brick type is required and must be a string');
    }

    if (config.enabled !== undefined && typeof config.enabled !== 'boolean') {
      errors.push('Brick enabled property must be a boolean');
    }

    if (config.validation) {
      const validationErrors = this.validateValidationRules(config.validation);
      errors.push(...validationErrors);
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  public static validateValidationRules(validation: any): string[] {
    const errors: string[] = [];

    if (validation.required !== undefined && typeof validation.required !== 'boolean') {
      errors.push('Validation required property must be a boolean');
    }

    if (validation.minLength !== undefined && (typeof validation.minLength !== 'number' || validation.minLength < 0)) {
      errors.push('Validation minLength must be a non-negative number');
    }

    if (validation.maxLength !== undefined && (typeof validation.maxLength !== 'number' || validation.maxLength < 0)) {
      errors.push('Validation maxLength must be a non-negative number');
    }

    if (validation.pattern !== undefined && !(validation.pattern instanceof RegExp)) {
      errors.push('Validation pattern must be a RegExp');
    }

    if (validation.min !== undefined && typeof validation.min !== 'number') {
      errors.push('Validation min must be a number');
    }

    if (validation.max !== undefined && typeof validation.max !== 'number') {
      errors.push('Validation max must be a number');
    }

    if (validation.custom !== undefined && typeof validation.custom !== 'function') {
      errors.push('Validation custom must be a function');
    }

    if (validation.message !== undefined && typeof validation.message !== 'string') {
      errors.push('Validation message must be a string');
    }

    return errors;
  }

  public static transformData<T>(data: T, transform: (data: T) => any): any {
    try {
      return transform(data);
    } catch (error) {
      console.error('Data transformation failed:', error);
      return data;
    }
  }

  public static mergeData(
    target: any, 
    source: any, 
    type: 'string' | 'object' | 'array' | 'dict'
  ): any {
    switch (type) {
      case 'string':
        return source;
      
      case 'object':
        return { ...target, ...source };
      
      case 'array':
        if (Array.isArray(target) && Array.isArray(source)) {
          return [...target, ...source];
        }
        return Array.isArray(source) ? source : [source];
      
      case 'dict':
        if (typeof target === 'object' && typeof source === 'object' && !Array.isArray(target) && !Array.isArray(source)) {
          return { ...target, ...source };
        }
        return source;
      
      default:
        return source;
    }
  }

  public static async saveToBackend(
    data: any, 
    config: {
      backendKey: string;
      backendType: 'list' | 'dict';
      backendSubkey?: string;
    }
  ): Promise<any> {
    try {
      // This would integrate with your actual backend API
      const payload = {
        [config.backendKey]: config.backendType === 'list' 
          ? (Array.isArray(data) ? data : [data])
          : data
      };

      if (config.backendSubkey && config.backendType === 'dict') {
        payload[config.backendKey] = {
          [config.backendSubkey]: data
        };
      }

      // Placeholder for actual API call
      console.log('Saving to backend:', payload);
      
      return { success: true, data: payload };
    } catch (error) {
      console.error('Failed to save to backend:', error);
      throw error;
    }
  }

  public static validateValue<T>(
    value: T, 
    rules: BrickValidationRule<T>
  ): BrickValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push(rules.message || 'This field is required');
    }

    if (value !== null && value !== undefined) {
      if (rules.minLength !== undefined && typeof value === 'string' && value.length < rules.minLength) {
        errors.push(rules.message || `Minimum length is ${rules.minLength}`);
      }

      if (rules.maxLength !== undefined && typeof value === 'string' && value.length > rules.maxLength) {
        errors.push(rules.message || `Maximum length is ${rules.maxLength}`);
      }

      if (rules.pattern && typeof value === 'string' && !rules.pattern.test(value)) {
        errors.push(rules.message || 'Value does not match required pattern');
      }

      if (rules.min !== undefined && typeof value === 'number' && value < rules.min) {
        errors.push(rules.message || `Minimum value is ${rules.min}`);
      }

      if (rules.max !== undefined && typeof value === 'number' && value > rules.max) {
        errors.push(rules.message || `Maximum value is ${rules.max}`);
      }

      if (rules.custom) {
        const customResult = rules.custom(value);
        if (customResult === false) {
          errors.push(rules.message || 'Value is invalid');
        } else if (typeof customResult === 'string') {
          errors.push(customResult);
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  public static deepClone<T>(obj: T): T {
    if (obj === null || typeof obj !== 'object') {
      return obj;
    }

    if (obj instanceof Date) {
      return new Date(obj.getTime()) as T;
    }

    if (obj instanceof Array) {
      return obj.map(item => this.deepClone(item)) as T;
    }

    if (typeof obj === 'object') {
      const cloned = {} as T;
      for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
          cloned[key] = this.deepClone(obj[key]);
        }
      }
      return cloned;
    }

    return obj;
  }

  public static debounce<T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void {
    let timeout: NodeJS.Timeout;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }

  public static throttle<T extends (...args: any[]) => any>(
    func: T,
    limit: number
  ): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    
    return (...args: Parameters<T>) => {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  public static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  public static isValidFileType(file: File, acceptTypes: string[]): boolean {
    if (!acceptTypes || acceptTypes.length === 0) return true;
    
    return acceptTypes.some(type => {
      if (type.endsWith('/*')) {
        const baseType = type.slice(0, -2);
        return file.type.startsWith(baseType);
      }
      return file.type === type;
    });
  }

  public static createFileFromBlob(blob: Blob, filename: string): File {
    return new File([blob], filename, { type: blob.type });
  }

  public static downloadFile(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  public static sanitizeHtml(html: string): string {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  }

  public static escapeRegex(string: string): string {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  public static generateRandomString(length: number = 8): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  public static isEqual(a: any, b: any): boolean {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (typeof a !== typeof b) return false;
    
    if (typeof a === 'object') {
      if (Array.isArray(a) !== Array.isArray(b)) return false;
      
      if (Array.isArray(a)) {
        if (a.length !== b.length) return false;
        for (let i = 0; i < a.length; i++) {
          if (!this.isEqual(a[i], b[i])) return false;
        }
        return true;
      }
      
      const keysA = Object.keys(a);
      const keysB = Object.keys(b);
      
      if (keysA.length !== keysB.length) return false;
      
      for (const key of keysA) {
        if (!keysB.includes(key)) return false;
        if (!this.isEqual(a[key], b[key])) return false;
      }
      
      return true;
    }
    
    return false;
  }
}
