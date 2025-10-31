# Generic Workflow Brick Architecture

## Problem
Current workflow has hardcoded step transitions and limited brick types. Need a flexible, configuration-driven system where:
- Backend defines workflow progression via JSON responses
- Frontend bricks are generic and reusable
- Everything is defined in workflow JSON configuration
- No hardcoded business logic in WorkflowEngine

## Proposed Brick Types

### 1. JSON Display Brick (`json_display`)
Receives JSON data and displays different parts as user/assistant messages.

**Configuration:**
```json
{
  "type": "json_display",
  "id": "display-music-request",
  "dataSource": "workflowData.musicRequest",
  "display": {
    "userFields": [
      { "key": "genre", "label": "Genre" },
      { "key": "bpm", "label": "BPM" }
    ],
    "assistantFields": [
      { "key": "generatedPrompt", "label": "Generated Prompt", "editable": true }
    ]
  },
  "actions": [
    {
      "label": "Confirm",
      "action": "confirm",
      "nextBrick": "generate-music-backend"
    },
    {
      "label": "Edit",
      "action": "edit",
      "enableEdit": true
    }
  ]
}
```

### 2. Backend Processing Brick (`backend_call`)
Triggers backend API call and optionally waits for response.

**Configuration:**
```json
{
  "type": "backend_call",
  "id": "generate-music-prompt",
  "endpoint": "/api/ai/generate-music-prompt",
  "method": "POST",
  "payload": {
    "genre": "{{workflowData.genre}}",
    "description": "{{workflowData.userInput}}"
  },
  "waitForResponse": true,
  "saveResponse": {
    "key": "generatedPrompt",
    "path": "data.prompt"
  },
  "onSuccess": {
    "nextBrick": "display-prompt-review"
  },
  "onError": {
    "message": "Failed to generate prompt",
    "retryable": true
  }
}
```

### 3. Waiting Brick (`waiting_display`)
Displays loading state while backend processes, then displays result based on response structure.

**Configuration:**
```json
{
  "type": "waiting_display",
  "id": "wait-for-music",
  "listenTo": "generate-music-backend",
  "loadingMessage": "Generating your music...",
  "estimatedTime": 60,
  "showProgress": true,
  "onResponse": {
    "success": {
      "displayAs": "media_player",
      "dataPath": "data.audioUrl",
      "message": "{{data.message}}",
      "actions": [
        {
          "label": "Confirm",
          "icon": "check",
          "nextStep": "video_generation"
        },
        {
          "label": "Regenerate",
          "icon": "refresh",
          "action": "retry",
          "retryBrick": "generate-music-backend"
        }
      ]
    },
    "error": {
      "message": "{{error.message}}",
      "retryable": true
    }
  }
}
```

### 4. Media Display Brick (`media_display`)
Generic brick for displaying any media type (audio, image, video).

**Configuration:**
```json
{
  "type": "media_display",
  "id": "display-generated-music",
  "mediaType": "audio",
  "dataSource": "workflowData.audioUrl",
  "controls": {
    "play": true,
    "seek": true,
    "volume": true,
    "download": false
  },
  "metadata": {
    "title": "{{workflowData.musicTitle}}",
    "description": "{{workflowData.musicDescription}}"
  },
  "actions": [
    {
      "label": "Confirm & Continue",
      "variant": "default",
      "nextStep": "video_generation"
    },
    {
      "label": "Regenerate",
      "variant": "outline",
      "icon": "refresh",
      "triggerBrick": "generate-music-backend"
    }
  ]
}
```

### 5. Confirmation Brick (`confirmation`)
Simple confirmation UI with customizable actions.

**Configuration:**
```json
{
  "type": "confirmation",
  "id": "confirm-music-prompt",
  "message": "Does this prompt look good?",
  "displayData": {
    "source": "workflowData.generatedPrompt",
    "editable": true
  },
  "actions": [
    {
      "label": "Yes, Generate Music",
      "variant": "default",
      "saveEdit": true,
      "nextBrick": "generate-music-backend"
    },
    {
      "label": "Regenerate Prompt",
      "variant": "outline",
      "triggerBrick": "generate-music-prompt"
    }
  ]
}
```

## Example Workflow Flow

### Music Generation Workflow

