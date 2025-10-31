/**
 * SANITIZER SERVICE
 * Frontend sanitization service for all user inputs
 * Now uses unified sanitization system for consistency with Python backend
 */

// Import unified sanitization system
import { 
  unifiedSanitizer, 
  sanitizeInput as unifiedSanitizeInput,
  SanitizerResult as UnifiedSanitizerResult 
} from '../../generated_sanitization/unified-sanitizer';

export interface SanitizerConfig {
  maxLength: number;
  allowHtml: boolean;
  allowScripts: boolean;
  allowSqlKeywords: boolean;
  stripWhitespace: boolean;
  normalizeUnicode: boolean;
  removeControlChars: boolean;
  allowedTags: string[];
  allowedAttributes: string[];
  customPatterns: string[];
}

export interface SanitizerResult {
  original: any;
  sanitized: any;
  isValid: boolean;
  warnings: string[];
  errors: string[];
}

export class InputSanitizer {
  private config: SanitizerConfig;
  private patterns!: Record<string, RegExp[]>;

  constructor(config: Partial<SanitizerConfig> = {}) {
    this.config = {
      maxLength: 10000,
      allowHtml: false,
      allowScripts: false,
      allowSqlKeywords: false,
      stripWhitespace: true,
      normalizeUnicode: true,
      removeControlChars: true,
      allowedTags: [],
      allowedAttributes: [],
      customPatterns: [],
      ...config,
    };
    this.setupPatterns();
  }

