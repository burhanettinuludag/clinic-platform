'use client';

import { useEffect, useRef } from 'react';

interface Neuron {
  x: number;
  y: number;
  radius: number;
  pulsePhase: number;
  connections: number[];
}

interface Props {
  className?: string;
}

export default function NeuralAnimation({ className }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = canvas.offsetWidth * window.devicePixelRatio;
      canvas.height = canvas.offsetHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Create neurons
    const neurons: Neuron[] = [];
    const neuronCount = 15;
    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;

    for (let i = 0; i < neuronCount; i++) {
      neurons.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: 3 + Math.random() * 4,
        pulsePhase: Math.random() * Math.PI * 2,
        connections: [],
      });
    }

    // Create connections (each neuron connects to 2-3 nearest neighbors)
    neurons.forEach((neuron, i) => {
      const distances = neurons
        .map((other, j) => ({
          index: j,
          dist: Math.hypot(other.x - neuron.x, other.y - neuron.y),
        }))
        .filter((d) => d.index !== i)
        .sort((a, b) => a.dist - b.dist);

      const connectionCount = 2 + Math.floor(Math.random() * 2);
      neuron.connections = distances.slice(0, connectionCount).map((d) => d.index);
    });

    let animationId: number;
    let time = 0;

    const animate = () => {
      time += 0.02;
      ctx.clearRect(0, 0, width, height);

      // Draw connections with flowing effect
      neurons.forEach((neuron, i) => {
        neuron.connections.forEach((targetIndex) => {
          const target = neurons[targetIndex];
          const gradient = ctx.createLinearGradient(
            neuron.x,
            neuron.y,
            target.x,
            target.y
          );

          const flowPhase = (time + i * 0.5) % 1;
          const alpha1 = 0.1 + 0.1 * Math.sin(time * 2 + neuron.pulsePhase);
          const alpha2 = 0.1 + 0.1 * Math.sin(time * 2 + target.pulsePhase);

          gradient.addColorStop(0, `rgba(6, 182, 212, ${alpha1})`);
          gradient.addColorStop(flowPhase, `rgba(147, 51, 234, 0.3)`);
          gradient.addColorStop(1, `rgba(6, 182, 212, ${alpha2})`);

          ctx.beginPath();
          ctx.moveTo(neuron.x, neuron.y);
          ctx.lineTo(target.x, target.y);
          ctx.strokeStyle = gradient;
          ctx.lineWidth = 1;
          ctx.stroke();
        });
      });

      // Draw neurons with pulse effect
      neurons.forEach((neuron) => {
        const pulse = Math.sin(time * 2 + neuron.pulsePhase);
        const glowRadius = neuron.radius * (1.5 + pulse * 0.5);
        const alpha = 0.3 + pulse * 0.2;

        // Outer glow
        const gradient = ctx.createRadialGradient(
          neuron.x,
          neuron.y,
          0,
          neuron.x,
          neuron.y,
          glowRadius * 3
        );
        gradient.addColorStop(0, `rgba(6, 182, 212, ${alpha})`);
        gradient.addColorStop(0.5, `rgba(147, 51, 234, ${alpha * 0.5})`);
        gradient.addColorStop(1, 'rgba(6, 182, 212, 0)');

        ctx.beginPath();
        ctx.arc(neuron.x, neuron.y, glowRadius * 3, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        // Core
        ctx.beginPath();
        ctx.arc(neuron.x, neuron.y, neuron.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${0.8 + pulse * 0.2})`;
        ctx.fill();
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-none ${className || ''}`}
      style={{ opacity: 0.6 }}
    />
  );
}
