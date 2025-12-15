import React, { useState } from "react";
import WebcamFeed from "../components/features/WebcamFeed";
import ChatInterface from "../components/features/ChatInterface";
import RemedyCard from "../components/features/RemedyCard";
import { Link } from "react-router-dom";

const Dashboard: React.FC = () => {
  const [currentEmotion, setCurrentEmotion] = useState<string>("neutral");

  return (
    <div className="h-screen bg-gray-100 flex flex-col overflow-hidden">
      {/* -------- MAIN APP LAYOUT -------- */}
      <>
        {/* Header */}
        <header className="bg-white shadow-md">
  <div className="max-w-[1400px] mx-auto px-6 flex justify-between items-center h-16">
    <Link to={"/"}>
      <div className="flex items-center gap-2 font-bold text-xl text-slate-800">
        <div>🧠</div>
        PsyPredict
      </div>
    </Link>
  </div>
</header>


        {/* MAIN GRID */}
        <div className="flex-1 overflow-hidden px-6 py-4">
          <div className="grid grid-cols-[420px_1fr] gap-6 h-full max-w-[1400px] mx-auto">
            {/* LEFT SIDE — CAMERA + REMEDY */}
            <div className="flex flex-col gap-4 h-full">
              {/* Webcam */}
              <div className="bg-white p-4 rounded-xl shadow-md border border-gray-200">
                <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                  Camera Analysis
                </h2>
                <WebcamFeed onEmotionDetected={setCurrentEmotion} />
              </div>

              {/* Remedy Card */}
              <div className="bg-white p-4 rounded-xl shadow-md border border-gray-200">
                <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                  Therapeutic Insight
                </h2>
                <RemedyCard emotion={currentEmotion} />
              </div>
            </div>

            {/* RIGHT SIDE — CHAT */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 flex flex-col overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-sm font-semibold text-gray-500 uppercase">
                  Chat
                </h2>
              </div>

              <ChatInterface currentEmotion={currentEmotion} />
            </div>
          </div>
        </div>
      </>
    </div>
  );
};

export default Dashboard;