```json
{
  "id": "music-generation",
  "initialStep": "get_user_input",
  "steps": {
    "get_user_input": {
      "id": "get_user_input",
      "stepNumber": 1,
      "bricks": [
        {
          "type": "llm",
          "id": "music-prompt-input",
          "buttons": [
            {
              "label": "Generate with AI",
              "action": "ai_generation",
              "returnValue": "ai_generation"
            }
          ],
          "activatePrompt": true,
          "prompt": {
            "placeholder": "Describe the music you want...",
            "editable": true,
            "confirmRequired": true
          }
        }
      ],
      "nextStep": "generate_prompt",
      "assistantMessage": {
        "content": "Describe your music or let AI help you",
        "enablePromptInput": true,
        "enableFileInput": false
      }
    },
    
    "generate_prompt": {
      "id": "generate_prompt",
      "stepNumber": 2,
      "bricks": [
        {
          "type": "backend_call",
          "id": "gen-prompt-backend",
          "endpoint": "/api/ai/generate-music-prompt",
          "method": "POST",
          "payload": {
            "description": "{{workflowData.userInput}}"
          },
          "waitForResponse": true,
          "saveResponse": {
            "key": "generatedPrompt"
          }
        },
        {
          "type": "waiting_display",
          "id": "wait-prompt",
          "listenTo": "gen-prompt-backend",
          "loadingMessage": "Generating prompt...",
          "onResponse": {
            "nextBrick": "confirm-prompt"
          }
        }
      ],
      "nextStep": "confirm_prompt"
    },
    
    "confirm_prompt": {
      "id": "confirm_prompt",
      "stepNumber": 3,
      "bricks": [
        {
          "type": "json_display",
          "id": "display-prompt",
          "dataSource": "workflowData",
          "display": {
            "userFields": [
              { "key": "userInput", "label": "Your Description" }
            ],
            "assistantFields": [
              { "key": "generatedPrompt", "label": "Generated Prompt", "editable": true }
            ]
          }
        },
        {
          "type": "confirmation",
          "id": "confirm-prompt-btn",
          "message": "Ready to generate music with this prompt?",
          "actions": [
            {
              "label": "Generate Music",
              "nextStep": "generate_music"
            },
            {
              "label": "Edit Prompt",
              "enableEdit": "generatedPrompt"
            }
          ]
        }
      ],
      "nextStep": "generate_music"
    },
    
    "generate_music": {
      "id": "generate_music",
      "stepNumber": 4,
      "bricks": [
        {
          "type": "backend_call",
          "id": "gen-music-backend",
          "endpoint": "/api/ai/generate-music",
          "method": "POST",
          "payload": {
            "prompt": "{{workflowData.generatedPrompt}}"
          },
          "waitForResponse": true,
          "timeout": 300000,
          "saveResponse": {
            "key": "audioUrl",
            "path": "data.url"
          }
        },
        {
          "type": "waiting_display",
          "id": "wait-music",
          "listenTo": "gen-music-backend",
          "loadingMessage": "Generating your music...",
          "estimatedTime": 60,
          "showProgress": true,
          "onResponse": {
            "success": {
              "nextBrick": "display-music"
            }
          }
        }
      ],
      "nextStep": "display_music"
    },
    
    "display_music": {
      "id": "display_music",
      "stepNumber": 5,
      "bricks": [
        {
          "type": "media_display",
          "id": "music-player",
          "mediaType": "audio",
          "dataSource": "workflowData.audioUrl",
          "actions": [
            {
              "label": "Confirm & Continue",
              "nextStep": "video_generation"
            },
            {
              "label": "Regenerate",
              "icon": "refresh",
              "triggerBrick": "gen-music-backend"
            }
          ]
        }
      ],
      "nextStep": "video_generation"
    }
  }
}
```

## Implementation Plan

### Phase 1: Core Brick Infrastructure
1. Create base brick interfaces for new types
2. Implement BrickFactory extensions
3. Add WorkflowEngine support for brick-driven navigation

### Phase 2: Individual Brick Implementation
1. Implement `json_display` brick
2. Implement `backend_call` brick with waiting support
3. Implement `waiting_display` brick
4. Implement `media_display` brick
5. Implement `confirmation` brick

### Phase 3: WorkflowEngine Updates
1. Remove all hardcoded step transitions
2. Implement brick-driven navigation
3. Add support for brick-to-brick communication
4. Add event listening between bricks

### Phase 4: Backend Integration
1. Update backend to return standardized JSON responses
2. Include `nextBrick` or `nextStep` in responses
3. Add progress tracking for long-running operations

### Phase 5: Migration
1. Convert existing workflows to new brick system
2. Test all workflow paths
3. Remove legacy code

## Benefits

1. **Flexibility**: Any workflow pattern can be configured via JSON
2. **Reusability**: Bricks are generic and work across workflows
3. **Maintainability**: No business logic in WorkflowEngine
4. **Backend-Driven**: Backend controls flow based on results
5. **Testability**: Each brick can be tested independently
6. **Extensibility**: New brick types can be added easily

## Next Steps

1. Review and approve architecture
2. Create TypeScript interfaces for new brick types
3. Implement Phase 1 (Core Infrastructure)
4. Start with one complete flow (music generation) as proof of concept

