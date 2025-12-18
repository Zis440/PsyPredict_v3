import React, { useState } from "react";
import WebcamFeed from "../components/features/WebcamFeed";
import ChatInterface from "../components/features/ChatInterface";
import RemedyCard from "../components/features/RemedyCard";
import { Link } from "react-router-dom";

import Navbar from "../components/common/Navbar";

const Dashboard: React.FC = () => {
  const [currentEmotion, setCurrentEmotion] = useState<string>("neutral");

  return (
    <div className="min-h-screen md:h-screen bg-gray-100 flex flex-col overflow-hidden">
      {/* -------- MAIN APP LAYOUT -------- */}
      <>
        {/* Navbar */}
        <Navbar />

        {/* MAIN GRID */}
        <div className="flex-1 overflow-hidden px-6 py-4">
          <div className="max-w-[1400px] mx-auto h-full">
            {/* MOBILE LAYOUT */}
            <div className="flex flex-col gap-4 md:hidden flex-1 min-h-0 overflow-hidden">
              {/* Camera */}
              <div className="bg-white p-4 rounded-xl shadow-md">
                <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                  Camera Analysis
                </h2>
                <WebcamFeed onEmotionDetected={setCurrentEmotion} />
              </div>

              {/* Therapeutic Insight */}
              <div className="bg-white p-4 rounded-xl shadow-md">
                <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                  Therapeutic Insight
                </h2>
                <RemedyCard emotion={currentEmotion} />
              </div>

              {/* Chat */}
              <div className="bg-white rounded-xl shadow-md flex flex-col overflow-hidden h-[60vh]">
                <div className="p-4 shrink-0">
                  <h2 className="text-sm font-semibold text-gray-500 uppercase">
                    Chat
                  </h2>
                </div>
                <div className="flex-1 overflow-y-auto overflow-x-hidden min-h-0">
                  <ChatInterface currentEmotion={currentEmotion} />
                </div>
              </div>
            </div>

            {/* DESKTOP LAYOUT — UNTOUCHED */}
            <div className="hidden md:grid grid-cols-[420px_1fr] gap-6 h-full">
              {/* LEFT SIDE */}
              <div className="flex flex-col gap-4 h-full">
                <div className="bg-white p-4 rounded-xl shadow-md">
                  <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                    Camera Analysis
                  </h2>
                  <WebcamFeed onEmotionDetected={setCurrentEmotion} />
                </div>

                <div className="bg-white p-4 rounded-xl shadow-md">
                  <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                    Therapeutic Insight
                  </h2>
                  <RemedyCard emotion={currentEmotion} />
                </div>
              </div>

              {/* RIGHT SIDE */}
              <div className="bg-white rounded-xl shadow-md flex flex-col overflow-hidden">
                <div className="p-4">
                  <h2 className="text-sm font-semibold text-gray-500 uppercase">
                    Chat
                  </h2>
                </div>
                <ChatInterface currentEmotion={currentEmotion} />
              </div>
            </div>
          </div>
        </div>
      </>
    </div>
  );
};

export default Dashboard;
