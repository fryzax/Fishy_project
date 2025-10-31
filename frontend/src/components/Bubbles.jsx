import React, { useEffect, useState } from 'react';
import bubbleImg from '../assets/fish-images/bubble.png';

const Bubbles = () => {
  const [staticBubbles, setStaticBubbles] = useState([]);
  const [risingBubbles, setRisingBubbles] = useState([]);
  const [cursorBubbles, setCursorBubbles] = useState([]);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    // Generate static rising bubbles (original)
    const generateStaticBubbles = () => {
      const newBubbles = [];
      for (let i = 0; i < 15; i++) {
        newBubbles.push({
          id: `static-${i}`,
          size: Math.random() * 60 + 30,
          left: Math.random() * 100,
          delay: Math.random() * 5,
          duration: Math.random() * 4 + 4,
          opacity: Math.random() * 0.4 + 0.3,
        });
      }
      setStaticBubbles(newBubbles);
    };

    // Generate cursor-following bubbles
    const generateCursorBubbles = () => {
      const newBubbles = [];
      for (let i = 0; i < 8; i++) {
        newBubbles.push({
          id: `cursor-${i}`,
          size: Math.random() * 40 + 20,
          x: Math.random() * window.innerWidth,
          y: Math.random() * window.innerHeight,
          opacity: Math.random() * 0.3 + 0.2,
          speed: Math.random() * 0.02 + 0.01, // 0.01-0.03
        });
      }
      setCursorBubbles(newBubbles);
    };

    generateStaticBubbles();
    generateCursorBubbles();

    // Track mouse position
    const handleMouseMove = (e) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Spawn rising bubbles from bottom periodically
    const spawnInterval = setInterval(() => {
      const newBubble = {
        id: `rising-${Date.now()}`,
        size: Math.random() * 50 + 25,
        left: Math.random() * 100,
        opacity: Math.random() * 0.5 + 0.3,
        duration: Math.random() * 3 + 3, // 3-6s
      };
      setRisingBubbles((prev) => [...prev, newBubble]);

      // Remove bubble after animation
      setTimeout(() => {
        setRisingBubbles((prev) => prev.filter((b) => b.id !== newBubble.id));
      }, newBubble.duration * 1000);
    }, 2000); // Spawn every 2 seconds

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      clearInterval(spawnInterval);
    };
  }, []);

  // Update cursor bubbles position to follow mouse
  useEffect(() => {
    const moveInterval = setInterval(() => {
      setCursorBubbles((bubbles) =>
        bubbles.map((bubble) => {
          const dx = mousePos.x - bubble.x;
          const dy = mousePos.y - bubble.y;
          return {
            ...bubble,
            x: bubble.x + dx * bubble.speed,
            y: bubble.y + dy * bubble.speed,
          };
        })
      );
    }, 50); // Update every 50ms

    return () => clearInterval(moveInterval);
  }, [mousePos]);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {/* Static rising bubbles (original) */}
      {staticBubbles.map((bubble) => (
        <img
          key={bubble.id}
          src={bubbleImg}
          alt="bubble"
          className="absolute animate-bubble"
          style={{
            width: `${bubble.size}px`,
            height: `${bubble.size}px`,
            left: `${bubble.left}%`,
            animationDelay: `${bubble.delay}s`,
            animationDuration: `${bubble.duration}s`,
            opacity: bubble.opacity,
          }}
        />
      ))}

      {/* Rising bubbles spawned from bottom */}
      {risingBubbles.map((bubble) => (
        <img
          key={bubble.id}
          src={bubbleImg}
          alt="bubble"
          className="absolute animate-bubble"
          style={{
            width: `${bubble.size}px`,
            height: `${bubble.size}px`,
            left: `${bubble.left}%`,
            bottom: '-100px',
            opacity: bubble.opacity,
            animationDuration: `${bubble.duration}s`,
          }}
        />
      ))}

      {/* Cursor-following bubbles */}
      {cursorBubbles.map((bubble) => (
        <img
          key={bubble.id}
          src={bubbleImg}
          alt="bubble"
          className="absolute transition-all duration-200 ease-out"
          style={{
            width: `${bubble.size}px`,
            height: `${bubble.size}px`,
            left: `${bubble.x}px`,
            top: `${bubble.y}px`,
            opacity: bubble.opacity,
            transform: 'translate(-50%, -50%)',
          }}
        />
      ))}
    </div>
  );
};

export default Bubbles;
