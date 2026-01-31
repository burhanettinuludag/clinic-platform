'use client';

interface BrainIconProps {
  className?: string;
  size?: number;
  animated?: boolean;
}

export default function BrainIcon({ className = '', size = 64, animated = true }: BrainIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`${className} ${animated ? 'animate-float' : ''}`}
    >
      <defs>
        <linearGradient id="brainGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#06b6d4" />
          <stop offset="50%" stopColor="#8b5cf6" />
          <stop offset="100%" stopColor="#c084fc" />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {/* Main brain shape */}
      <g filter="url(#glow)">
        {/* Left hemisphere */}
        <path
          d="M50 15 C30 15 20 30 20 45 C20 55 25 65 35 70 C30 75 28 82 30 88 C32 92 40 94 45 90 C47 95 55 95 55 90 L55 55 C55 45 50 35 50 25 C50 20 50 15 50 15"
          fill="url(#brainGradient)"
          opacity="0.9"
          className={animated ? 'animate-pulse-slow' : ''}
        />

        {/* Right hemisphere */}
        <path
          d="M50 15 C70 15 80 30 80 45 C80 55 75 65 65 70 C70 75 72 82 70 88 C68 92 60 94 55 90 C53 95 45 95 45 90 L45 55 C45 45 50 35 50 25 C50 20 50 15 50 15"
          fill="url(#brainGradient)"
          opacity="0.9"
          className={animated ? 'animate-pulse-slow' : ''}
          style={{ animationDelay: '0.5s' }}
        />

        {/* Brain folds - left */}
        <path
          d="M30 35 Q35 40 30 50 M35 30 Q42 38 35 48 M25 50 Q32 55 28 65"
          stroke="rgba(255,255,255,0.4)"
          strokeWidth="2"
          fill="none"
          strokeLinecap="round"
        />

        {/* Brain folds - right */}
        <path
          d="M70 35 Q65 40 70 50 M65 30 Q58 38 65 48 M75 50 Q68 55 72 65"
          stroke="rgba(255,255,255,0.4)"
          strokeWidth="2"
          fill="none"
          strokeLinecap="round"
        />

        {/* Center line */}
        <line
          x1="50"
          y1="20"
          x2="50"
          y2="85"
          stroke="rgba(255,255,255,0.3)"
          strokeWidth="2"
        />

        {/* Neural connection dots */}
        {[
          { cx: 35, cy: 40 },
          { cx: 65, cy: 40 },
          { cx: 30, cy: 55 },
          { cx: 70, cy: 55 },
          { cx: 40, cy: 70 },
          { cx: 60, cy: 70 },
        ].map((dot, i) => (
          <circle
            key={i}
            cx={dot.cx}
            cy={dot.cy}
            r="3"
            fill="white"
            opacity="0.8"
            className={animated ? 'animate-neuron-pulse' : ''}
            style={{ animationDelay: `${i * 0.3}s` }}
          />
        ))}
      </g>
    </svg>
  );
}
