# Bricks Architecture Guide

## Overview

Bricks are modular, reusable components that perform specific tasks within a workflow. The engine orchestrates bricks based on workflow configuration, and bricks return structured JSON data back to the engine.

## Core Principle

**Bricks process data and return JSON. Engine handles all UI updates.**

```
Workflow Config → Engine → Brick.execute() → Returns JSON → Engine processes → UI updates
```

## Brick Lifecycle

### 1. Creation
```typescript
constructor(config: BrickConfig, context: BrickContext) {
  this.id = config.id;
  this.config = config as SpecificBrickConfig;
  this.context = context;
  // Initialize state
  // Set up event listeners if needed
}
```

### 2. Execution
```typescript
public async execute(): Promise<BrickExecutionResult> {
  try {
    // Process according to brick's purpose
    // Return structured data for engine
    return {
      success: true,
      data: {
        // Any data engine needs to process
        message?: { ... }, // For LLM bricks
        processing?: boolean, // For multi-step bricks
        result?: any
      }
    };
  } catch (error) {
    return {
      success: false,
      error: error as Error
    };
  }
}
```

### 3. Component Rendering
```typescript
export const BrickComponent: React.FC<Props> = ({ brick, onComplete, onError, context }) => {
  // If brick has UI (user_input, json_display, media_display, etc.)
  // Render the UI
  
  // If brick has no UI (llm, background, backend_call)
  // Return null - engine handles everything
  
  return null; // or <UI />
};
```

## Brick Types

### 1. LLMBrick (No UI - Engine Controlled)
**Purpose**: Present messages and action buttons to users

**Architecture**:
- ❌ Does NOT directly inject messages
- ✅ Returns message data in `execute()`
- ✅ Engine injects the message
- ✅ Engine handles button clicks
- ✅ Component returns `null`

**Example**:
```typescript
public async execute(): Promise<BrickExecutionResult> {
  return {
    success: true,
    data: {
      message: {
        role: 'assistant',
        content: this.config.assistantMessage?.content,
        actionButtons: this.config.buttons,
        enableFileInput: this.config.assistantMessage?.enableFileInput,
        enablePromptInput: this.config.assistantMessage?.enablePromptInput,
        showDelay: this.config.assistantMessage?.showDelay
      }
    }
  };
}
```

### 2. UserInputBrick (Has UI)
**Purpose**: Collect file uploads or form inputs

**Architecture**:
- ✅ Renders file upload UI or form inputs
- ✅ Waits for user action
- ✅ Returns collected data when complete

**Files**: `UserInputBrick.tsx`

### 3. BackendCallBrick (No UI - Engine Controlled)
**Purpose**: Make API calls to backend

**Architecture**:
- ❌ Does NOT render UI
- ✅ Makes HTTP request
- ✅ Returns response data
- ✅ Can be manually triggered via events
- ✅ Supports `autoExecute` flag

**Key Features**:
- Template interpolation: `{{workflowData.field}}`
- Response path extraction
- Timeout handling
- Auto-execution control

**Files**: `BackendCallBrick.tsx`

### 4. WaitingDisplayBrick (Has UI)
**Purpose**: Show loading state while waiting for another brick

**Architecture**:
- ✅ Renders progress indicator
- ✅ Listens to another brick's events
- ✅ Updates based on that brick's status
- ✅ Shows estimated time

**Files**: `WaitingDisplayBrick.tsx`

### 5. JSONDisplayBrick (Has UI)
**Purpose**: Display JSON data with optional editing

**Architecture**:
- ✅ Renders JSON fields as messages
- ✅ Supports inline editing
- ✅ Can trigger other bricks
- ✅ Handles user/assistant field display

**Files**: `JSONDisplayBrick.tsx`

### 6. MediaDisplayBrick (Has UI)
**Purpose**: Display audio, video, or images

**Architecture**:
- ✅ Renders media player
- ✅ Supports playback controls
- ✅ Shows metadata
- ✅ Handles user actions

**Files**: `MediaDisplayBrick.tsx`

