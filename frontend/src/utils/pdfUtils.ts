import jsPDF from 'jspdf';
import type { PsychReport, RemedyData } from '../services/api';

interface Message {
  role: "user" | "assistant";
  content: string;
  report?: PsychReport;
  remedy?: RemedyData;
  fusionScore?: number;
}

// ── Color Palette ────────────────────────────────────────────────────────────
const COLORS = {
  indigo:      [79, 70, 229]   as const,
  indigoDark:  [55, 48, 163]   as const,
  indigoLight: [238, 242, 255] as const,
  amber:       [217, 119, 6]   as const,
  amberLight:  [255, 251, 235] as const,
  amberDark:   [146, 64, 14]   as const,
  red:         [185, 28, 28]   as const,
  redLight:    [254, 242, 242] as const,
  redBorder:   [252, 165, 165] as const,
  green:       [22, 163, 74]   as const,
  greenLight:  [240, 253, 244] as const,
  yellow:      [202, 138, 4]   as const,
  yellowLight: [254, 252, 232] as const,
  orange:      [234, 88, 12]   as const,
  orangeLight: [255, 247, 237] as const,
  slate50:     [248, 250, 252] as const,
  slate100:    [241, 245, 249] as const,
  slate200:    [226, 232, 240] as const,
  slate300:    [203, 213, 225] as const,
  slate500:    [100, 116, 139] as const,
  slate700:    [51, 65, 85]    as const,
  slate800:    [30, 41, 59]    as const,
  white:       [255, 255, 255] as const,
  body:        [40, 40, 40]    as const,
  muted:       [100, 100, 100] as const,
  lightGray:   [150, 150, 150] as const,
};

const RISK_COLORS: Record<string, { text: readonly [number, number, number]; bg: readonly [number, number, number]; label: string }> = {
  MINIMAL:  { text: COLORS.green,   bg: COLORS.greenLight,   label: "Minimal Risk"  },
  LOW:      { text: [37, 99, 235],  bg: [239, 246, 255],     label: "Low Risk"      },
  MODERATE: { text: COLORS.yellow,  bg: COLORS.yellowLight,  label: "Moderate Risk" },
  HIGH:     { text: COLORS.orange,  bg: COLORS.orangeLight,  label: "High Risk"     },
  CRITICAL: { text: COLORS.red,     bg: COLORS.redLight,     label: "Critical Risk" },
};

// ── Helper: Parse Gita remedy into reference + shloka text + insight ──────
function parseGitaRemedy(raw: string): { reference: string; shlokaText: string; insight: string } {
  // Format: "[Gita, Ch X, V Y] Shloka text... Insight: explanation"
  const refMatch = raw.match(/^\[([^\]]+)\]\s*/);
  const reference = refMatch ? refMatch[1] : "";
  const withoutRef = refMatch ? raw.slice(refMatch[0].length) : raw;

  const insightIdx = withoutRef.indexOf("Insight:");
  let shlokaText: string;
  let insight: string;

  if (insightIdx !== -1) {
    shlokaText = withoutRef.slice(0, insightIdx).trim();
    insight = withoutRef.slice(insightIdx + "Insight:".length).trim();
  } else {
    shlokaText = withoutRef.trim();
    insight = "";
  }

  return { reference, shlokaText, insight };
}

