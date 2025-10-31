// MyLogo.tsx
import { cn } from "@/lib/utils";

interface MyLogoProps {
  className?: string;
}

export function ClipizyLogo({ className }: MyLogoProps) {
  return (
    <svg
      viewBox="0 0 512 512"
      className={cn("w-12 h-12", className)}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
    >
      <defs>
        {/* Gradient for outer ring */}
        <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#66b4f6" />
          <stop offset="100%" stopColor="#9275cf" />
        </linearGradient>

        {/* Gradient for waveform */}
        <linearGradient id="waveGradient" x1="0%" y1="50%" x2="100%" y2="50%">
          <stop offset="0%" stopColor="#66b4f6" />
          <stop offset="100%" stopColor="#9275cf" />
        </linearGradient>
      </defs>

      {/* Outer circle */}
      <circle
        cx="256"
        cy="256"
        r="200"
        stroke="url(#ringGradient)"
        strokeWidth="30"
        fill="none"
      />

      {/* Waveform path */}
      <path
        d="M120 260 L160 260 Q180 200 200 260 L220 360 L250 140 L280 360 L310 200 L330 260 L390 260"
        stroke="url(#waveGradient)"
        strokeWidth="30"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}