### 7. BatchMediaDisplayBrick (Has UI)
**Purpose**: Generate and display multiple media items sequentially

**Architecture**:
- ✅ Generates items one by one
- ✅ Shows progress
- ✅ Allows individual validation/regeneration
- ✅ Batch validation
- ✅ Supports text (editable), image, audio, video

**Files**: `BatchMediaDisplayBrick.tsx`

### 8. ConfirmationBrick (Has UI)
**Purpose**: Present confirmation choices to user

**Architecture**:
- ✅ Renders message and buttons
- ✅ Can display data for review
- ✅ Handles user confirmation

**Files**: `ConfirmationBrick.tsx`

### 9. BackgroundBrick (No UI - Silent)
**Purpose**: Run operations silently in background

**Architecture**:
- ❌ Never renders UI
- ✅ Executes asynchronously
- ✅ Does not block workflow
- ✅ Reports completion via events

**Files**: `BackgroundBrick.tsx`

### 10. APICallBrick (Has UI - Deprecated)
**Purpose**: Legacy API call brick (use BackendCallBrick instead)

**Status**: Being phased out in favor of BackendCallBrick

**Files**: `APICallBrick.tsx`

## BrickRenderer

**Location**: `src/app/dashboard/create/workflows/components/BrickRenderer.tsx`

**Purpose**: Dynamically render brick components based on type

```typescript
export function BrickRenderer({ brick, onAction, onComplete, onError, context }) {
  // Never render silent bricks
  if (brick.type === 'background') {
    return null;
  }

  switch (brick.type) {
    case 'llm':
      return <LLMBrickComponent brick={brick} ... />;
    case 'user_input':
      return <UserInputBrickComponent brick={brick} ... />;
    case 'json_display':
      return <JSONDisplayBrickComponent brick={brick} ... />;
    case 'backend_call':
      return <BackendCallBrickComponent brick={brick} ... />;
    case 'waiting_display':
      return <WaitingDisplayBrickComponent brick={brick} ... />;
    case 'media_display':
      return <MediaDisplayBrickComponent brick={brick} ... />;
    case 'batch_media_display':
      return <BatchMediaDisplayBrickComponent brick={brick} ... />;
    case 'confirmation':
      return <ConfirmationBrickComponent brick={brick} ... />;
    default:
      return <div>Unknown brick type: {brick.type}</div>;
  }
}
```

## BrickFactory

**Location**: `src/app/dashboard/create/workflows/bricks/BrickFactory.ts`

**Purpose**: Create brick instances dynamically

```typescript
public async create(config: BrickConfig, context: BrickContext): Promise<BrickInstance> {
  await this.loadDefaultBricks();
  
  const creator = this.brickTypes.get(config.type);
  if (!creator) {
    throw new Error(`Unknown brick type: ${config.type}`);
  }
  
  return creator(config, context);
}
```

## Common Patterns

### 1. Returning Message Data (LLM Bricks)
```typescript
return {
  success: true,
  data: {
    message: {
      role: 'assistant',
      content: 'Message text',
      actionButtons: [...],
      enableFileInput: true,
      enablePromptInput: false
    }
  }
};
```

### 2. Returning User Action Data (Button Clicks)
```typescript
brickEventEmitter.emitComplete(this.id, undefined, {
  action: buttonId,
  returnValue: button.returnValue,
  userMessage: button.userMessage, // Engine will inject
  nextStep: button.nextStep // Engine will navigate
});
```

### 3. Template Interpolation
```typescript
private interpolateTemplate(template: string): string {
  return template.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
    const cleanPath = path.trim().replace(/^workflowData\./, '');
    const keys = cleanPath.split('.');
    let value = this.context.workflowData;
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        return match;
      }
    }
    
    return String(value);
  });
}
```

### 4. Event Listening
```typescript
// Listen for external triggers
brickEventEmitter.on(`trigger:${this.id}`, () => {
  this.execute();
});

// Listen for data from other bricks
brickEventEmitter.on(`data:${otherBrickId}`, (data) => {
  // Process data
});
```

