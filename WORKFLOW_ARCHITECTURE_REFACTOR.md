# Workflow Architecture Refactor

## Problem
The previous architecture had bricks directly injecting messages into the chat via React useEffect hooks, bypassing the workflow engine orchestration. This caused:
- Duplicate messages
- Lack of central control
- Difficult debugging
- Poor separation of concerns

## New Architecture

### Core Principle
**Workflow → Engine → Brick → Engine → Chat**

### Flow

```
1. Workflow JSON defines step structure
   ↓
2. Engine reads workflow and creates bricks
   ↓
3. Engine executes bricks
   ↓
4. Bricks return JSON output to engine
   ↓
5. Engine processes output (messages, navigation, save)
   ↓
6. Engine continues reading workflow
```

## Component Responsibilities

### 1. Workflow (JSON Configuration)
**Responsibility**: Define structure, not behavior

- Brick types to use
- Input data for each brick
- Decision tree / navigation
- Message content
- Button configurations

**Example**:
```json
{
  "id": "track-actions",
  "type": "llm",
  "buttons": [
    {
      "label": "Generate with AI",
      "action": "generateTrackWithAI",
      "returnValue": "ai_generation",
      "variant": "default",
      "userMessage": "I want to generate an AI track",
      "nextStep": "track_ai_description"
    }
  ],
  "assistantMessage": {
    "content": "Great! First, let's get your music track...",
    "showDelay": 1200,
    "enableFileInput": true,
    "enablePromptInput": true
  }
}
```

### 2. Engine (`WorkflowEngine.tsx`)
**Responsibility**: Orchestrate everything

**Tasks**:
- Load workflow configuration
- Create/retrieve project data
- Create brick instances
- Execute bricks in proper order
- **Process brick outputs** (NEW)
- **Inject messages based on brick output** (NEW)
- Handle navigation
- Auto-save to database
- Manage workflow state

**Key Changes**:
```typescript
// Engine now processes brick execution results
const result = await brick.execute();

// Engine injects messages based on brick output
if (result.success && result.data?.message) {
  const messageData = result.data.message;
  context.addAssistantMessageWithDelay({
    role: 'assistant',
    content: messageData.content,
    actionButtons: messageData.actionButtons,
    // ...
  }, messageData.showDelay);
}

// Engine injects user messages from button clicks
if (data.userMessage) {
  context.setMessages(prev => ([
    ...prev,
    {
      id: `user-${Date.now()}`,
      role: 'user',
      content: data.userMessage,
      timestamp: new Date()
    }
  ]));
}
```

### 3. Bricks (`LLMBrick.tsx`, etc.)
**Responsibility**: Process data and return JSON

**Tasks**:
- Receive configuration from workflow
- Process with their specificities
- **Return structured JSON output** (NEW)
- **NO direct message injection** (REMOVED)
- **NO direct navigation** (moved to engine)

**Key Changes**:

**Before (BAD)**:
```typescript
// Component directly injected messages - BYPASSED ENGINE
useEffect(() => {
  context.addAssistantMessageWithDelay({
    role: 'assistant',
    content: assistantText,
    //...
  }, delay);
}, []);
```

**After (GOOD)**:
```typescript
// Brick returns message data for engine to process
public async execute(): Promise<BrickExecutionResult> {
  return {
    success: true,
    data: {
      type: 'llm_brick_ready',
      // Engine will process this
      message: assistantMessage ? {
        role: 'assistant',
        content: assistantMessage,
        actionButtons,
        enableFileInput,
        enablePromptInput,
        showDelay
      } : null
    }
  };
}
```

**Button Click Handling**:
```typescript
// Brick returns data for engine to process
private handleButtonClick(buttonId: string): void {
  brickEventEmitter.emitComplete(this.id, undefined, {
    action: buttonId,
    returnValue: button.returnValue,
    userMessage: button.userMessage, // Engine will inject
    nextStep: button.nextStep // Engine will navigate
  });
}
```

## Communication Flow

### 1. Message Injection
```
Brick.execute() 
  → returns { data: { message: {...} } }
  → Engine receives
  → Engine calls context.addAssistantMessageWithDelay()
  → Message appears in chat
```

### 2. Button Click
```
User clicks button
  → Engine emits: button:brick-id:action
  → Brick listens and handles
  → Brick returns: { userMessage, nextStep, returnValue }
  → Engine injects user message
  → Engine navigates to nextStep
```

### 3. Multi-Step Bricks
```
Brick.execute()
  → returns { processing: true, message: "Step 1..." }
  → Engine injects message
  → Engine waits
  → Brick completes processing
  → Brick returns { processing: false, result: {...} }
  → Engine continues workflow
```

## Benefits

### ✅ Single Source of Truth
- Engine controls ALL chat messages
- No duplicate messages
- Predictable behavior

### ✅ Clean Separation
- Workflow = Data/Configuration
- Engine = Orchestration
- Bricks = Processing Logic

### ✅ Debuggable
- All messages flow through engine
- Easy to trace execution
- Clear event flow

### ✅ Testable
- Bricks return pure JSON
- Engine logic is centralized
- No hidden side effects

### ✅ Maintainable
- Changes in one place
- No scattered message injection
- Clear responsibilities

## Example Flow: Music Generation

### Step 1: Initial Message
```
1. Engine loads "track_input" step
2. Engine creates LLMBrick instance
3. Engine executes LLMBrick
4. LLMBrick returns:
   {
     data: {
       message: {
         content: "Great! First, let's get your music track...",
         actionButtons: [{label: "Generate with AI", action: "..."}]
       }
     }
   }
5. Engine receives output
6. Engine injects message into chat
7. User sees: "Great! First, let's get your music track..."
```

### Step 2: Button Click
```
1. User clicks "Generate with AI"
2. Engine emits: button:track-actions:generateTrackWithAI
3. LLMBrick receives event
4. LLMBrick processes and returns:
   {
     data: {
       action: "generateTrackWithAI",
       returnValue: "ai_generation",
       userMessage: "I want to generate an AI track",
       nextStep: "track_ai_description"
     }
   }
5. Engine receives output
6. Engine injects user message: "I want to generate an AI track"
7. Engine navigates to "track_ai_description" step
8. No duplicates!
```

## Files Modified

1. **`LLMBrick.tsx`**
   - Removed direct message injection from component
   - Added message data to execute() return value
   - Modified button handling to return data instead of inject

2. **`WorkflowEngine.tsx`**
   - Added message processing from brick outputs
   - Added user message injection from button clicks
   - Added button event emission system

3. **`music-clip-workflow.json`**
   - Fixed API endpoints
   - Added proper button navigation
   - Ensured proper workflow structure

## Migration Path

### For New Bricks
1. Return message data in `execute()` result
2. Return user actions in completion events
3. Let engine handle all message injection
4. Let engine handle all navigation

### For Existing Bricks
1. Identify direct message injection
2. Move to execute() return value
3. Remove useEffect hooks that inject messages
4. Update event listeners to return data

## Testing Checklist

- [x] No duplicate messages
- [x] Messages appear in correct order
- [x] Button clicks work properly
- [x] Navigation works correctly
- [x] User messages appear when expected
- [x] Assistant messages appear with delay
- [x] Auto-save works correctly
- [x] Workflow state is maintained

---

**Status**: ✅ Architecture refactored and tested
**Date**: 2025-10-31
**Principle**: Workflow defines structure, Engine orchestrates, Bricks process

