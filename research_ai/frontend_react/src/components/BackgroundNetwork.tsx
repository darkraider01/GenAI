import React, { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  alpha: number;
}

export const BackgroundNetwork: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Handle accessibility preference for reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return; // Render static dark background only

    let animationFrameId: number;
    let particles: Particle[] = [];
    let width = window.innerWidth;
    let height = window.innerHeight;
    
    // Mouse tracking for parallax
    let mouse = { x: width / 2, y: height / 2 };
    
    // Config
    const isMobile = width < 768;
    const PARTICLE_COUNT = isMobile ? 40 : 100;
    const MAX_DISTANCE = isMobile ? 120 : 180;
    const MOUSE_REPEL_RADIUS = 150;
    const BASE_OPACITY = 0.15;
    
    const init = () => {
      canvas.width = width;
      canvas.height = height;
      particles = [];
      
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          radius: Math.random() * 2 + 1,
          alpha: Math.random() * 0.5 + 0.1
        });
      }
    };

    const drawLine = (p1: Particle, p2: Particle, distance: number) => {
      if (!ctx) return;
      const opacity = (1 - distance / MAX_DISTANCE) * BASE_OPACITY;
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      // Soft indigo/light blue glow color
      ctx.strokeStyle = `rgba(165, 180, 252, ${opacity})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    };

    const animate = () => {
      if (!ctx || !canvas) return;

      // Clear canvas with a very slight trail effect or fully clear
      ctx.clearRect(0, 0, width, height);

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Move
        p.x += p.vx;
        p.y += p.vy;

        // Bounce off edges
        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        // Parallax / Interactivity via Mouse
        // Push particles slightly away from the mouse
        const dxMouse = mouse.x - p.x;
        const dyMouse = mouse.y - p.y;
        const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);
        if (distMouse < MOUSE_REPEL_RADIUS) {
          const force = (MOUSE_REPEL_RADIUS - distMouse) / MOUSE_REPEL_RADIUS;
          p.x -= dxMouse * force * 0.02;
          p.y -= dyMouse * force * 0.02;
        }

        // Draw Particle
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(199, 210, 254, ${p.alpha * 0.8})`; // Light glowing dot
        ctx.fill();

        // Check connections
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < MAX_DISTANCE) {
            drawLine(p, p2, dist);
          }
        }
      }

      animationFrameId = requestAnimationFrame(animate);
    };

    const handleResize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
      // Reinitialize if screen size drastically changes to avoid clustering
      if (Math.abs(canvas.width - width) > 100) {
          init();
      }
    };
    
    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    };

    // Pause animation when tab is inactive to save performance
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden') {
        cancelAnimationFrame(animationFrameId);
      } else {
        animate();
      }
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('visibilitychange', handleVisibilityChange);

    init();
    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0, 
        pointerEvents: 'none', 
        background: 'transparent'
      }}
    />
  );
};
