import React, { useState } from 'react';
import axios from 'axios';
import Bubbles from './components/Bubbles';
import SwimmingFish from './components/SwimmingFish';
import ImageUploader from './components/ImageUploader';
import ResultDisplay from './components/ResultDisplay';
import KrakenEasterEgg from './components/KrakenEasterEgg';

function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showKraken, setShowKraken] = useState(false);

  const handleImageUpload = async (file) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Créer FormData pour l'upload
      const formData = new FormData();
      formData.append('file', file);

      // TODO: Remplacer par l'URL de votre API backend
      // const response = await axios.post('/api/predict', formData, {
      //   headers: {
      //     'Content-Type': 'multipart/form-data',
      //   },
      // });

      // MOCK pour tester le frontend sans backend
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simule le délai de l'API

      // 5% chance d'avoir le Kraken Easter Egg ! 🦑
      const krakenChance = Math.random();
      if (krakenChance < 0.05) {
        setShowKraken(true);
        setIsLoading(false);
        return;
      }

      const mockSpecies = ['Catfish', 'Gold Fish', 'Mudfish', 'Mullet', 'Snakehead'];
      const mockResult = {
        species: mockSpecies[Math.floor(Math.random() * mockSpecies.length)],
        confidence: Math.random() * 0.4 + 0.6, // 60-100%
      };

      setResult(mockResult);
      // setResult(response.data); // Décommenter pour utiliser la vraie API
    } catch (err) {
      console.error('Error:', err);
      setError('Oops! Something went wrong. Try again! 🐠');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen ocean-gradient relative overflow-hidden">
      {/* Animated background elements */}
      <Bubbles />
      <SwimmingFish />

      {/* Kraken Easter Egg */}
      <KrakenEasterEgg show={showKraken} />

      {/* Main content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="pt-12 pb-8 text-center">
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-4 animate-float drop-shadow-2xl">
            🐟 Fishy Classifier 🐟
          </h1>
          <p className="text-2xl text-ocean-100 font-medium">
            What kind of fish is that? Let's find out! 🔍
          </p>
        </header>

        {/* Main content area */}
        <main className="flex-1 container mx-auto px-4 pb-12">
          <ImageUploader onImageUpload={handleImageUpload} isLoading={isLoading} />

          {error && (
            <div className="max-w-2xl mx-auto mt-8">
              <div className="glass rounded-2xl p-6 bg-red-500/20 border-2 border-red-400/50">
                <p className="text-white text-center text-xl">
                  {error}
                </p>
              </div>
            </div>
          )}

          <ResultDisplay result={result} />
        </main>

        {/* Footer */}
        <footer className="pb-8 text-center">
          <p className="text-ocean-100 text-lg">
            Made with 💙 and lots of fish
          </p>
          <div className="mt-2 text-4xl space-x-2">
            <span className="inline-block animate-wiggle">🐟</span>
            <span className="inline-block animate-wiggle" style={{ animationDelay: '0.1s' }}>🐠</span>
            <span className="inline-block animate-wiggle" style={{ animationDelay: '0.2s' }}>🐡</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