  private setupPatterns(): void {
    this.patterns = {
      sqlInjection: [
        /(union|select|insert|update|delete|drop|create|alter|exec|execute)/i,
        /(or|and)\s+\d+\s*=\s*\d+/i,
        /('|"|;|--|\/\*|\*\/)/i,
        /(xp_|sp_|fn_)/i,
        /(waitfor|delay|sleep)/i,
        /(load_file|into\s+outfile|into\s+dumpfile)/i,
      ],
      xss: [
        /<script[^>]*>.*?<\/script>/gi,
        /javascript:/gi,
        /vbscript:/gi,
        /on\w+\s*=/gi,
        /<iframe[^>]*>/gi,
        /<object[^>]*>/gi,
        /<embed[^>]*>/gi,
        /<link[^>]*>/gi,
        /<meta[^>]*>/gi,
        /<style[^>]*>/gi,
        /expression\s*\(/gi,
        /url\s*\(/gi,
      ],
      pathTraversal: [
        /\.\.\//g,
        /\.\.\\/g,
        /%2e%2e%2f/gi,
        /%2e%2e%5c/gi,
        /\.\.%2f/gi,
        /\.\.%5c/gi,
        /%252e%252e%252f/gi,
        /%252e%252e%255c/gi,
      ],
      commandInjection: [
        /[;&|`$]/g,
        /(cmd|command|exec|system|shell)/i,
        /(powershell|bash|sh|cmd)/i,
        /`[^`]*`/g,
        /\$\([^)]*\)/g,
        /<[^>]*>/g,
      ],
      ldapInjection: [
        /[()=*!&|]/g,
        /(objectclass|cn|sn|givenname|mail)/i,
        /(admin|administrator|root)/i,
      ],
      noSqlInjection: [
        /(\$where|\$ne|\$gt|\$lt|\$regex|\$exists)/i,
        /(true|false|null)/i,
        /(and|or|not)/i,
      ],
      controlChars: [
        /[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g,
      ],
      unicodeAbuse: [
        /[\u200B-\u200D\uFEFF]/g,
        /[\u2028\u2029]/g,
        /[\u2060-\u2064]/g,
      ],
    };
  }

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

    // HTML sanitization if HTML is allowed
    if (this.config.allowHtml && this.config.allowedTags.length > 0) {
      value = this.sanitizeHtml(value);
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
        // Remove any non-numeric characters except decimal point and minus
        const cleaned = value.replace(/[^\d.-]/g, '');
        sanitized = cleaned.includes('.') ? parseFloat(cleaned) : parseInt(cleaned, 10);
      } else {
        sanitized = value;
      }

      // Validate range for common numeric types
      if (inputType === 'integer') {
        sanitized = Math.floor(sanitized);
      }

      // Check for reasonable bounds
      if (Math.abs(sanitized) > 1e15) {
        warnings.push('Number exceeds reasonable bounds');
      }

      // Check for NaN
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

  sanitizeList(value: any[], itemType: string = 'string'): SanitizerResult {
    if (!Array.isArray(value)) {
      return {
        original: value,
        sanitized: [],
        isValid: false,
        errors: ['Input must be an array'],
        warnings: [],
      };
    }

    const original = value;
    const warnings: string[] = [];
    const errors: string[] = [];
    const sanitized: any[] = [];

    value.forEach((item, index) => {
      let result: SanitizerResult;

      if (itemType === 'string') {
        result = this.sanitizeString(String(item));
      } else if (itemType === 'number') {
        result = this.sanitizeNumber(item);
      } else if (itemType === 'boolean') {
        result = this.sanitizeBoolean(item);
      } else {
        result = this.sanitizeString(String(item));
      }

      sanitized.push(result.sanitized);
      warnings.push(...result.warnings.map(w => `Item ${index}: ${w}`));
      errors.push(...result.errors.map(e => `Item ${index}: ${e}`));
    });

    return {
      original,
      sanitized,
      isValid: errors.length === 0,
      warnings,
      errors,
    };
  }

  sanitizeObject(value: Record<string, any>, schema?: Record<string, string>): SanitizerResult {
    if (typeof value !== 'object' || value === null || Array.isArray(value)) {
      return {
        original: value,
        sanitized: {},
        isValid: false,
        errors: ['Input must be an object'],
        warnings: [],
      };
    }

    const original = value;
    const warnings: string[] = [];
    const errors: string[] = [];
    const sanitized: Record<string, any> = {};

    for (const [key, val] of Object.entries(value)) {
      // Sanitize key
      const keyResult = this.sanitizeString(String(key), 'key');
      if (!keyResult.isValid) {
        errors.push(...keyResult.errors.map(e => `Key '${key}': ${e}`));
        continue;
      }

      const sanitizedKey = keyResult.sanitized;

      // Determine value type from schema or auto-detect
      const valType = schema?.[sanitizedKey] || this.detectType(val);

      // Sanitize value
      let valResult: SanitizerResult;
      if (valType === 'string') {
        valResult = this.sanitizeString(String(val));
      } else if (valType === 'number') {
        valResult = this.sanitizeNumber(val);
      } else if (valType === 'boolean') {
        valResult = this.sanitizeBoolean(val);
      } else if (valType === 'array') {
        valResult = this.sanitizeList(Array.isArray(val) ? val : [val]);
      } else if (valType === 'object') {
        valResult = this.sanitizeObject(typeof val === 'object' && val !== null ? val : {});
      } else {
        valResult = this.sanitizeString(String(val));
      }

      sanitized[sanitizedKey] = valResult.sanitized;
      warnings.push(...valResult.warnings.map(w => `Key '${sanitizedKey}': ${w}`));
      errors.push(...valResult.errors.map(e => `Key '${sanitizedKey}': ${e}`));
    }

    return {
      original,
      sanitized,
      isValid: errors.length === 0,
      warnings,
      errors,
    };
  }

  sanitizeJson(value: string | object, schema?: Record<string, string>): SanitizerResult {
    const original = value;
    const warnings: string[] = [];
    const errors: string[] = [];

    try {
      let parsed: any;
      
      if (typeof value === 'string') {
        parsed = JSON.parse(value);
      } else {
        parsed = value;
      }

      let result: SanitizerResult;
      if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
        result = this.sanitizeObject(parsed, schema);
      } else if (Array.isArray(parsed)) {
        result = this.sanitizeList(parsed);
      } else {
        result = this.sanitizeString(String(parsed));
      }

      return {
        original,
        sanitized: result.sanitized,
        isValid: result.isValid,
        warnings: [...warnings, ...result.warnings],
        errors: [...errors, ...result.errors],
      };

    } catch (e) {
      errors.push(`Invalid JSON: ${e}`);
      return {
        original,
        sanitized: {},
        isValid: false,
        warnings,
        errors,
      };
    }
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
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.mp3', '.wav', '.mp4', '.avi'];
    const fileExt = filename.toLowerCase().split('.').pop() || '';
    if (!allowedExtensions.includes(`.${fileExt}`)) {
      errors.push(`File extension '.${fileExt}' not allowed`);
    }

    // Validate content type
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/gif', 'application/pdf',
      'text/plain', 'audio/mpeg', 'audio/wav', 'video/mp4', 'video/avi'
    ];
    if (!allowedTypes.includes(contentType)) {
      errors.push(`Content type '${contentType}' not allowed`);
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024;
    if (size > maxSize) {
      errors.push(`File size ${size} exceeds maximum ${maxSize} bytes`);
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

  private detectType(value: any): string {
    if (typeof value === 'boolean') return 'boolean';
    if (typeof value === 'number') return 'number';
    if (Array.isArray(value)) return 'array';
    if (typeof value === 'object' && value !== null) return 'object';
    return 'string';
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  private sanitizeHtml(html: string): string {
    // Simple HTML sanitization - in production, use a library like DOMPurify
    const temp = document.createElement('div');
    temp.innerHTML = html;
    
    // Remove all tags not in allowed list
    const allowedTags = this.config.allowedTags;
    const allowedAttributes = this.config.allowedAttributes;
    
    const walker = document.createTreeWalker(
      temp,
      NodeFilter.SHOW_ELEMENT,
      null
    );

    const elementsToRemove: Element[] = [];
    let node: Node | null = walker.nextNode();

    while (node) {
      const element = node as Element;
      
      if (!allowedTags.includes(element.tagName.toLowerCase())) {
        elementsToRemove.push(element);
      } else {
        // Remove disallowed attributes
        const attributes = Array.from(element.attributes);
        attributes.forEach(attr => {
          if (!allowedAttributes.includes(attr.name)) {
            element.removeAttribute(attr.name);
          }
        });
      }
      
      node = walker.nextNode();
    }

    elementsToRemove.forEach(el => el.remove());

    return temp.innerHTML;
  }
}

// Global sanitizer instance
const sanitizer = new InputSanitizer();

export function sanitizeInput(
  value: any,
  inputType: string = 'auto',
  schema?: Record<string, string>,
  config?: Partial<SanitizerConfig>
): SanitizerResult {
  const sanitizerInstance = config ? new InputSanitizer(config) : sanitizer;
  
  if (inputType === 'auto') {
    inputType = sanitizerInstance['detectType'](value);
  }

  switch (inputType) {
    case 'string':
      return sanitizerInstance.sanitizeString(value);
    case 'number':
      return sanitizerInstance.sanitizeNumber(value);
    case 'boolean':
      return sanitizerInstance.sanitizeBoolean(value);
    case 'array':
      return sanitizerInstance.sanitizeList(value);
    case 'object':
      return sanitizerInstance.sanitizeObject(value, schema);
    case 'json':
      return sanitizerInstance.sanitizeJson(value, schema);
    case 'file':
      if (typeof value === 'object' && value.filename && value.contentType && value.size) {
        return sanitizerInstance.sanitizeFileUpload(
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
      return sanitizerInstance.sanitizeString(String(value));
  }
}

export function createSanitizerConfig(config: Partial<SanitizerConfig>): SanitizerConfig {
  return {
    maxLength: 10000,
    allowHtml: false,
    allowScripts: false,
    allowSqlKeywords: false,
    stripWhitespace: true,
    normalizeUnicode: true,
    removeControlChars: true,
    allowedTags: [],
    allowedAttributes: [],
    customPatterns: [],
    ...config,
  };
}

export function getSanitizer(): InputSanitizer {
  return sanitizer;
}

// Unified sanitization functions
export function getUnifiedSanitizer() {
  return unifiedSanitizer;
}

export function sanitizeInputUnified(
  value: any,
  inputType: string = 'auto',
  schema?: Record<string, string>
): UnifiedSanitizerResult {
  return unifiedSanitizeInput(value, inputType, schema);
}

// Backward compatibility - redirect to unified system
// Note: sanitizeInput is already exported above, this duplicate is removed
