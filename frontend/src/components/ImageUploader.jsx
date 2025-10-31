import React, { useState, useRef } from 'react';

const ImageUploader = ({ onImageUpload, isLoading }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleFile(file);
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleFile = (file) => {
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
    };
    reader.readAsDataURL(file);

    // Send to parent
    onImageUpload(file);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleReset = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {!preview ? (
        <div
          onClick={handleClick}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            relative glass rounded-3xl p-12
            cursor-pointer transition-all duration-300
            hover:scale-105 hover-lift
            ${isDragging ? 'scale-105 border-ocean-300 bg-ocean-500/20' : 'border-white/30'}
          `}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileInput}
            className="hidden"
          />

          <div className="flex flex-col items-center justify-center space-y-6">
            {/* Animated fish icon */}
            <div className="text-8xl animate-wiggle">
              🐟
            </div>

            {/* Text */}
            <div className="text-center">
              <h3 className="text-3xl font-bold text-white mb-2">
                Drop your fishy friend here!
              </h3>
              <p className="text-ocean-100 text-lg">
                or click to browse
              </p>
            </div>

            {/* Visual indicator */}
            <div className="flex space-x-2">
              <div className="w-3 h-3 bg-ocean-300 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
              <div className="w-3 h-3 bg-ocean-300 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-3 h-3 bg-ocean-300 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      ) : (
        <div className="glass rounded-3xl p-8 relative">
          {/* Preview Image */}
          <div className="relative">
            <img
              src={preview}
              alt="Preview"
              className="w-full h-96 object-contain rounded-2xl"
            />

            {/* Loading overlay */}
            {isLoading && (
              <div className="absolute inset-0 bg-ocean-900/70 rounded-2xl flex items-center justify-center">
                <div className="text-center">
                  <div className="spinner mx-auto mb-4"></div>
                  <p className="text-white text-xl font-semibold animate-pulse">
                    Analyzing your fish... 🔍
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Reset button */}
          {!isLoading && (
            <button
              onClick={handleReset}
              className="mt-6 w-full bg-ocean-500 hover:bg-ocean-600 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-2xl"
            >
              Try another fish! 🐠
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