// ══════════════════════════════════════════════════════════════════════════════
// Main PDF Generator
// ══════════════════════════════════════════════════════════════════════════════
export const generateChatPDF = (messages: Message[], date: string) => {
  const doc = new jsPDF();
  const PW  = doc.internal.pageSize.getWidth();   // page width
  const PH  = doc.internal.pageSize.getHeight();   // page height
  const MX  = 18;                                   // horizontal margin
  const CW  = PW - MX * 2;                         // content width
  let   Y   = 0;                                    // current Y cursor

  // ── Utility: safe page break ───────────────────────────────────────────
  const ensureSpace = (needed: number) => {
    if (Y + needed > PH - 22) {
      doc.addPage();
      Y = 22;
    }
  };

  // ── Utility: draw a thin horizontal rule ───────────────────────────────
  const drawRule = (color: readonly [number, number, number] = COLORS.slate200) => {
    doc.setDrawColor(...color);
    doc.setLineWidth(0.3);
    doc.line(MX, Y, PW - MX, Y);
    Y += 4;
  };

  // ── Utility: section heading ───────────────────────────────────────────
  const sectionHeading = (
    title: string,
    color: readonly [number, number, number] = COLORS.indigo,
    icon?: string
  ) => {
    ensureSpace(14);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(...color);
    const label = icon ? `${icon}  ${title}` : title;
    doc.text(label, MX, Y);
    Y += 2;
    doc.setDrawColor(...color);
    doc.setLineWidth(0.6);
    doc.line(MX, Y, MX + doc.getTextWidth(label) + 2, Y);
    Y += 6;
  };

  // ── Utility: field label + value ───────────────────────────────────────
  const fieldRow = (label: string, value: string, labelWidth = 42) => {
    ensureSpace(8);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.setTextColor(...COLORS.slate700);
    doc.text(label, MX + 4, Y);

    doc.setFont("helvetica", "normal");
    doc.setTextColor(...COLORS.body);
    const lines = doc.splitTextToSize(value, CW - labelWidth - 8);
    doc.text(lines, MX + labelWidth, Y);
    Y += lines.length * 4.5 + 2;
  };

  // ══════════════════════════════════════════════════════════════════════════
  // PAGE 1 — COVER / HEADER
  // ══════════════════════════════════════════════════════════════════════════

  // Top accent bar
  doc.setFillColor(...COLORS.indigo);
  doc.rect(0, 0, PW, 4, 'F');

  // Branding
  Y = 18;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(26);
  doc.setTextColor(...COLORS.indigo);
  doc.text("PsyPredict", MX, Y);

  // Subtitle
  Y += 8;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  doc.setTextColor(...COLORS.slate500);
  doc.text("Comprehensive Clinical AI Assessment Report", MX, Y);

  // Date (right-aligned)
  const dateStr = `Generated: ${new Date(date).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}  •  ${new Date(date).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}`;
  doc.setFontSize(9);
  doc.setTextColor(...COLORS.muted);
  doc.text(dateStr, PW - MX, Y, { align: "right" });

  Y += 8;
  drawRule(COLORS.indigo);

  // ── Collect summary stats ──────────────────────────────────────────────
  const totalMessages = messages.length;
  const userMessages  = messages.filter(m => m.role === "user").length;
  const aiMessages    = messages.filter(m => m.role === "assistant").length;
  const lastReport    = [...messages].reverse().find(m => m.report)?.report;
  const lastRemedy    = [...messages].reverse().find(m => m.remedy)?.remedy;
  const riskLevel     = lastReport?.risk_classification ?? "N/A";

  // ── Session Overview Box ───────────────────────────────────────────────
  const colW = CW / 4;
  const conditionText = lastRemedy?.condition ?? "—";

  // Pre-measure condition text to compute dynamic box height
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  const conditionLines = doc.splitTextToSize(conditionText, colW - 10);
  const boxH = Math.max(28, 18 + conditionLines.length * 4.5);

  ensureSpace(boxH + 4);
  doc.setFillColor(...COLORS.slate50);
  doc.setDrawColor(...COLORS.slate200);
  doc.setLineWidth(0.3);
  doc.roundedRect(MX, Y, CW, boxH, 3, 3, 'FD');

  const boxY = Y + 7;
  const valY = Y + 16;

  // Column labels
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(...COLORS.muted);
  doc.text("SESSION DATE", MX + 6, boxY);
  doc.text("MESSAGES", MX + colW + 6, boxY);
  doc.text("RISK LEVEL", MX + colW * 2 + 6, boxY);
  doc.text("CONDITION", MX + colW * 3 + 6, boxY);

  // Column values
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(...COLORS.slate800);
  doc.text(new Date(date).toLocaleDateString("en-IN"), MX + 6, valY);
  doc.text(`${totalMessages} (${userMessages} client, ${aiMessages} AI)`, MX + colW + 6, valY);

  // Risk colored
  const riskCfg = RISK_COLORS[riskLevel];
  if (riskCfg) {
    doc.setTextColor(...riskCfg.text);
    doc.text(riskCfg.label, MX + colW * 2 + 6, valY);
  } else {
    doc.text(riskLevel, MX + colW * 2 + 6, valY);
  }

  // Condition — wrapped within column
  doc.setTextColor(...COLORS.slate800);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.text(conditionLines, MX + colW * 3 + 6, valY);

  Y += boxH + 6;

  // ── Medical Disclaimer ─────────────────────────────────────────────────
  const disclaimerText = "This record is generated by an automated AI system for educational and preliminary screening purposes only. It is NOT a verified medical diagnosis, prescription, or professional psychiatric evaluation. Please share this document with a certified healthcare professional for proper evaluation. In case of an emergency or crisis, contact local emergency services immediately.";
  const splitDisclaimer = doc.splitTextToSize(disclaimerText, CW - 14);
  const disclaimerH = splitDisclaimer.length * 4 + 12;

  ensureSpace(disclaimerH + 2);
  doc.setFillColor(...COLORS.redLight);
  doc.setDrawColor(...COLORS.redBorder);
  doc.setLineWidth(0.4);
  doc.roundedRect(MX, Y, CW, disclaimerH, 3, 3, 'FD');

  // Left red accent strip
  doc.setFillColor(...COLORS.red);
  doc.roundedRect(MX, Y, 3, disclaimerH, 1.5, 1.5, 'F');

  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(...COLORS.red);
  doc.text("MEDICAL DISCLAIMER", MX + 8, Y + 6);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(120, 30, 30);
  doc.text(splitDisclaimer, MX + 8, Y + 12);
  Y += disclaimerH + 8;

  // ════════════════════════════════════════════════════════════════════════
  // SECTION: FULL CONVERSATION TRANSCRIPT
  // ════════════════════════════════════════════════════════════════════════
  sectionHeading("CONVERSATION TRANSCRIPT");

  messages.forEach((msg, idx) => {
    const isUser   = msg.role === "user";
    const speaker  = isUser ? "Client" : "PsyPredict AI";
    const accent: readonly [number, number, number] = isUser ? COLORS.indigo : COLORS.slate500;

    // Speaker badge
    ensureSpace(12);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.setTextColor(...accent);
    doc.text(`${speaker}`, MX + 1, Y);

    // Message number
    doc.setFont("helvetica", "normal");
    doc.setFontSize(7);
    doc.setTextColor(...COLORS.lightGray);
    doc.text(`#${idx + 1}`, PW - MX, Y, { align: "right" });
    Y += 4;

    // Message content
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(...COLORS.body);
    const splitContent = doc.splitTextToSize(msg.content, CW - 8);

    // Process lines in chunks to handle page breaks properly
    for (let i = 0; i < splitContent.length; i++) {
      ensureSpace(5);
      doc.text(splitContent[i], MX + 4, Y);
      Y += 4.2;
    }
    Y += 2;

    // ── Clinical Assessment (inline after AI message) ────────────────
    if (!isUser && msg.report) {
      const r = msg.report;
      const risk = RISK_COLORS[r.risk_classification] ?? RISK_COLORS.MINIMAL;

      ensureSpace(16);

      // Assessment box header
      doc.setFillColor(...COLORS.indigoLight);
      doc.setDrawColor(...COLORS.indigo);
      doc.setLineWidth(0.3);
      doc.roundedRect(MX + 2, Y - 2, CW - 4, 10, 2, 2, 'FD');
      doc.setFont("helvetica", "bold");
      doc.setFontSize(8);
      doc.setTextColor(...COLORS.indigo);
      doc.text("CLINICAL ASSESSMENT", MX + 6, Y + 4);

      // Risk badge (right side of header)
      const badgeText = risk.label;
      const badgeW = doc.getTextWidth(badgeText) + 8;
      doc.setFillColor(...risk.bg);
      doc.roundedRect(PW - MX - badgeW - 6, Y - 1, badgeW, 8, 2, 2, 'F');
      doc.setFontSize(7);
      doc.setTextColor(...risk.text);
      doc.text(badgeText, PW - MX - badgeW - 2, Y + 4);

      // Confidence
      if (r.confidence_score != null) {
        const confText = `Confidence: ${(r.confidence_score * 100).toFixed(0)}%`;
        const confW = doc.getTextWidth(confText) + 6;
        doc.setFillColor(...COLORS.slate100);
        doc.roundedRect(PW - MX - badgeW - confW - 10, Y - 1, confW, 8, 2, 2, 'F');
        doc.setTextColor(...COLORS.slate500);
        doc.text(confText, PW - MX - badgeW - confW - 7, Y + 4);
      }

      Y += 12;

      // Emotional state
      fieldRow("Emotional State:", r.emotional_state_summary, 34);

      // Behavioral inference
      fieldRow("Behavioral Inference:", r.behavioral_inference, 40);

      // Cognitive distortions
      if (r.cognitive_distortions && r.cognitive_distortions.length > 0) {
        ensureSpace(10);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(8);
        doc.setTextColor(...COLORS.slate700);
        doc.text("Cognitive Distortions:", MX + 4, Y);
        Y += 5;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        let tagX = MX + 6;
        r.cognitive_distortions.forEach((d) => {
          const tw = doc.getTextWidth(d) + 8;
          if (tagX + tw > PW - MX) {
            tagX = MX + 6;
            Y += 7;
            ensureSpace(8);
          }
          doc.setFillColor(...COLORS.indigoLight);
          doc.roundedRect(tagX, Y - 3.5, tw, 6, 2, 2, 'F');
          doc.setTextColor(...COLORS.indigo);
          doc.text(d, tagX + 4, Y);
          tagX += tw + 3;
        });
        Y += 8;
      }

      // Suggested interventions
      if (r.suggested_interventions && r.suggested_interventions.length > 0) {
        ensureSpace(10);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(8);
        doc.setTextColor(...COLORS.slate700);
        doc.text("Suggested Interventions:", MX + 4, Y);
        Y += 5;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.setTextColor(...COLORS.body);
        r.suggested_interventions.forEach((s) => {
          const lines = doc.splitTextToSize(`•  ${s}`, CW - 18);
          for (const line of lines) {
            ensureSpace(5);
            doc.text(line, MX + 8, Y);
            Y += 4.2;
          }
          Y += 1;
        });
        Y += 2;
      }

      // Crisis resources
      if (r.crisis_triggered && r.crisis_resources && r.crisis_resources.length > 0) {
        ensureSpace(16);
        doc.setFillColor(...COLORS.redLight);
        doc.setDrawColor(...COLORS.redBorder);
        doc.roundedRect(MX + 2, Y - 2, CW - 4, 8, 2, 2, 'FD');
        doc.setFont("helvetica", "bold");
        doc.setFontSize(8);
        doc.setTextColor(...COLORS.red);
        doc.text("CRISIS SUPPORT RESOURCES", MX + 6, Y + 3);
        Y += 10;

        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        r.crisis_resources.forEach((cr) => {
          ensureSpace(6);
          doc.setTextColor(...COLORS.red);
          doc.setFont("helvetica", "bold");
          doc.text(`${cr.name}:`, MX + 6, Y);
          doc.setFont("helvetica", "normal");
          doc.setTextColor(...COLORS.body);
          doc.text(`${cr.contact}  (${cr.available})`, MX + 6 + doc.getTextWidth(`${cr.name}: `), Y);
          Y += 5;
        });
        Y += 2;
      }

      // ── Remedy / Ancient Wisdom ────────────────────────────────────
      if (msg.remedy) {
        const rem = msg.remedy;
        ensureSpace(20);

        // Amber section header
        doc.setFillColor(...COLORS.amberLight);
        doc.setDrawColor(...COLORS.amber);
        doc.setLineWidth(0.3);
        doc.roundedRect(MX + 2, Y - 2, CW - 4, 10, 2, 2, 'FD');
        doc.setFont("helvetica", "bold");
        doc.setFontSize(8);
        doc.setTextColor(...COLORS.amber);
        doc.text("ANCIENT WISDOM & CARE PLAN", MX + 6, Y + 4);

        // Condition badge
        if (rem.condition) {
          const cBadge = rem.condition;
          const cBadgeW = doc.getTextWidth(cBadge) + 8;
          doc.setFillColor(...COLORS.amberLight);
          doc.roundedRect(PW - MX - cBadgeW - 6, Y - 1, cBadgeW, 8, 2, 2, 'F');
          doc.setFontSize(7);
          doc.setTextColor(...COLORS.amberDark);
          doc.text(cBadge, PW - MX - cBadgeW - 2, Y + 4);
        }

        Y += 14;

        // Gita Shloka
        if (rem.gita_remedy) {
          const parsed = parseGitaRemedy(rem.gita_remedy);

          ensureSpace(10);
          doc.setFont("helvetica", "bold");
          doc.setFontSize(8);
          doc.setTextColor(...COLORS.amberDark);
          doc.text("Bhagavad Gita Wisdom", MX + 4, Y);
          
          const labelWidth = doc.getTextWidth("Bhagavad Gita Wisdom  ");

          if (parsed.reference) {
            doc.setFont("helvetica", "normal");
            doc.setFontSize(7);
            doc.setTextColor(...COLORS.amber);
            doc.text(`[${parsed.reference}]`, MX + 4 + labelWidth, Y);
          }
          Y += 5;

          // Shloka text (italic, quoted)
          doc.setFont("helvetica", "italic");
          doc.setFontSize(9);
          doc.setTextColor(80, 60, 20);
          const shlokaLines = doc.splitTextToSize(`"${parsed.shlokaText}"`, CW - 16);
          for (const line of shlokaLines) {
            ensureSpace(5);
            doc.text(line, MX + 8, Y);
            Y += 4.5;
          }
          Y += 2;

          // Insight
          if (parsed.insight) {
            ensureSpace(8);
            doc.setFont("helvetica", "bold");
            doc.setFontSize(8);
            doc.setTextColor(...COLORS.amberDark);
            doc.text("Insight:", MX + 4, Y);
            Y += 4;

            doc.setFont("helvetica", "normal");
            doc.setFontSize(8.5);
            doc.setTextColor(...COLORS.body);
            const insightLines = doc.splitTextToSize(parsed.insight, CW - 14);
            for (const line of insightLines) {
              ensureSpace(5);
              doc.text(line, MX + 8, Y);
              Y += 4.2;
            }
            Y += 3;
          }
        }

        // Medications & Dosage (side-by-side look)
        if (rem.medications || rem.dosage) {
          ensureSpace(14);
          const halfW = (CW - 10) / 2;

          // Medications box
          doc.setFillColor(...COLORS.white);
          doc.setDrawColor(...COLORS.slate200);
          doc.setLineWidth(0.2);
          doc.roundedRect(MX + 4, Y - 2, halfW, 6, 1.5, 1.5, 'FD');
          doc.setFont("helvetica", "bold");
          doc.setFontSize(7);
          doc.setTextColor(...COLORS.red);
          doc.text("MEDICATIONS", MX + 8, Y + 2);

          // Dosage box
          doc.setFillColor(...COLORS.white);
          doc.setDrawColor(...COLORS.slate200);
          doc.roundedRect(MX + halfW + 8, Y - 2, halfW, 6, 1.5, 1.5, 'FD');
          doc.setTextColor(...COLORS.red);
          doc.text("DOSAGE", MX + halfW + 12, Y + 2);
          Y += 8;

          // Medication content
          doc.setFont("helvetica", "normal");
          doc.setFontSize(8);
          doc.setTextColor(...COLORS.body);
          const medLines = doc.splitTextToSize(rem.medications || "—", halfW - 8);
          const dosLines = doc.splitTextToSize(rem.dosage || "—", halfW - 8);
          const maxRows = Math.max(medLines.length, dosLines.length);

          for (let i = 0; i < maxRows; i++) {
            ensureSpace(5);
            if (medLines[i]) doc.text(medLines[i], MX + 8, Y);
            if (dosLines[i]) doc.text(dosLines[i], MX + halfW + 12, Y);
            Y += 4.2;
          }
          Y += 3;
        }

        // Recommended Treatments
        if (rem.treatments) {
          ensureSpace(10);
          doc.setFont("helvetica", "bold");
          doc.setFontSize(8);
          doc.setTextColor(...COLORS.slate700);
          doc.text("Recommended Treatments:", MX + 4, Y);
          Y += 4.5;

          doc.setFont("helvetica", "normal");
          doc.setFontSize(8);
          doc.setTextColor(...COLORS.body);
          const tLines = doc.splitTextToSize(rem.treatments, CW - 14);
          for (const line of tLines) {
            ensureSpace(5);
            doc.text(line, MX + 8, Y);
            Y += 4.2;
          }
          Y += 2;
        }

        // Medication warning
        ensureSpace(8);
        doc.setFont("helvetica", "italic");
        doc.setFontSize(7);
        doc.setTextColor(...COLORS.muted);
        doc.text("Always consult a licensed healthcare professional before taking any medication.", MX + 4, Y);
        Y += 6;
      }

      // Divider after assessment block
      drawRule(COLORS.slate200);
      Y += 2;
    }

    // Light separator between messages (if no assessment was rendered)
    if (isUser || !msg.report) {
      if (idx < messages.length - 1) {
        ensureSpace(4);
        doc.setDrawColor(...COLORS.slate100);
        doc.setLineWidth(0.15);
        doc.line(MX + 4, Y, PW - MX - 4, Y);
        Y += 4;
      }
    }
  });

  // ════════════════════════════════════════════════════════════════════════
  // FOOTER — Page numbers on every page
  // ════════════════════════════════════════════════════════════════════════
  const totalPages = doc.getNumberOfPages();
  const refCode = new Date().getTime().toString(36).toUpperCase();

  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    // Top accent bar (on every page)
    doc.setFillColor(...COLORS.indigo);
    doc.rect(0, 0, PW, 4, 'F');

    // Footer line
    doc.setDrawColor(...COLORS.slate200);
    doc.setLineWidth(0.3);
    doc.line(MX, PH - 16, PW - MX, PH - 16);

    // Footer text
    doc.setFontSize(7);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(...COLORS.lightGray);
    doc.text("PsyPredict AI  •  Consultation Record", MX, PH - 10);
    doc.text(`Page ${i} of ${totalPages}`, PW / 2, PH - 10, { align: "center" });
    doc.text(`Ref: ${refCode}`, PW - MX, PH - 10, { align: "right" });
  }

  // ── Save ────────────────────────────────────────────────────────────────
  doc.save(`PsyPredict_Clinical_Report_${new Date().toISOString().split('T')[0]}.pdf`);
};
