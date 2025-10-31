// formatTime - use @/lib/utils instead

export const generateWaveformData = async (file: File): Promise<number[]> => {
  const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
  const arrayBuffer = await file.arrayBuffer();
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
  const channelData = audioBuffer.getChannelData(0);
  const samples = 400; // Number of bars we want to show
  const blockSize = Math.floor(channelData.length / samples);
  const waveform: number[] = [];
  
  for (let i = 0; i < samples; i++) {
    const start = blockSize * i;
    let sum = 0;
    for (let j = 0; j < blockSize; j++) {
      sum += Math.abs(channelData[start + j]);
    }
    waveform.push(sum / blockSize);
  }
  
  const max = Math.max(...waveform);
  return waveform.map(v => v / max);
};

export const drawWaveform = (
  canvas: HTMLCanvasElement,
  waveformData: number[],
  currentTime: number,
  duration: number,
  scenes: any[] = [],
  currentSegmentId: number | null = null,
  zoomStart: number = 0,
  zoomEnd: number = 1
) => {
  if (!canvas || !waveformData.length || duration === 0) return;
  
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  
  // Only resize canvas if dimensions changed
  if (canvas.width !== rect.width * dpr || canvas.height !== rect.height * dpr) {
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
  }

  const width = rect.width;
  const height = rect.height;

  ctx.clearRect(0, 0, width, height);

  // Cache colors to avoid repeated DOM queries
  const style = getComputedStyle(document.documentElement);
  const waveColor = `hsl(${style.getPropertyValue('--muted-foreground').trim()})`;
  const progressColor = `hsl(${style.getPropertyValue('--primary').trim()})`;
  const backgroundColor = `hsl(${style.getPropertyValue('--secondary').trim()})`;
  const segmentColor = `hsl(${style.getPropertyValue('--accent').trim()})`;

  ctx.fillStyle = backgroundColor;
  ctx.fillRect(0, 0, width, height);

  const zoomWidth = zoomEnd - zoomStart;
  const startIndex = Math.floor(zoomStart * waveformData.length);
  const endIndex = Math.floor(zoomEnd * waveformData.length);
  const visibleData = waveformData.slice(startIndex, endIndex);
  
  const barWidth = width / visibleData.length;
  const barGap = 1;
  const centerY = height / 2;

  const playheadX = ((currentTime / duration) - zoomStart) / zoomWidth * width;

  // Pre-calculate segment boundaries for performance
  let currentScene: any = null;
  let segmentEnd = duration;
  if (currentSegmentId) {
    currentScene = scenes.find(s => s.id === currentSegmentId);
    if (currentScene) {
      const nextScene = scenes.find(s => s.startTime > currentScene.startTime);
      segmentEnd = nextScene ? nextScene.startTime : duration;
    }
  }

  // Draw waveform bars
  for (let i = 0; i < visibleData.length; i++) {
    const x = i * barWidth;
    const barHeight = visibleData[i] * height;
    const globalIndex = startIndex + i;
    const globalTime = (globalIndex / waveformData.length) * duration;

    let fillColor = waveColor;
    if (x < playheadX) {
      fillColor = progressColor;
    } else if (currentScene && globalTime >= currentScene.startTime && globalTime < segmentEnd) {
      fillColor = segmentColor;
    }

    ctx.fillStyle = fillColor;
    ctx.fillRect(x, centerY - barHeight / 2, barWidth - barGap, barHeight);
  }

  // Draw segment background overlay
  if (currentScene) {
    const segmentStartX = ((currentScene.startTime / duration) - zoomStart) / zoomWidth * width;
    const segmentEndX = ((segmentEnd / duration) - zoomStart) / zoomWidth * width;
    
    if (segmentStartX >= 0 && segmentStartX <= width) {
      ctx.fillStyle = segmentColor + '20';
      ctx.fillRect(segmentStartX, 0, segmentEndX - segmentStartX, height);
    }
  }
};
