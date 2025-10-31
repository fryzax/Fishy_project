import React, { useState, useEffect } from 'react';
import krakenImg from '../assets/fish-images/kraken.png';

const KrakenEasterEgg = ({ show }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      // Auto hide after 5 seconds
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [show]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="text-center">
        {/* Kraken image with dramatic entrance */}
        <img
          src={krakenImg}
          alt="RELEASE THE KRAKEN!"
          className="w-96 h-96 mx-auto mb-8 animate-wiggle object-contain"
          style={{
            filter: 'drop-shadow(0 0 30px rgba(255, 0, 0, 0.8))',
          }}
        />

        {/* Dramatic text */}
        <h1 className="text-6xl font-bold text-red-500 mb-4 animate-pulse">
          🌊 RELEASE THE KRAKEN! 🌊
        </h1>
        <p className="text-3xl text-white mb-4">
          That's not a fish... that's LEGENDARY! 🦑
        </p>
        <p className="text-xl text-ocean-200 italic">
          (Click anywhere to continue)
        </p>
      </div>

      {/* Click to dismiss */}
      <div
        className="absolute inset-0 cursor-pointer"
        onClick={() => setIsVisible(false)}
      />
    </div>
  );
};

export default KrakenEasterEgg;
