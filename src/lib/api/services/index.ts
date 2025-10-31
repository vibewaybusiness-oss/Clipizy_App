// API SERVICES BARREL EXPORT
export { musicService } from '../music';
export { projectsService } from '../projects';
export { pricingService } from '../pricing';
export { authService } from '../auth';

// Re-export base classes for custom services
export { BaseApiClient, ApiError } from '../base';
export type { ApiResponse, ApiError as ApiErrorType } from '../base';
