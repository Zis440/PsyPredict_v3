// src/services/biometrics.ts
/**
 * PsyPredict Biometric Visual & Oculomotor Telemetry Service
 * Powered by Google MediaPipe Face Landmarker (478 3D landmarks + 52 FACS blendshapes)
 * 
 * Extracts:
 * 1. Oculomotor Tracking: Iris gaze vectors, direct vs downcast vs darting gaze, eye contact ratio.
 * 2. Blink Dynamics (Eye Aspect Ratio - EAR): Blinks per minute, fatigue vs hyperarousal.
 * 3. Micro-Tension & Action Units: Corrugator brow furrow, masseter jaw clench, eyelid droop.
 * 4. 16+ Vast Emotional & Cognitive Taxonomy with continuous Valence, Arousal, and Distress.
 * 5. Vedic Triguna Mapping (Sattva, Rajas, Tamas).
 */

import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

export interface BiometricTelemetry {
  dominant_emotion: string;
  confidence: number;
  valence: number;              // -1.0 to +1.0
  arousal: number;              // 0.0 to 1.0
  distress_score: number;       // 0.0 to 1.0
  gaze_direction: "direct" | "downcast" | "darting" | "avoidant" | "upward";
  eye_contact_ratio: number;    // 0.0 to 1.0
  blink_rate_bpm: number;       // Blinks per minute
  facial_tension_index: number; // 0.0 to 1.0
  triguna_dominant: "sattva" | "rajas" | "tamas";
  face_box?: number[];          // [x, y, w, h] in normalized or pixel coords
  iris_landmarks?: {
    leftIris: { x: number; y: number };
    rightIris: { x: number; y: number };
  };
  notes?: string;
}

export class BiometricVisionEngine {
  private landmarker: FaceLandmarker | null = null;
  private isInitializing: boolean = false;
  private lastVideoTime: number = -1;

  // Blink tracking state
  private blinkTimestamps: number[] = [];
  private isEyeClosed: boolean = false;
  private earThreshold: number = 0.21;

  // Gaze & Saccade tracking state
  private gazeHistory: Array<{ direction: string; timestamp: number; xRatio: number; yRatio: number }> = [];
  private directGazeWindow: boolean[] = [];

