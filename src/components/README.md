# Components Directory Structure

This directory contains all React components organized by functionality and purpose.

## Directory Structure

```
src/components/
├── ui/                          # shadcn/ui components (unchanged)
├── layout/                      # Layout-related components
│   ├── navigation.tsx
│   ├── footer.tsx
│   ├── conditional-layout.tsx
│   ├── protected-route.tsx
│   └── admin-route.tsx
├── common/                      # Shared/common components
│   ├── info-popup.tsx
│   ├── music-logo.tsx
│   ├── clipizy-logo.tsx
│   ├── video-theater.tsx
│   ├── timeline-header.tsx
│   └── user-profile.tsx
├── features/                    # Feature-specific components
│   ├── admin/
│   ├── blog/
│   ├── music-clip/
│   ├── projects/
│   ├── social-media/
│   └── calendar/
├── forms/                       # Form-related components
│   ├── BudgetSlider.tsx
│   ├── StepNavigation.tsx
│   ├── generators/
│   │   ├── ClipizyGenerator.tsx
│   │   └── ClipizyGenerator.tsx
│   └── [step components]
├── types/                       # TypeScript type definitions
│   ├── clipizy.types.ts
│   └── waveform.types.ts
├── hooks/                       # Custom React hooks
│   └── useWaveformVisualizer.ts
├── utils/                       # Utility functions
│   ├── clipizy.utils.ts
│   └── waveform.utils.ts
└── index.ts                     # Main barrel export
```

## Naming Conventions

- **Component files**: PascalCase (e.g., `BudgetSlider.tsx`)
- **Hook files**: camelCase with `use` prefix (e.g., `useWaveformVisualizer.ts`)
- **Utility files**: camelCase with `.utils.ts` suffix (e.g., `pricing.utils.ts`)
- **Type files**: camelCase with `.types.ts` suffix (e.g., `clipizy.types.ts`)

## Component Organization

### Layout Components
Components that handle overall page layout and navigation.

### Common Components
Reusable components used across multiple features.

### Feature Components
Components specific to particular features, organized by domain.

### Form Components
Components related to forms, including multi-step forms and generators.

### UI Components
Base UI components from shadcn/ui library.

## Type Definitions

All TypeScript interfaces and types are centralized in the `types/` directory for better maintainability.

## Custom Hooks

Business logic has been extracted into custom hooks in the `hooks/` directory to improve reusability and testability.

## Utility Functions

Pure utility functions are organized in the `utils/` directory.

## Barrel Exports

Each directory has an `index.ts` file that exports all components, making imports cleaner:

```typescript
// Instead of:
import { BudgetSlider } from '@/components/forms/BudgetSlider';

// You can now use:
import { BudgetSlider } from '@/components';
```

## Benefits of This Structure

1. **Better Organization**: Components are grouped by purpose and functionality
2. **Improved Maintainability**: Smaller, focused components are easier to maintain
3. **Enhanced Reusability**: Composable components can be reused across features
4. **Better Type Safety**: Centralized type definitions
5. **Cleaner Imports**: Barrel exports simplify import statements
6. **Easier Testing**: Isolated business logic in custom hooks
7. **Scalability**: Organized structure supports future growth

## Migration Notes

- Large components have been broken down into smaller, focused components
- Business logic has been extracted into custom hooks
- Type definitions have been centralized
- All components follow consistent naming conventions
- Barrel exports provide clean import paths
