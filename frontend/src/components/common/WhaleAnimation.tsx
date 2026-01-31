'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';

interface Whale {
  id: number;
  x: number;
  y: number;
  size: number;
  speed: number;
  delay: number;
  direction: 'left' | 'right';
}

export default function WhaleAnimation() {
  const [whales, setWhales] = useState<Whale[]>([]);

  useEffect(() => {
    // Create multiple whales with random positions
    const initialWhales: Whale[] = [
      { id: 1, x: -150, y: 20, size: 80, speed: 15, delay: 0, direction: 'right' },
      { id: 2, x: 110, y: 60, size: 60, speed: 20, delay: 3, direction: 'left' },
      { id: 3, x: -150, y: 40, size: 50, speed: 25, delay: 7, direction: 'right' },
    ];
    setWhales(initialWhales);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {whales.map((whale) => (
        <div
          key={whale.id}
          className="absolute animate-whale"
          style={{
            top: `${whale.y}%`,
            width: whale.size,
            height: whale.size / 2,
            animationDuration: `${whale.speed}s`,
            animationDelay: `${whale.delay}s`,
            transform: whale.direction === 'left' ? 'scaleX(-1)' : 'scaleX(1)',
            opacity: 0.7,
          }}
        >
          <Image
            src="/whale.svg"
            alt="Swimming whale"
            width={whale.size}
            height={whale.size / 2}
            className="animate-float"
          />
        </div>
      ))}

      <style jsx global>{`
        @keyframes swimRight {
          0% {
            left: -150px;
          }
          100% {
            left: 110%;
          }
        }

        @keyframes swimLeft {
          0% {
            left: 110%;
          }
          100% {
            left: -150px;
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        .animate-whale {
          animation: swimRight linear infinite;
        }

        .animate-whale[style*="scaleX(-1)"] {
          animation: swimLeft linear infinite;
        }

        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
