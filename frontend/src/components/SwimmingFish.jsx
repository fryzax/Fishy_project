import React, { useEffect, useState } from 'react';
import clownImg from '../assets/fish-images/clown.png';
import barImg from '../assets/fish-images/bar.png';
import espadonImg from '../assets/fish-images/espadon.png';
import requinImg from '../assets/fish-images/requin.png';
import leviatorImg from '../assets/fish-images/leviator.png';

const SwimmingFish = () => {
  const [fishes, setFishes] = useState([]);

  const fishImages = [clownImg, barImg, espadonImg, requinImg, leviatorImg];

  useEffect(() => {
    // Generate random swimming fish
    const generateFish = () => {
      const newFish = [];
      for (let i = 0; i < 5; i++) {
        newFish.push({
          id: i,
          image: fishImages[i],
          top: Math.random() * 80 + 10, // 10-90%
          delay: Math.random() * 15, // 0-15s
          duration: Math.random() * 5 + 10, // 10-15s
          size: Math.random() * 40 + 60, // 60-100px
        });
      }
      setFishes(newFish);
    };

    generateFish();
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {fishes.map((fish) => (
        <img
          key={fish.id}
          src={fish.image}
          alt="swimming fish"
          className="absolute animate-swim"
          style={{
            top: `${fish.top}%`,
            animationDelay: `${fish.delay}s`,
            animationDuration: `${fish.duration}s`,
            width: `${fish.size}px`,
            height: 'auto',
            filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.3))',
          }}
        />
      ))}
    </div>
  );
};

export default SwimmingFish;
