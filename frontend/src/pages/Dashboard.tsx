import React, { useState } from "react";
import WebcamFeed from "../components/features/WebcamFeed";
import ChatInterface from "../components/features/ChatInterface";
import RemedyCard from "../components/features/RemedyCard";

import Navbar from "../components/common/Navbar";

const Dashboard: React.FC = () => {
  const [currentEmotion, setCurrentEmotion] = useState<string>("neutral");

  return (
    // CHANGED: Use h-[100dvh] for better mobile browser support and strict height constraints
    <div className="min-h-screen md:h-[100dvh] bg-gray-100 flex flex-col overflow-hidden">
      {/* -------- MAIN APP LAYOUT -------- */}
      <>
        {/* Navbar */}
        <Navbar />

        {/* MAIN GRID */}
        {/* CHANGED: Added min-h-0 to ensure flex child can scroll internally instead of expanding parent */}
        <div className="flex-1 overflow-hidden px-3 py-3 md:px-4 md:py-4 lg:px-6 flex flex-col min-h-0">
          <div className="max-w-[1400px] mx-auto w-full h-full">
            
            {/* MOBILE LAYOUT (Unchanged logic, just ensure full width) */}
            <div className="flex flex-col gap-4 md:hidden flex-1 min-h-0 overflow-y-auto pb-4">
              {/* Camera */}
              <div className="bg-white p-4 rounded-xl shadow-md shrink-0">
                <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                  Camera Analysis
                </h2>
                <WebcamFeed onEmotionDetected={setCurrentEmotion} />
              </div>

              {/* Therapeutic Insight */}
              <div className="bg-white p-4 rounded-xl shadow-md shrink-0">
                <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                  Therapeutic Insight
                </h2>
                <RemedyCard emotion={currentEmotion} />
              </div>

              {/* Chat */}
              <div className="bg-white rounded-xl shadow-md flex flex-col overflow-hidden h-[60vh] shrink-0">
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

            {/* DESKTOP LAYOUT */}
            {/* CHANGED: Grid columns are now responsive. 
                - md (small laptops): Sidebar is 300px
                - lg (standard): Sidebar is 350px
                - xl (large screens): Sidebar is 420px
             */}
            <div className="hidden md:grid md:grid-cols-[300px_1fr] lg:grid-cols-[350px_1fr] xl:grid-cols-[420px_1fr] gap-4 lg:gap-6 h-full min-h-0">
              
              {/* LEFT SIDE */}
              {/* CHANGED: overflow-y-auto allows the left side to scroll independently if the camera/remedy cards get too tall for a small screen */}
              <div className="flex flex-col gap-4 h-full overflow-y-auto pr-1">
                <div className="bg-white p-3 lg:p-4 rounded-xl shadow-md shrink-0">
                  <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                    Camera Analysis
                  </h2>
                  <WebcamFeed onEmotionDetected={setCurrentEmotion} />
                </div>

                <div className="bg-white p-3 lg:p-4 rounded-xl shadow-md shrink-0">
                  <h2 className="text-sm font-semibold text-gray-500 uppercase mb-2">
                    Therapeutic Insight
                  </h2>
                  <RemedyCard emotion={currentEmotion} />
                </div>
              </div>

              {/* RIGHT SIDE */}
              {/* CHANGED: min-h-0 is CRITICAL here to prevent the input box from being pushed off screen */}
              <div className="bg-white rounded-xl shadow-md flex flex-col overflow-hidden h-full min-h-0">
                <div className="p-3 lg:p-4 shrink-0 border-b border-gray-100">
                  <h2 className="text-sm font-semibold text-gray-500 uppercase">
                    Chat
                  </h2>
                </div>
                {/* ChatInterface takes remaining height */}
                <div className="flex-1 min-h-0 relative">
                  <ChatInterface currentEmotion={currentEmotion} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </>
    </div>
  );
};

export default Dashboard;