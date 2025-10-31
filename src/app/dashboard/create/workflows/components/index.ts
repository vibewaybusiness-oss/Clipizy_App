// =========================
// WORKFLOW COMPONENTS EXPORTS
// =========================

// Core components
export { BrickRenderer } from './BrickRenderer';
export { componentRegistry } from './ComponentRegistry';
export { ModalProvider, useModal, ModalTypes } from './ModalSystem';
export { OverlayGateway } from './OverlayGateway';

// Re-export types
export type { BrickComponentProps, BrickComponent } from './ComponentRegistry';
export type { ModalType } from './ModalSystem';