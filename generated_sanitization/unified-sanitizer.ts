// Unified TypeScript Sanitizer
// Generated from Python unified sanitizer

import { sanitizerConfig, sanitizationPatterns } from './sanitizer-config';

export interface SanitizerResult {
  original: any;
  sanitized: any;
  isValid: boolean;
  warnings: string[];
  errors: string[];
}

export class UnifiedInputSanitizer {
  private config = sanitizerConfig;
  private patterns = sanitizationPatterns;

  sanitizeString(value: string, inputType: string = 'text'): SanitizerResult {
    if (typeof value !== 'string') {
      return {
        original: value,
        sanitized: String(value),
        isValid: false,
        errors: ['Input must be a string'],
        warnings: [],
      };
    }

    const original = value;
    const warnings: string[] = [];
    const errors: string[] = [];

    // Length validation
    if (value.length > this.config.maxLength) {
      value = value.substring(0, this.config.maxLength);
      warnings.push(`Input truncated to ${this.config.maxLength} characters`);
    }

    // Strip whitespace if configured
    if (this.config.stripWhitespace) {
      value = value.trim();
    }

    // Remove control characters
    if (this.config.removeControlChars) {
      value = value.replace(this.patterns.controlChars[0], '');
    }

    // Normalize unicode
    if (this.config.normalizeUnicode) {
      value = value.replace(this.patterns.unicodeAbuse[0], '');
    }

    // HTML encoding
    if (!this.config.allowHtml) {
      value = this.escapeHtml(value);
    }

    // Check for malicious patterns
    for (const [category, patterns] of Object.entries(this.patterns)) {
      if (category === 'controlChars' || category === 'unicodeAbuse') {
        continue;
      }

      for (const pattern of patterns) {
        if (pattern.test(value)) {
          if (category === 'sqlInjection' && !this.config.allowSqlKeywords) {
            errors.push(`Potential ${category} detected`);
          } else {
            warnings.push(`Potential ${category} pattern detected`);
          }
        }
      }
    }

    return {
      original,
      sanitized: value,
      isValid: errors.length === 0,
      warnings,
      errors,
    };
  }

  sanitizeNumber(value: number | string, inputType: string = 'number'): SanitizerResult {
    const original = value;
    const warnings: string[] = [];
    const errors: string[] = [];
    let sanitized: number;

    try {
      if (typeof value === 'string') {
        const cleaned = value.replace(/[^\d.-]/g, '');
        sanitized = cleaned.includes('.') ? parseFloat(cleaned) : parseInt(cleaned, 10);
      } else {
        sanitized = value;
      }

      if (inputType === 'integer') {
        sanitized = Math.floor(sanitized);
      }

      if (Math.abs(sanitized) > 1e15) {
        warnings.push('Number exceeds reasonable bounds');
      }

      if (isNaN(sanitized)) {
        errors.push('Invalid number format');
        sanitized = 0;
      }

    } catch (e) {
      errors.push(`Invalid number format: ${e}`);
      sanitized = 0;
    }

    return {
      original,
      sanitized,
      isValid: errors.length === 0,
      warnings,
      errors,
    };
  }

  sanitizeBoolean(value: any): SanitizerResult {
    const original = value;
    const warnings: string[] = [];
    const errors: string[] = [];

    let sanitized: boolean;

    if (typeof value === 'boolean') {
      sanitized = value;
    } else if (typeof value === 'string') {
      sanitized = ['true', '1', 'yes', 'on', 'enabled'].includes(value.toLowerCase());
    } else if (typeof value === 'number') {
      sanitized = Boolean(value);
    } else {
      sanitized = Boolean(value);
      warnings.push('Non-boolean value converted to boolean');
    }

    return {
      original,
      sanitized,
      isValid: true,
      warnings,
      errors,
    };
  }

  sanitizeFileUpload(filename: string, contentType: string, size: number): SanitizerResult {
    const original = { filename, contentType, size };
    const warnings: string[] = [];
    const errors: string[] = [];

    // Sanitize filename
    const filenameResult = this.sanitizeString(filename, 'filename');
    if (!filenameResult.isValid) {
      errors.push(...filenameResult.errors.map(e => `Filename: ${e}`));
    }

    // Validate file extension
    const fileExt = filename.toLowerCase().split('.').pop() || '';
    if (!this.config.allowedExtensions.includes(`.${fileExt}`)) {
      errors.push(`File extension '.${fileExt}' not allowed`);
    }

    // Validate content type
    if (!this.config.allowedContentTypes.includes(contentType)) {
      errors.push(`Content type '${contentType}' not allowed`);
    }

    // Validate file size
    if (size > this.config.maxFileSize) {
      errors.push(`File size ${size} exceeds maximum ${this.config.maxFileSize} bytes`);
    }

    const sanitized = {
      filename: filenameResult.sanitized,
      contentType,
      size,
    };

    return {
      original,
      sanitized,
      isValid: errors.length === 0,
      warnings,
      errors,
    };
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Global sanitizer instance
export const unifiedSanitizer = new UnifiedInputSanitizer();

// Main sanitization function
export function sanitizeInput(
  value: any,
  inputType: string = 'auto',
  schema?: Record<string, string>
): SanitizerResult {
  if (inputType === 'auto') {
    inputType = detectType(value);
  }

  switch (inputType) {
    case 'string':
      return unifiedSanitizer.sanitizeString(value);
    case 'number':
      return unifiedSanitizer.sanitizeNumber(value);
    case 'boolean':
      return unifiedSanitizer.sanitizeBoolean(value);
    case 'file':
      if (typeof value === 'object' && value.filename && value.contentType && value.size) {
        return unifiedSanitizer.sanitizeFileUpload(
          value.filename,
          value.contentType,
          value.size
        );
      } else {
        return {
          original: value,
          sanitized: value,
          isValid: false,
          errors: ['Invalid file upload data'],
          warnings: [],
        };
      }
    default:
      return unifiedSanitizer.sanitizeString(String(value));
  }
}

function detectType(value: any): string {
  if (typeof value === 'boolean') return 'boolean';
  if (typeof value === 'number') return 'number';
  if (Array.isArray(value)) return 'array';
  if (typeof value === 'object' && value !== null) return 'object';
  return 'string';
}
