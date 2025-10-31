import React, { useEffect, useState } from 'react';
import clownImg from '../assets/fish-images/clown.png';
import barImg from '../assets/fish-images/bar.png';
import espadonImg from '../assets/fish-images/espadon.png';
import requinImg from '../assets/fish-images/requin.png';
import leviatorImg from '../assets/fish-images/leviator.png';
import poissonMocheImg from '../assets/fish-images/poissonmoche.png';

// Fun facts pour chaque espèce de poisson
const fishFacts = {
  'Catfish': [
    'Catfish have over 27,000 taste buds! 👅',
    'Some catfish can walk on land! 🚶',
    'Catfish whiskers are called barbels! 🎯'
  ],
  'Gold Fish': [
    'Goldfish can live for over 40 years! 🎂',
    'They can see more colors than humans! 🌈',
    'Goldfish have a memory of at least 3 months! 🧠'
  ],
  'Mudfish': [
    'Mudfish can survive out of water for months! 💪',
    'They breathe air using a modified swim bladder! 🫁',
    'Mudfish are living fossils! 🦴'
  ],
  'Mullet': [
    'Mullet can jump up to 3 feet high! 🦘',
    'They feed on algae and detritus! 🌱',
    'Mullet travel in large schools! 🐟🐟🐟'
  ],
  'Snakehead': [
    'Snakehead fish can breathe air! 💨',
    'They can survive on land for days! 🏝️',
    'Snakeheads are fierce predators! 🦈'
  ]
};

// Images pour chaque espèce (vous pouvez mapper selon vos besoins)
const fishImages = {
  'Catfish': poissonMocheImg,
  'Gold Fish': clownImg,
  'Mudfish': barImg,
  'Mullet': espadonImg,
  'Snakehead': requinImg,
  // Fallback
  'default': leviatorImg
};

const ResultDisplay = ({ result }) => {
  const [showConfetti, setShowConfetti] = useState(false);
  const [randomFact, setRandomFact] = useState('');

  useEffect(() => {
    if (result) {
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 3000);

      // Get random fact
      const facts = fishFacts[result.species] || [];
      const fact = facts[Math.floor(Math.random() * facts.length)];
      setRandomFact(fact);
    }
  }, [result]);

  if (!result) return null;

  const confidence = (result.confidence * 100).toFixed(1);
  const fishImage = fishImages[result.species] || fishImages['default'];

  return (
    <div className="w-full max-w-2xl mx-auto mt-8 relative">
      {/* Confetti effect */}
      {showConfetti && (
        <div className="absolute inset-0 pointer-events-none z-10">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute text-3xl animate-bounce"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 0.5}s`,
                animationDuration: `${Math.random() * 1 + 1}s`,
              }}
            >
              {['🎉', '✨', '🌟', '💫', '⭐'][Math.floor(Math.random() * 5)]}
            </div>
          ))}
        </div>
      )}

      {/* Result card */}
      <div className="glass rounded-3xl p-8 animate-pulse-glow">
        {/* Header */}
        <div className="text-center mb-6">
          <img
            src={fishImage}
            alt={result.species}
            className="w-48 h-48 mx-auto mb-4 animate-wiggle object-contain"
            style={{
              filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.3))',
            }}
          />
          <h2 className="text-4xl font-bold text-white mb-2">
            It's a {result.species}!
          </h2>
          <p className="text-ocean-100 text-xl">
            I'm {confidence}% sure! 🎯
          </p>
        </div>

        {/* Confidence bar */}
        <div className="mb-6">
          <div className="bg-white/20 rounded-full h-6 overflow-hidden">
            <div
              className="bg-gradient-to-r from-ocean-400 to-ocean-600 h-full rounded-full transition-all duration-1000 ease-out flex items-center justify-center"
              style={{ width: `${confidence}%` }}
            >
              <span className="text-white font-bold text-sm">
                {confidence}%
              </span>
            </div>
          </div>
        </div>

        {/* Fun fact */}
        {randomFact && (
          <div className="bg-white/10 rounded-2xl p-6 border-2 border-white/20">
            <h3 className="text-xl font-bold text-ocean-100 mb-2">
              🎓 Fun Fact:
            </h3>
            <p className="text-white text-lg">
              {randomFact}
            </p>
          </div>
        )}

        {/* Celebration message */}
        <div className="mt-6 text-center">
          <p className="text-ocean-100 text-lg italic">
            {confidence > 90 ? "I'm super confident about this one! 💪" :
             confidence > 70 ? "Pretty sure about this! 👍" :
             confidence > 50 ? "I think this is right... 🤔" :
             "Hmm, this is a tricky one! 🤷"}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResultDisplay;
