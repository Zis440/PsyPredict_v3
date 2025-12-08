import React, { useState } from 'react';
import WebcamFeed from '../components/features/WebcamFeed';
import ChatInterface from '../components/features/ChatInterface';
import RemedyCard from '../components/features/RemedyCard';

const Dashboard: React.FC = () => {
  const [currentEmotion, setCurrentEmotion] = useState<string>("neutral");

  // New: Start screen state
  const [started, setStarted] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">

      {/* -------- START SCREEN -------- */}
      {!started && (
        <div className="flex flex-col items-center justify-center h-screen bg-indigo-700 text-white">
          <h1 className="text-4xl font-bold mb-6 tracking-wide">PsyPredict</h1>
          <button
            onClick={() => setStarted(true)}
            className="px-10 py-4 bg-white text-indigo-700 text-xl font-semibold rounded-xl shadow-lg hover:bg-gray-100 transition-all"
          >
            Start PsyPredict
          </button>
        </div>
      )}

      {/* -------- MAIN APP LAYOUT -------- */}
      {started && (
        <>
          {/* Header */}
          <header className="bg-indigo-700 text-white p-4 shadow-md flex justify-between items-center">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              📘 PsyPredict v2
              <span className="text-xs opacity-75 font-normal bg-indigo-800 px-2 py-1 rounded">Beta</span>
            </h1>
            <div className="text-sm opacity-90">Connected</div>
          </header>

          {/* MAIN GRID */}
          <div className="flex flex-1 flex-row overflow-hidden p-6 gap-6">

            {/* LEFT SIDE — CAMERA + REMEDY */}
            <div className="flex flex-col w-1/2 gap-4">

              {/* Webcam */}
              <div className="bg-white p-4 rounded-xl shadow-md border border-gray-200">
                <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">Live Emotional Analysis</h2>
                <WebcamFeed onEmotionDetected={setCurrentEmotion} />
              </div>

              {/* Remedy Card */}
              <div className="bg-white p-4 rounded-xl shadow-md border border-gray-200">
                <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">Therapeutic Insight</h2>
                <RemedyCard emotion={currentEmotion} />
              </div>
            </div>

            {/* RIGHT SIDE — CHAT */}
            <div className="flex-1">
              <ChatInterface currentEmotion={currentEmotion} />
            </div>
          </div>
        </>
      )}

    </div>
  );
};

export default Dashboard;
