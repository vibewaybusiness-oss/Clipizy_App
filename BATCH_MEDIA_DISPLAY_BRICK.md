# BatchMediaDisplayBrick - Sequential Media Generation with Validation

## Overview

The `BatchMediaDisplayBrick` is a powerful brick that generates multiple media items sequentially (text, images, audio, video) and displays them with individual validation/regeneration controls. Each item can be edited, validated, or regenerated, with visual feedback and pricing information.

## Features

### ✨ Multi-Media Support
- **Text**: Editable text with inline editing
- **Image**: Full-size image display
- **Audio**: Playable audio with controls
- **Video**: Playable video with controls

### ✨ Individual Item Controls
- **Edit**: Edit text content inline (text type only)
- **Regenerate**: Regenerate any media item with pricing display
- **Validate**: Mark item as validated (green border)

### ✨ Visual Status Indicators
- **Generating** (Gray): Item is being generated
- **Ready** (Blue): Item is generated and ready for review
- **Regenerating** (Orange): Item is being regenerated
- **Validated** (Green): Item has been approved

### ✨ Pricing Integration
- Displays regeneration cost per item
- Fetches prices from workflow data using templates: `{{$image_generation_price}}`

### ✨ Sequential Generation
- Generates items one by one
- Shows progress bar during generation
- Real-time updates as each item completes

### ✨ Batch Validation
- "Validate All & Continue" button appears when all items are ready
- Automatically saves validated items to workflow data
- Proceeds to next step after validation

## Configuration

### TypeScript Interface

```typescript
export interface BatchMediaDisplayBrickConfig extends BaseBrickConfig {
  type: 'batch_media_display';
  generations: Array<{
    mediaType: 'text' | 'image' | 'audio' | 'video';
    label?: string;
    endpoint: string;
    payload?: Record<string, any>;
    contentPath?: string; // Path to extract content from response, default: 'url'
    regenerationPrice?: string; // Template like "{{$image_generation_price}}"
  }>;
  saveKey?: string; // Key to save validated media in workflowData, default: 'generatedMedia'
  onComplete?: {
    nextStep?: string;
    message?: string;
  };
}
```

### JSON Configuration Example

```json
{
  "type": "batch_media_display",
  "id": "batch-scene-generation",
  "generations": [
    {
      "mediaType": "text",
      "label": "Scene 1 Description",
      "endpoint": "/api/ai/generate-scene-description",
      "payload": {
        "scene_number": 1,
        "project_id": "{{workflowData.project_id}}",
        "context": "{{workflowData.videoContext}}"
      },
      "contentPath": "description",
      "regenerationPrice": "{{$text_generation_price}}"
    },
    {
      "mediaType": "image",
      "label": "Scene 1 Visual",
      "endpoint": "/api/ai/generate-scene-image",
      "payload": {
        "scene_number": 1,
        "description": "{{workflowData.scene1Description}}",
        "project_id": "{{workflowData.project_id}}"
      },
      "contentPath": "image_url",
      "regenerationPrice": "{{$image_generation_price}}"
    },
    {
      "mediaType": "video",
      "label": "Scene 1 Video",
      "endpoint": "/api/ai/generate-scene-video",
      "payload": {
        "scene_number": 1,
        "image_url": "{{workflowData.scene1ImageUrl}}",
        "project_id": "{{workflowData.project_id}}"
      },
      "contentPath": "video_url",
      "regenerationPrice": "{{$video_generation_price}}"
    }
  ],
  "saveKey": "validatedScenes",
  "onComplete": {
    "nextStep": "combine_video",
    "message": "All scenes validated! Creating final video..."
  }
}
```

## Template Variables

### Standard Variables
Use `{{workflowData.field}}` to access any workflow data:
```json
{
  "payload": {
    "project_id": "{{workflowData.project_id}}",
    "user_input": "{{workflowData.userDescription}}"
  }
}
```

### Pricing Variables
Use `{{$pricing_key}}` to access pricing data:
- `{{$text_generation_price}}`
- `{{$image_generation_price}}`
- `{{$audio_generation_price}}`
- `{{$video_generation_price}}`

The brick will look for these in `workflowData.pricing`:
```json
{
  "workflowData": {
    "pricing": {
      "text_generation_price": 0.01,
      "image_generation_price": 0.05,
      "audio_generation_price": 0.10,
      "video_generation_price": 0.50
    }
  }
}
```

## Backend Response Format

Each generation endpoint should return a response containing the media URL or content:

### Text Response
```json
{
  "success": true,
  "description": "A sunny beach scene with waves crashing...",
  "model": "gpt-4"
}
```

### Image Response
```json
{
  "success": true,
  "image_url": "https://s3.amazonaws.com/.../scene1.jpg",
  "width": 1024,
  "height": 1024
}
```

### Audio Response
```json
{
  "success": true,
  "audio_url": "https://s3.amazonaws.com/.../track.mp3",
  "duration": 180
}
```

### Video Response
```json
{
  "success": true,
  "video_url": "https://s3.amazonaws.com/.../scene1.mp4",
  "duration": 30,
  "resolution": "1920x1080"
}
```

