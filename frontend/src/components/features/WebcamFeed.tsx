// src/components/features/WebcamFeed.tsx

import React, { useRef, useState, useEffect, useCallback } from "react";
import Webcam from "react-webcam";
import { predictEmotion } from "../../services/api";
import { biometricEngine } from "../../services/biometrics";
import type { BiometricTelemetry } from "../../services/biometrics";
import { Eye, Activity, Sparkles } from "lucide-react";

interface WebcamFeedProps {
  onEmotionDetected: (emotion: string) => void;
  onBiometricsDetected?: (telemetry: BiometricTelemetry) => void;
}

const WebcamFeed: React.FC<WebcamFeedProps> = ({
  onEmotionDetected,
  onBiometricsDetected,
}) => {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [telemetry, setTelemetry] = useState<BiometricTelemetry | null>(null);
  const [detectedEmotion, setDetectedEmotion] = useState<string>("Neutral");
  const [engineReady, setEngineReady] = useState<boolean>(false);
  const [isCalibrating, setIsCalibrating] = useState<boolean>(true);

  const isMobile = typeof window !== "undefined" && window.innerWidth < 768;
  const videoConstraints = {
    width: isMobile ? 240 : 480,
    height: isMobile ? 180 : 360,
    facingMode: "user",
  };

  // 1. Initialize MediaPipe Biometrics Engine
  useEffect(() => {
    let mounted = true;
    biometricEngine
      .initialize()
      .then(() => {
        if (mounted) {
          setEngineReady(true);
          setIsCalibrating(false);
        }
      })
      .catch((err) => {
        console.error("Biometrics engine init error:", err);
        if (mounted) setIsCalibrating(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  // 2. Real-Time Telemetry Processing Loop
  useEffect(() => {
    if (!engineReady) return;

    let animFrameId: number;
    let lastProcessTime = 0;
    const PROCESS_INTERVAL = 120; // Run every ~120ms (approx 8-10 fps) for smooth tracking without CPU drain

    const processFrame = () => {
      const now = performance.now();
      if (
        now - lastProcessTime >= PROCESS_INTERVAL &&
        webcamRef.current?.video &&
        webcamRef.current.video.readyState >= 2
      ) {
        lastProcessTime = now;
        const video = webcamRef.current.video;
        const data = biometricEngine.processVideoFrame(video);

        if (data) {
          setTelemetry(data);
          setDetectedEmotion(data.dominant_emotion.replace(/_/g, " "));
          onEmotionDetected(data.dominant_emotion);
          if (onBiometricsDetected) {
            onBiometricsDetected(data);
          }

          // Draw HUD overlay on canvas
          drawBiometricHUD(data, video);
        } else {
          // Clear canvas when no face is detected
          const canvas = canvasRef.current;
          if (canvas) {
            const ctx = canvas.getContext("2d");
            if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
          }
        }
      }
      animFrameId = requestAnimationFrame(processFrame);
    };

    animFrameId = requestAnimationFrame(processFrame);
    return () => cancelAnimationFrame(animFrameId);
  }, [engineReady, onEmotionDetected, onBiometricsDetected]);

  // 3. Fallback server snapshot check if MediaPipe takes time
  const captureAndPredictFallback = useCallback(async () => {
    if (!webcamRef.current || engineReady) return;
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    try {
      const blob = await fetch(imageSrc).then((res) => res.blob());
      const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
      const result = await predictEmotion(file);
      if (result?.emotion) {
        setDetectedEmotion(result.emotion);
        onEmotionDetected(result.emotion);
      }
    } catch (e) {
      console.debug("Fallback prediction skipped:", e);
    }
  }, [engineReady, onEmotionDetected]);

  useEffect(() => {
    if (engineReady) return;
    const interval = setInterval(captureAndPredictFallback, 4000);
    return () => clearInterval(interval);
  }, [engineReady, captureAndPredictFallback]);

  // 4. Render Medical-Grade Biometric HUD onto transparent canvas
  const drawBiometricHUD = (data: BiometricTelemetry, video: HTMLVideoElement) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
      canvas.width = video.videoWidth || 480;
      canvas.height = video.videoHeight || 360;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const w = canvas.width;
    const h = canvas.height;

    // Draw Iris Reticles
    if (data.iris_landmarks) {
      const { leftIris, rightIris } = data.iris_landmarks;
      const irisColor =
        data.gaze_direction === "direct"
          ? "rgba(52, 211, 153, 0.8)" // Green for direct
          : data.gaze_direction === "downcast"
          ? "rgba(96, 165, 250, 0.8)" // Blue for downcast
          : "rgba(251, 146, 60, 0.8)"; // Orange for darting / avoidant

      [leftIris, rightIris].forEach((iris) => {
        const ix = iris.x * w;
        const iy = iris.y * h;

        ctx.strokeStyle = irisColor;
        ctx.lineWidth = 1.5;

        // Circular reticle
        ctx.beginPath();
        ctx.arc(ix, iy, 7, 0, 2 * Math.PI);
        ctx.stroke();

        // Inner tracking pip
        ctx.fillStyle = irisColor;
        ctx.beginPath();
        ctx.arc(ix, iy, 2, 0, 2 * Math.PI);
        ctx.fill();

        // Crosshairs
        ctx.beginPath();
        ctx.moveTo(ix - 10, iy);
        ctx.lineTo(ix + 10, iy);
        ctx.moveTo(ix, iy - 10);
        ctx.lineTo(ix, iy + 10);
        ctx.stroke();
      });
    }

    // Draw Sleek Minimal Corner Bounding Box
    if (data.face_box && data.face_box.length === 4) {
      const [bx, by, bw, bh] = data.face_box;
      const cornerLen = 16;
      ctx.strokeStyle =
        data.triguna_dominant === "rajas"
          ? "rgba(244, 63, 94, 0.75)"
          : data.triguna_dominant === "tamas"
          ? "rgba(147, 51, 234, 0.75)"
          : "rgba(16, 185, 129, 0.75)";
      ctx.lineWidth = 2;

      // Top-Left
      ctx.beginPath();
      ctx.moveTo(bx, by + cornerLen);
      ctx.lineTo(bx, by);
      ctx.lineTo(bx + cornerLen, by);
      ctx.stroke();

      // Top-Right
      ctx.beginPath();
      ctx.moveTo(bx + bw - cornerLen, by);
      ctx.lineTo(bx + bw, by);
      ctx.lineTo(bx + bw, by + cornerLen);
      ctx.stroke();

      // Bottom-Left
      ctx.beginPath();
      ctx.moveTo(bx, by + bh - cornerLen);
      ctx.lineTo(bx, by + bh);
      ctx.lineTo(bx + cornerLen, by + bh);
      ctx.stroke();

      // Bottom-Right
      ctx.beginPath();
      ctx.moveTo(bx + bw - cornerLen, by + bh);
      ctx.lineTo(bx + bw, by + bh);
      ctx.lineTo(bx + bw, by + bh - cornerLen);
      ctx.stroke();
    }
  };

  const getTrigunaBadge = () => {
    const triguna = telemetry?.triguna_dominant || "sattva";
    if (triguna === "rajas") {
      return {
        label: "RAJAS (AGITATED / RESTLESS)",
        bg: "bg-rose-500/20 text-rose-300 border-rose-500/40",
        dot: "bg-rose-400",
      };
    }
    if (triguna === "tamas") {
      return {
        label: "TAMAS (DEJECTED / WITHDRAWN)",
        bg: "bg-purple-500/20 text-purple-300 border-purple-500/40",
        dot: "bg-purple-400",
      };
    }
    return {
      label: "SATTVA (CENTERED / CALM)",
      bg: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
      dot: "bg-emerald-400",
    };
  };

  const trigunaInfo = getTrigunaBadge();

  return (
    <div className="relative w-full rounded-2xl overflow-hidden shadow-2xl border border-neutral-800 bg-neutral-950 font-sans">
      {/* 1. Video and Overlay Canvas */}
      <div className="relative w-full aspect-4/3 bg-black flex items-center justify-center overflow-hidden">
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={videoConstraints}
          mirrored={true}
          className="w-full h-full object-cover"
        />

        {/* HUD Canvas overlay */}
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full pointer-events-none object-cover"
          style={{ transform: "scaleX(-1)" }} // Match mirrored webcam
        />

        {/* Top Status Bar: Live State Pill */}
        <div className="absolute top-3 left-3 right-3 flex items-center justify-between gap-2 z-10 pointer-events-none">
          {/* Main Emotion & Arousal Pill */}
          <div className="flex items-center gap-2 bg-neutral-900/85 backdrop-blur-md border border-neutral-700/60 px-3 py-1.5 rounded-full text-xs font-semibold text-white shadow-lg">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75 animate-ping"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
            </span>
            <span className="tracking-wide uppercase text-[11px]">
              {detectedEmotion}
            </span>
          </div>

          {/* Gaze Vector Badge */}
          <div className="flex items-center gap-1.5 bg-neutral-900/85 backdrop-blur-md border border-neutral-700/60 px-2.5 py-1.5 rounded-full text-[10px] font-medium text-neutral-300 shadow-lg">
            <Eye className="w-3.5 h-3.5 text-sky-400" />
            <span className="uppercase">
              Gaze: {telemetry?.gaze_direction || "CENTER"}
            </span>
          </div>
        </div>

        {/* Calibrating Notification */}
        {isCalibrating && (
          <div className="absolute inset-0 bg-black/60 backdrop-blur-xs flex items-center justify-center z-20">
            <div className="flex items-center gap-2 text-xs text-neutral-300 font-mono bg-neutral-900/90 px-4 py-2 rounded-xl border border-neutral-700">
              <Activity className="w-4 h-4 text-emerald-400 animate-spin" />
              <span>Initializing Oculomotor Mesh...</span>
            </div>
          </div>
        )}
      </div>

      {/* 2. Biometric & Triguna Telemetry Panel */}
      <div className="p-3 bg-neutral-900/95 border-t border-neutral-800 space-y-2.5 text-xs">
        {/* Vedic Triguna Indicator */}
        <div className="flex items-center justify-between">
          <span className="text-[10px] uppercase font-bold tracking-wider text-neutral-400 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-400" />
            Vedic Triguna Alignment
          </span>
          <span
            className={`text-[9px] px-2 py-0.5 rounded-full border font-mono font-bold tracking-tight ${trigunaInfo.bg}`}
          >
            {trigunaInfo.label}
          </span>
        </div>

        {/* Live Gauges Grid */}
        <div className="grid grid-cols-3 gap-2">
          {/* Eye Contact Ratio */}
          <div className="bg-neutral-950/70 p-2 rounded-lg border border-neutral-800/80">
            <div className="text-[10px] text-neutral-400 font-medium">Eye Contact</div>
            <div className="text-sm font-semibold text-sky-300 font-mono mt-0.5">
              {telemetry ? `${Math.round(telemetry.eye_contact_ratio * 100)}%` : "--"}
            </div>
            <div className="w-full bg-neutral-800 h-1 rounded-full mt-1.5 overflow-hidden">
              <div
                className="bg-sky-400 h-full rounded-full transition-all duration-300"
                style={{ width: `${(telemetry?.eye_contact_ratio || 0) * 100}%` }}
              />
            </div>
          </div>

          {/* Blink Rate (BPM) */}
          <div className="bg-neutral-950/70 p-2 rounded-lg border border-neutral-800/80">
            <div className="text-[10px] text-neutral-400 font-medium">Blink Rate</div>
            <div className="text-sm font-semibold text-emerald-300 font-mono mt-0.5">
              {telemetry ? `${telemetry.blink_rate_bpm} bpm` : "--"}
            </div>
            <div className="w-full bg-neutral-800 h-1 rounded-full mt-1.5 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  (telemetry?.blink_rate_bpm || 0) > 28
                    ? "bg-rose-500"
                    : "bg-emerald-400"
                }`}
                style={{
                  width: `${Math.min(100, ((telemetry?.blink_rate_bpm || 15) / 40) * 100)}%`,
                }}
              />
            </div>
          </div>

          {/* Facial Tension Index */}
          <div className="bg-neutral-950/70 p-2 rounded-lg border border-neutral-800/80">
            <div className="text-[10px] text-neutral-400 font-medium">Facial Strain</div>
            <div className="text-sm font-semibold text-amber-300 font-mono mt-0.5">
              {telemetry
                ? `${Math.round(telemetry.facial_tension_index * 100)}%`
                : "--"}
            </div>
            <div className="w-full bg-neutral-800 h-1 rounded-full mt-1.5 overflow-hidden">
              <div
                className="bg-amber-400 h-full rounded-full transition-all duration-300"
                style={{
                  width: `${(telemetry?.facial_tension_index || 0) * 100}%`,
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebcamFeed;