  public async initialize(): Promise<void> {
    if (this.landmarker || this.isInitializing) return;
    this.isInitializing = true;

    try {
      const filesetResolver = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
      );

      this.landmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
        baseOptions: {
          modelAssetPath:
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
          delegate: "GPU",
        },
        outputFaceBlendshapes: true,
        outputFacialTransformationMatrixes: true,
        runningMode: "VIDEO",
        numFaces: 1,
      });
      console.log("[OK] MediaPipe Face Landmarker initialized successfully (GPU).");
    } catch (gpuErr) {
      console.warn("[WARN] GPU initialization failed, falling back to CPU delegate:", gpuErr);
      try {
        const filesetResolver = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
        );
        this.landmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
          baseOptions: {
            modelAssetPath:
              "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            delegate: "CPU",
          },
          outputFaceBlendshapes: true,
          outputFacialTransformationMatrixes: true,
          runningMode: "VIDEO",
          numFaces: 1,
        });
        console.log("[OK] MediaPipe Face Landmarker initialized successfully (CPU).");
      } catch (cpuErr) {
        console.error("[ERROR] Failed to initialize MediaPipe Face Landmarker:", cpuErr);
      }
    } finally {
      this.isInitializing = false;
    }
  }

  public isReady(): boolean {
    return this.landmarker !== null;
  }

  /**
   * Processes a live video frame and returns complete biometric visual telemetry.
   */
  public processVideoFrame(videoElement: HTMLVideoElement): BiometricTelemetry | null {
    if (!this.landmarker || videoElement.readyState < 2) {
      return null;
    }

    const now = performance.now();
    if (videoElement.currentTime === this.lastVideoTime) {
      return null; // Skip duplicate frame
    }
    this.lastVideoTime = videoElement.currentTime;

    const result = this.landmarker.detectForVideo(videoElement, now);
    if (!result.faceLandmarks || result.faceLandmarks.length === 0) {
      return null;
    }

    const landmarks = result.faceLandmarks[0];
    const blendshapes = result.faceBlendshapes?.[0]?.categories || [];

    // Map blendshapes to dictionary for O(1) lookup
    const bs: Record<string, number> = {};
    for (const b of blendshapes) {
      bs[b.categoryName] = b.score;
    }

    // 1. Calculate Eye Aspect Ratio (EAR) for Left & Right Eye
    // Left eye landmark indices: [33, 160, 158, 133, 153, 144]
    // Right eye landmark indices: [362, 385, 387, 263, 373, 380]
    const leftEAR = this.calculateEAR(landmarks, 33, 160, 158, 133, 153, 144);
    const rightEAR = this.calculateEAR(landmarks, 362, 385, 387, 263, 373, 380);
    const avgEAR = (leftEAR + rightEAR) / 2;

    // Blink detection
    this.updateBlinkTracking(avgEAR, now);
    const bpm = this.calculateBlinksPerMinute(now);

    // 2. Iris & Gaze Vector Tracking
    // Left Iris: 468 (center), Right Iris: 473 (center)
    const leftIris = landmarks[468] || landmarks[473] || landmarks[168];
    const rightIris = landmarks[473] || landmarks[468] || landmarks[168];

    const gaze = this.calculateGazeMetrics(landmarks, leftIris, rightIris, now);

    // 3. Facial Micro-Tension Analysis
    const browDown = ((bs["browDownLeft"] || 0) + (bs["browDownRight"] || 0)) / 2;
    const browInnerUp = bs["browInnerUp"] || 0;
    const browOuterUp = ((bs["browOuterUpLeft"] || 0) + (bs["browOuterUpRight"] || 0)) / 2;
    const mouthPress = ((bs["mouthPressLeft"] || 0) + (bs["mouthPressRight"] || 0)) / 2;
    const eyeSquint = ((bs["eyeSquintLeft"] || 0) + (bs["eyeSquintRight"] || 0)) / 2;
    const eyeWide = ((bs["eyeWideLeft"] || 0) + (bs["eyeWideRight"] || 0)) / 2;
    const mouthSmile = ((bs["mouthSmileLeft"] || 0) + (bs["mouthSmileRight"] || 0)) / 2;
    const mouthFrown = ((bs["mouthFrownLeft"] || 0) + (bs["mouthFrownRight"] || 0)) / 2;

    // Composite facial tension index (brow furrow + jaw clench + squint)
    const facialTension = Math.min(1.0, browDown * 0.45 + mouthPress * 0.35 + eyeSquint * 0.20);

    // 4. Continuous Valence & Arousal
    // Valence: positivity/pleasantness vs distress/negativity (-1.0 to 1.0)
    let valence = mouthSmile * 1.0 - mouthFrown * 0.7 - browDown * 0.5 - mouthPress * 0.3;
    valence = Math.max(-1.0, Math.min(1.0, valence));

    // Arousal: physiological activation / stress (0.0 to 1.0)
    const blinkArousal = Math.min(1.0, bpm / 35);
    let arousal = eyeWide * 0.35 + facialTension * 0.35 + blinkArousal * 0.30;
    arousal = Math.max(0.0, Math.min(1.0, arousal));

    // Distress score (0.0 to 1.0)
    let distress = 0.20;
    if (valence < 0) {
      distress = Math.min(1.0, Math.abs(valence) * 0.5 + arousal * 0.3 + (gaze.direction === "downcast" ? 0.2 : gaze.direction === "darting" ? 0.15 : 0));
    } else {
      distress = Math.max(0.05, 0.20 - valence * 0.15);
    }

    // 5. Vast 16-State Affective Classification
    const classification = this.classifyVastEmotion({
      valence,
      arousal,
      distress,
      gazeDirection: gaze.direction,
      bpm,
      browDown,
      browInnerUp,
      browOuterUp,
      mouthSmile,
      mouthFrown,
      mouthPress,
      eyeWide,
      facialTension,
      avgEAR,
    });

    // 6. Vedic Triguna Mapping
    let triguna: "sattva" | "rajas" | "tamas" = "sattva";
    if (arousal > 0.55 || gaze.direction === "darting" || facialTension > 0.45 || bpm > 26) {
      triguna = "rajas"; // Hyperarousal, restlessness, agitation
    } else if (valence < -0.25 || gaze.direction === "downcast" || (bpm < 11 && avgEAR < 0.24) || classification.emotion.includes("dejected") || classification.emotion.includes("burnout")) {
      triguna = "tamas"; // Dejection, lethargy, withdrawal, blunting
    } else {
      triguna = "sattva"; // Regulated, centered, equanimous
    }

    // Compute Face Bounding Box
    let minX = 1, minY = 1, maxX = 0, maxY = 0;
    for (const pt of landmarks) {
      if (pt.x < minX) minX = pt.x;
      if (pt.y < minY) minY = pt.y;
      if (pt.x > maxX) maxX = pt.x;
      if (pt.y > maxY) maxY = pt.y;
    }

    return {
      dominant_emotion: classification.emotion,
      confidence: classification.confidence,
      valence: Number(valence.toFixed(3)),
      arousal: Number(arousal.toFixed(3)),
      distress_score: Number(distress.toFixed(3)),
      gaze_direction: gaze.direction as any,
      eye_contact_ratio: Number(gaze.eyeContactRatio.toFixed(2)),
      blink_rate_bpm: Math.round(bpm),
      facial_tension_index: Number(facialTension.toFixed(3)),
      triguna_dominant: triguna,
      face_box: [
        Math.round(minX * (videoElement.videoWidth || 480)),
        Math.round(minY * (videoElement.videoHeight || 360)),
        Math.round((maxX - minX) * (videoElement.videoWidth || 480)),
        Math.round((maxY - minY) * (videoElement.videoHeight || 360)),
      ],
      iris_landmarks: {
        leftIris: { x: leftIris.x, y: leftIris.y },
        rightIris: { x: rightIris.x, y: rightIris.y },
      },
      notes: `${classification.emotion} | Gaze: ${gaze.direction} | Triguna: ${triguna.toUpperCase()}`,
    };
  }

  // --- Helper: Distance between two 3D landmarks ---
  private dist(p1: any, p2: any): number {
    return Math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + ((p1.z || 0) - (p2.z || 0)) ** 2);
  }

  // --- Helper: Eye Aspect Ratio (EAR) ---
  private calculateEAR(
    landmarks: any[],
    p1: number,
    p2: number,
    p3: number,
    p4: number,
    p5: number,
    p6: number
  ): number {
    const dVertical1 = this.dist(landmarks[p2], landmarks[p6]);
    const dVertical2 = this.dist(landmarks[p3], landmarks[p5]);
    const dHorizontal = this.dist(landmarks[p1], landmarks[p4]);
    if (dHorizontal === 0) return 0.25;
    return (dVertical1 + dVertical2) / (2.0 * dHorizontal);
  }

  // --- Helper: Blink tracking and frequency ---
  private updateBlinkTracking(ear: number, now: number): void {
    if (ear < this.earThreshold) {
      if (!this.isEyeClosed) {
        this.isEyeClosed = true;
        this.blinkTimestamps.push(now);
      }
    } else {
      this.isEyeClosed = false;
    }

    // Keep timestamps from the last 30 seconds
    const thirtySecAgo = now - 30_000;
    this.blinkTimestamps = this.blinkTimestamps.filter((t) => t >= thirtySecAgo);
  }

  private calculateBlinksPerMinute(now: number): number {
    const thirtySecAgo = now - 30_000;
    const recentBlinks = this.blinkTimestamps.filter((t) => t >= thirtySecAgo).length;
    // Extrapolate 30s to 60s
    return Math.min(60, recentBlinks * 2);
  }

  // --- Helper: Gaze Direction & Saccade Tracking ---
  private calculateGazeMetrics(
    landmarks: any[],
    leftIris: any,
    rightIris: any,
    now: number
  ): { direction: string; eyeContactRatio: number } {
    // Relative position of iris inside eye corners
    // Left eye corners: 33 (outer), 133 (inner)
    const leftInner = landmarks[133] || { x: 0.5, y: 0.5 };
    const leftOuter = landmarks[33] || { x: 0.4, y: 0.5 };
    const leftEyeWidth = Math.abs(leftInner.x - leftOuter.x) || 0.05;
    const leftXRatio = (leftIris.x - Math.min(leftInner.x, leftOuter.x)) / leftEyeWidth;

    // Right eye corners: 362 (inner), 263 (outer)
    const rightInner = landmarks[362] || { x: 0.5, y: 0.5 };
    const rightOuter = landmarks[263] || { x: 0.6, y: 0.5 };
    const rightEyeWidth = Math.abs(rightOuter.x - rightInner.x) || 0.05;
    const rightXRatio = (rightIris.x - Math.min(rightInner.x, rightOuter.x)) / rightEyeWidth;
    const xRatio = (leftXRatio + rightXRatio) / 2;

    // Vertical eye ratio: relative to upper lid (159) and lower lid (145)
    const upperLid = landmarks[159] || landmarks[158] || { x: 0.5, y: 0.45 };
    const lowerLid = landmarks[145] || landmarks[153] || { x: 0.5, y: 0.55 };
    const eyeHeight = Math.abs(lowerLid.y - upperLid.y) || 0.02;
    const yRatio = (leftIris.y - upperLid.y) / eyeHeight;

    let dir = "direct";
    if (yRatio > 0.70) {
      dir = "downcast"; // Looking down (dejection / shame / sorrow)
    } else if (yRatio < 0.28) {
      dir = "upward"; // Looking up (deep recall or dissociation)
    } else if (xRatio < 0.35 || xRatio > 0.65) {
      dir = "avoidant"; // Looking away laterally
    } else {
      dir = "direct"; // Centered eye contact
    }

    // Track rolling gaze history
    this.gazeHistory.push({ direction: dir, timestamp: now, xRatio, yRatio });
    const twoSecAgo = now - 2000;
    this.gazeHistory = this.gazeHistory.filter((g) => g.timestamp >= twoSecAgo);

    // Detect darting / rapid saccades (frequent direction changes within 2 seconds)
    if (this.gazeHistory.length >= 6) {
      let directionShifts = 0;
      for (let i = 1; i < this.gazeHistory.length; i++) {
        if (Math.abs(this.gazeHistory[i].xRatio - this.gazeHistory[i - 1].xRatio) > 0.15) {
          directionShifts++;
        }
      }
      if (directionShifts >= 3) {
        dir = "darting"; // Anxiety / hypervigilance / restless saccades
      }
    }

    // Eye contact window
    const isDirect = dir === "direct";
    this.directGazeWindow.push(isDirect);
    if (this.directGazeWindow.length > 50) this.directGazeWindow.shift();
    const eyeContactRatio =
      this.directGazeWindow.filter(Boolean).length / (this.directGazeWindow.length || 1);

    return { direction: dir, eyeContactRatio };
  }

  // --- Helper: Vast 16-State Affective Classifier ---
  private classifyVastEmotion(metrics: {
    valence: number;
    arousal: number;
    distress: number;
    gazeDirection: string;
    bpm: number;
    browDown: number;
    browInnerUp: number;
    browOuterUp: number;
    mouthSmile: number;
    mouthFrown: number;
    mouthPress: number;
    eyeWide: number;
    facialTension: number;
    avgEAR: number;
  }): { emotion: string; confidence: number } {
    const {
      valence,
      arousal,
      gazeDirection,
      bpm,
      browDown,
      browInnerUp,
      browOuterUp,
      mouthSmile,
      mouthFrown,
      mouthPress,
      eyeWide,
      facialTension,
      avgEAR,
    } = metrics;

    // 1. Panic / Acute Fear
    if (eyeWide > 0.45 && (browInnerUp > 0.35 || bpm > 32)) {
      return { emotion: "panic_fear", confidence: 92.5 };
    }

    // 2. Anxious / Hypervigilant
    if (gazeDirection === "darting" || (bpm > 28 && (browInnerUp > 0.25 || facialTension > 0.35))) {
      return { emotion: "anxious_hypervigilant", confidence: 88.0 };
    }

    // 3. Overwhelmed
    if (facialTension > 0.55 && browInnerUp > 0.35) {
      return { emotion: "overwhelmed", confidence: 89.0 };
    }

    // 4. Grief / Emotional Pain
    if (browInnerUp > 0.40 && mouthFrown > 0.25 && gazeDirection === "downcast") {
      return { emotion: "grief_sorrow", confidence: 91.0 };
    }

    // 5. Shame / Withdrawn
    if (gazeDirection === "downcast" && mouthSmile < 0.1 && (facialTension < 0.25 || browDown > 0.2)) {
      return { emotion: "shame_withdrawn", confidence: 86.5 };
    }

    // 6. Depressed / Dejected
    if (mouthFrown > 0.30 || (valence < -0.35 && gazeDirection === "downcast")) {
      return { emotion: "depressed_dejected", confidence: 87.0 };
    }

    // 7. Repressed Anger / Jaw Tension
    if (mouthPress > 0.40 && browDown > 0.30) {
      return { emotion: "repressed_anger", confidence: 90.0 };
    }

    // 8. Agitated / Restless
    if (facialTension > 0.45 && (gazeDirection === "darting" || arousal > 0.6)) {
      return { emotion: "agitated_restless", confidence: 85.0 };
    }

    // 9. Frustrated / Tense
    if (browDown > 0.45) {
      return { emotion: "frustrated_tense", confidence: 86.0 };
    }

    // 10. Skeptical / Guarded
    if (browOuterUp > 0.35 && gazeDirection === "avoidant") {
      return { emotion: "skeptical_guarded", confidence: 83.0 };
    }

    // 11. Cognitive Overload
    if (browDown > 0.35 && gazeDirection === "upward") {
      return { emotion: "cognitive_overload", confidence: 82.0 };
    }

    // 12. Fatigued / Burnout
    if (avgEAR < 0.22 && bpm < 12 && mouthSmile < 0.1) {
      return { emotion: "fatigued_burnout", confidence: 85.0 };
    }

    // 13. Flat Affect / Dissociated
    if (facialTension < 0.15 && Math.abs(valence) < 0.15 && eyeWide < 0.15 && bpm < 14) {
      return { emotion: "flat_affect", confidence: 80.0 };
    }

    // 14. Joyful / Grounded
    if (mouthSmile > 0.45 && facialTension < 0.30) {
      return { emotion: "joyful_grounded", confidence: 93.0 };
    }

    // 15. Calm / Serene
    if (facialTension < 0.20 && Math.abs(valence) < 0.25 && gazeDirection === "direct") {
      return { emotion: "calm_serene", confidence: 89.0 };
    }

    // 16. Default: Neutral / Attentive
    return { emotion: "neutral_attentive", confidence: 84.0 };
  }
}

// Global Singleton
export const biometricEngine = new BiometricVisionEngine();