## Content Path Extraction

Use `contentPath` to specify which field contains the media URL/content:

```json
{
  "contentPath": "image_url"  // Extracts response.image_url
}
```

For nested paths:
```json
{
  "contentPath": "data.media.url"  // Extracts response.data.media.url
}
```

Default is `"url"` if not specified.

## Usage Flow

### 1. Generation Phase
```
[Generating 1/3] ━━━━━━━━━░░░░░░░░░░ 33%
  └─ Text: Generating...
  └─ Image: Pending...
  └─ Video: Pending...
```

### 2. Review Phase
```
┌──────────────────────────────┐
│ ✓ Text: "Beach scene..."     │
│   [Edit] [Regenerate $0.01]  │
│   [✓ Validate]                │
└──────────────────────────────┘

┌──────────────────────────────┐
│ 🖼️ Image: [Beach.jpg]         │
│   [Regenerate $0.05]          │
│   [✓ Validate]                │
└──────────────────────────────┘

┌──────────────────────────────┐
│ 🎬 Video: [Player controls]   │
│   [Regenerate $0.50]          │
│   [✓ Validate]                │
└──────────────────────────────┘

[✓ Validate All & Continue]
```

### 3. Status Colors

| Status | Border Color | Description |
|--------|-------------|-------------|
| Generating | Gray | Item is being created |
| Ready | Blue | Item ready for review |
| Regenerating | Orange | Item is being recreated |
| Validated | Green | Item approved |

## User Actions

### Edit (Text Only)
1. Click "Edit" button
2. Modify text in textarea
3. Click "Save" to confirm
4. Status returns to "Ready"

### Regenerate (All Types)
1. Click "Regenerate" button (shows price)
2. Item status changes to orange
3. New generation starts
4. Status returns to "Ready" when complete

### Validate (All Types)
1. Click "Validate" button
2. Item status changes to green
3. Border becomes green
4. Checkmark icon appears

### Validate All
1. Appears when all items are generated
2. Validates all non-validated items
3. Saves to workflow data
4. Proceeds to next step

## Saved Data Structure

After validation, data is saved to `workflowData[saveKey]`:

```json
{
  "validatedScenes": [
    {
      "id": "batch-scene-generation-media-0",
      "type": "text",
      "content": "A sunny beach scene...",
      "status": "validated"
    },
    {
      "id": "batch-scene-generation-media-1",
      "type": "image",
      "content": "https://s3.amazonaws.com/.../scene1.jpg",
      "status": "validated"
    },
    {
      "id": "batch-scene-generation-media-2",
      "type": "video",
      "content": "https://s3.amazonaws.com/.../scene1.mp4",
      "status": "validated"
    }
  ]
}
```

## Complete Example Workflow

See `/api/services/chatbot/configs/video-generation-batch-example.json` for a complete working example that:

1. Generates 6 media items (2 scenes × 3 items each)
2. Each scene has: Description (text), Visual (image), Video
3. Shows pricing for each regeneration
4. Validates all items
5. Combines validated scenes into final video

## Integration with Other Bricks

### After BatchMediaDisplay
```json
{
  "type": "backend_call",
  "endpoint": "/api/ai/combine-scenes",
  "payload": {
    "scenes": "{{workflowData.validatedScenes}}"
  }
}
```

### Before BatchMediaDisplay (Setup Pricing)
```json
{
  "type": "backend_call",
  "endpoint": "/api/credits/pricing",
  "saveResponse": {
    "key": "pricing"
  }
}
```

## Advanced Features

### Dynamic Generation Count
The number of generations is determined by the `generations` array length. You can dynamically generate this in your backend based on user input.

### Conditional Pricing
```json
{
  "regenerationPrice": "{{$premium_enabled ? $premium_price : $standard_price}}"
}
```

### Cross-Item Dependencies
Use previously generated items in subsequent payloads:
```json
{
  "generations": [
    {
      "mediaType": "text",
      "endpoint": "/api/generate-description"
    },
    {
      "mediaType": "image",
      "payload": {
        "description": "{{workflowData.scene1Description}}"
      }
    }
  ]
}
```

## Best Practices

1. **Keep Generations Sequential**: Items generate one at a time for better UX
2. **Provide Clear Labels**: Use descriptive labels for each generation
3. **Set Realistic Pricing**: Display accurate regeneration costs
4. **Use Progress Indicators**: Users see exactly where they are in the process
5. **Validate Before Proceeding**: Don't skip validation step for quality control

## Files

- **Implementation**: `src/app/dashboard/create/workflows/bricks/BatchMediaDisplayBrick.tsx`
- **Type Definition**: `src/types/workflow.ts` (BatchMediaDisplayBrickConfig)
- **Factory Registration**: `src/app/dashboard/create/workflows/bricks/BrickFactory.ts`
- **Renderer**: `src/app/dashboard/create/workflows/components/BrickRenderer.tsx`
- **Example**: `api/services/chatbot/configs/video-generation-batch-example.json`

---

**Status**: ✅ Complete and ready for use

