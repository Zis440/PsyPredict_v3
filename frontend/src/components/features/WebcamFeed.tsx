// src/components/features/WebcamFeed.tsx

import React, { useRef, useState, useEffect, useCallback } from "react";
import Webcam from "react-webcam";
import { predictEmotion } from "../../services/api"; // Import your API helper

interface WebcamFeedProps {
  onEmotionDetected: (emotion: string) => void; // Parent component gets the emotion
}

const WebcamFeed: React.FC<WebcamFeedProps> = ({ onEmotionDetected }) => {
  const webcamRef = useRef<Webcam>(null);
  const [detectedEmotion, setDetectedEmotion] = useState<string>("Neutral");
  const [faceBox, setFaceBox] = useState<number[] | null>(null);

  // Define video constraints (keep it small for speed)
const isMobile = window.innerWidth < 768;

const videoConstraints = {
  width: isMobile ? 200 : 480,
  height: isMobile ? 200 : 360,
  facingMode: "user",
};


  // --- Function to Capture & Send Image ---
  const captureAndPredict = useCallback(async () => {
    if (!webcamRef.current) return;

    // 1. Capture Screenshot
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    // 2. Convert Base64 to Blob (Backend expects a file)
    const blob = await fetch(imageSrc).then((res) => res.blob());
    const file = new File([blob], "capture.jpg", { type: "image/jpeg" });

    try {
      // 3. Send to Backend
      const result = await predictEmotion(file);

      if (result.emotion) {
        setDetectedEmotion(result.emotion);
        setFaceBox(result.face_box); // [x, y, w, h]
        onEmotionDetected(result.emotion); // Tell the parent component
      }
    } catch (error) {
      console.error("Emotion detection failed:", error);
    }
  }, [onEmotionDetected]);

  // --- Auto-Run every 3 Seconds ---
  useEffect(() => {
    const interval = setInterval(captureAndPredict, 3000); // 3000ms = 3 seconds
    return () => clearInterval(interval); // Cleanup on unmount
  }, [captureAndPredict]);

  return (
<div className="relative w-full max-w-[240px] md:max-w-none mx-auto rounded-xl overflow-hidden shadow-md border border-gray-300 bg-black">
      {/* 1. The Live Video */}
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        videoConstraints={videoConstraints}
        className="w-full h-auto"
      />

      {/* 2. The Face Box Overlay */}
      {faceBox && (
        <div
          className="absolute border border-green-400 rounded-lg transition-all duration-300 ease-in-out"
          style={{
            left: `${(faceBox[0] / 48) * 100}%`, // Adjust scale if needed based on CSS size
            top: `${(faceBox[1] / 48) * 100}%`,
            width: `${(faceBox[2] / 48) * 100}%`,
            height: `${(faceBox[3] / 48) * 100}%`,
          }}
        />
      )}

      {/* 3. Emotion Label */}
      <div className="absolute top-4 right-4 flex items-center gap-2 bg-neutral-200 text-black px-3 py-1.5 rounded-full font-medium text-sm shadow">
  <span className="relative flex h-2 w-2">
    <span className="absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75 animate-ping"></span>
    <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500"></span>
  </span>
  <span>{detectedEmotion.toUpperCase()}</span>
</div>
    </div>
  );
};

export default WebcamFeed;