### 5. Multi-Step Processing
```typescript
public async execute(): Promise<BrickExecutionResult> {
  // Step 1: Start processing
  brickEventEmitter.emitData(this.id, { processing: true, step: 1 });
  
  const result = await this.processStep1();
  
  // Step 2: Continue processing
  brickEventEmitter.emitData(this.id, { processing: true, step: 2 });
  
  const finalResult = await this.processStep2(result);
  
  // Complete
  return {
    success: true,
    data: { processing: false, result: finalResult }
  };
}
```

## Best Practices

### ✅ DO

1. **Return Structured Data**: Always return proper `BrickExecutionResult`
2. **Use Event Emitters**: Communicate via events, not direct calls
3. **Template Variables**: Support `{{workflowData.field}}` patterns
4. **Error Handling**: Always catch and return errors properly
5. **Validation**: Implement `validate()` method
6. **State Management**: Use internal state, emit changes via events
7. **Cleanup**: Implement `destroy()` for cleanup

### ❌ DON'T

1. **Direct Message Injection**: Never call `context.setMessages()` or `context.addAssistantMessageWithDelay()` directly from bricks
2. **Direct Navigation**: Never call `context.setStep()` directly from execute()
3. **Side Effects**: Don't modify external state directly
4. **Blocking Operations**: Don't block the event loop
5. **Hardcoded Values**: Always use config and workflow data

## Event System

### Standard Events

```typescript
// Completion
brickEventEmitter.emitComplete(brickId, metadata, data);

// Error
brickEventEmitter.emitError(brickId, metadata, error);

// Data updates
brickEventEmitter.emitData(brickId, metadata, data);

// Status changes
brickEventEmitter.emitStatus(brickId, metadata, status);

// Custom events
brickEventEmitter.emit(`custom:${brickId}:event`, data);
```

### Listening to Events

```typescript
const subscriptionId = brickEventEmitter.on(`event:${brickId}`, (data) => {
  // Handle event
});

// Cleanup
brickEventEmitter.offById(subscriptionId);
```

## Testing Checklist

- [ ] Brick executes without errors
- [ ] Returns proper `BrickExecutionResult` structure
- [ ] Handles errors gracefully
- [ ] Emits proper events
- [ ] Component renders correctly (or returns null)
- [ ] No direct message injection
- [ ] No direct navigation
- [ ] Proper cleanup on destroy
- [ ] Template interpolation works
- [ ] Event listeners are cleaned up

## File Structure

```
src/app/dashboard/create/workflows/bricks/
├── LLMBrick.tsx               # Message & button brick
├── UserInputBrick.tsx         # File/form input brick
├── BackendCallBrick.tsx       # API call brick
├── BackgroundBrick.tsx        # Silent background brick
├── JSONDisplayBrick.tsx       # JSON display/edit brick
├── MediaDisplayBrick.tsx      # Media player brick
├── BatchMediaDisplayBrick.tsx # Batch media generation brick
├── WaitingDisplayBrick.tsx    # Loading/waiting brick
├── ConfirmationBrick.tsx      # Confirmation dialog brick
├── BrickFactory.ts            # Brick creation factory
├── BrickEventEmitter.ts       # Event system
├── BrickError.ts              # Error handling
├── BrickUtils.ts              # Utility functions
├── BrickValidation.ts         # Validation rules
├── BrickRegistry.ts           # Brick registration
└── index.ts                   # Exports
```

## Migration Guide

### From Old Architecture

**Before (BAD)**:
```typescript
// Component directly injected messages
useEffect(() => {
  context.addAssistantMessageWithDelay({
    role: 'assistant',
    content: 'Hello'
  });
}, []);
```

**After (GOOD)**:
```typescript
// Brick returns message data
public async execute(): Promise<BrickExecutionResult> {
  return {
    success: true,
    data: {
      message: {
        role: 'assistant',
        content: 'Hello'
      }
    }
  };
}

// Component returns null
return null;
```

---

**Status**: ✅ All bricks refactored to new architecture
**Date**: 2025-10-31
**Principle**: Bricks process, Engine orchestrates, No direct side effects

