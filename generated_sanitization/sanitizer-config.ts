// Generated TypeScript sanitization configuration
// This file is auto-generated from Python unified sanitizer

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
  allowedExtensions: string[];
  allowedContentTypes: string[];
  maxFileSize: number;
  customPatterns: string[];
  level: string;
}

export interface SanitizationPatterns {
  controlChars: RegExp[];
  unicodeAbuse: RegExp[];
  sqlInjection?: RegExp[];
  xss?: RegExp[];
  pathTraversal?: RegExp[];
  commandInjection?: RegExp[];
  ldapInjection?: RegExp[];
  noSqlInjection?: RegExp[];
  custom?: RegExp[];
}

// Configuration for moderate sanitization level
export const sanitizerConfig: SanitizerConfig = {
  "maxLength": 10000,
  "allowHtml": false,
  "allowScripts": false,
  "allowSqlKeywords": false,
  "stripWhitespace": true,
  "normalizeUnicode": true,
  "removeControlChars": true,
  "allowedTags": [],
  "allowedAttributes": [],
  "allowedExtensions": [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".txt", ".mp3", ".wav", ".mp4", ".avi"],
  "allowedContentTypes": ["image/jpeg", "image/png", "image/gif", "application/pdf", "text/plain", "audio/mpeg", "audio/wav", "video/mp4", "video/avi"],
  "maxFileSize": 10485760,
  "customPatterns": [],
  "level": "moderate"
};

// Compiled regex patterns
export const sanitizationPatterns: SanitizationPatterns = {
  controlChars: [
    /[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/gi,
  ],
  unicodeAbuse: [
    /[\u200B-\u200D\uFEFF]/gi,
    /[\u2028\u2029]/gi,
    /[\u2060-\u2064]/gi,
  ],
  sqlInjection: [
    /(union|select|insert|update|delete|drop|create|alter|exec|execute)/gi,
    /(or|and)\s+\d+\s*=\s*\d+/gi,
    /('|"|;|--|\/\*|\*\/)/gi,
    /(xp_|sp_|fn_)/gi,
    /(waitfor|delay|sleep)/gi,
    /(load_file|into\s+outfile|into\s+dumpfile)/gi,
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
    /\.\.\//gi,
    /\.\.\\/gi,
    /%2e%2e%2f/gi,
    /%2e%2e%5c/gi,
    /\.\.%2f/gi,
    /\.\.%5c/gi,
    /%252e%252e%252f/gi,
    /%252e%252e%255c/gi,
  ],
  commandInjection: [
    /[;&|`$]/gi,
    /(cmd|command|exec|system|shell)/gi,
    /(powershell|bash|sh|cmd)/gi,
    /`[^`]*`/gi,
    /\$\([^)]*\)/gi,
    /<[^>]*>/gi,
  ],
};
