export const voiceTypes = [
  {
    id: "historical",
    name: "Historical",
    description: "Deep, authoritative, like a documentary narrator",
    icon: "📜",
    gradient: "from-amber-500/20 to-orange-500/20",
    preview: "In the year 1066, William the Conqueror crossed the English Channel...",
    available: true
  },
  {
    id: "storytelling",
    name: "Storytelling",
    description: "Warm, engaging, perfect for narratives",
    icon: "📖",
    gradient: "from-blue-500/20 to-indigo-500/20",
    preview: "Once upon a time, in a land far, far away...",
    available: true
  },
  {
    id: "dynamic",
    name: "Dynamic",
    description: "Energetic, exciting, great for action content",
    icon: "⚡",
    gradient: "from-yellow-500/20 to-red-500/20",
    preview: "Get ready for the most incredible adventure of your life!",
    available: true
  },
  {
    id: "professional",
    name: "Professional",
    description: "Clear, confident, ideal for business content",
    icon: "💼",
    gradient: "from-slate-500/20 to-gray-500/20",
    preview: "Today we'll be discussing the quarterly financial results...",
    available: true
  },
  {
    id: "casual",
    name: "Casual",
    description: "Relaxed, friendly, conversational tone",
    icon: "😊",
    gradient: "from-green-500/20 to-emerald-500/20",
    preview: "Hey there! So today I wanted to chat with you about...",
    available: true
  },
  {
    id: "dramatic",
    name: "Dramatic",
    description: "Expressive, theatrical, perfect for entertainment",
    icon: "🎭",
    gradient: "from-purple-500/20 to-pink-500/20",
    preview: "The stage is set, the audience waits with bated breath...",
    available: true
  },
  {
    id: "educational",
    name: "Educational",
    description: "Clear, patient, great for tutorials",
    icon: "🎓",
    gradient: "from-cyan-500/20 to-blue-500/20",
    preview: "Let's break this down step by step. First, we need to...",
    available: true
  },
  {
    id: "mysterious",
    name: "Mysterious",
    description: "Intriguing, captivating, perfect for suspense",
    icon: "🌙",
    gradient: "from-indigo-500/20 to-purple-500/20",
    preview: "In the shadows of the night, secrets whisper...",
    available: true
  },
  {
    id: "clone-voice",
    name: "Clone Voice",
    description: "Clone a voice from audio file",
    icon: "🎵",
    gradient: "from-pink-500/20 to-rose-500/20",
    preview: "Upload an audio file to clone this voice",
    available: false,
    comingSoonText: "Voice cloning coming soon",
    onNewsletterSignup: (email: string) => console.log(`Voice cloning signup: ${email}`)
  }
];

export const voiceCharacteristics = [
  {
    id: "male",
    name: "Male",
    description: "Deep, masculine voice characteristics",
    icon: "👨",
    gradient: "from-blue-500/20 to-cyan-500/20"
  },
  {
    id: "female",
    name: "Female",
    description: "Clear, feminine voice characteristics",
    icon: "👩",
    gradient: "from-pink-500/20 to-rose-500/20"
  },
  {
    id: "neutral",
    name: "Neutral",
    description: "Gender-neutral voice characteristics",
    icon: "👤",
    gradient: "from-gray-500/20 to-slate-500/20"
  }
];
