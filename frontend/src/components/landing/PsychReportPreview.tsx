import { Lightbulb, CheckCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import BlurFade from "@/components/magicui/blur-fade";

export const PsychReportPreview = () => {
  return (
    <section className="py-24 px-6 max-w-6xl mx-auto">
      <div className="text-center mb-16">
        <Badge className="mb-4 bg-emerald-50 text-emerald-700 border-none hover:bg-emerald-100">
          Clinical Rigor
        </Badge>
        <h2 className="text-3xl md:text-4xl font-bold mb-4">Structured Insights, Not Just Chat.</h2>
        <p className="text-slate-500 max-w-2xl mx-auto">
          Every session generates a professional PsychReport. No generic advice—only
          actionable, clinical-grade analysis.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-12 items-center">
        <BlurFade delay={0.1} inView className="md:order-1">
          <Card className="shadow-2xl border-indigo-100 overflow-hidden bg-white">
            <div className="bg-indigo-600 p-4 text-white flex justify-between items-center">
              <span className="font-bold text-sm tracking-widest uppercase">PsychReport-Draft-01</span>
              <Badge className="bg-white/20 text-white border-none">CONFIDENTIAL</Badge>
            </div>
            <CardContent className="p-6 space-y-6">
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Risk Classification</p>
                <div className="flex items-center gap-3">
                  <div className="h-2 flex-1 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-yellow-400 w-[65%]" />
                  </div>
                  <span className="text-xs font-bold text-yellow-600">MODERATE (0.65)</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Text Sentiment</p>
                  <p className="text-xs font-semibold">Reflective / Anxious</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Emotion Fusion</p>
                  <p className="text-xs font-semibold">Weighted Sync Active</p>
                </div>
              </div>

              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Cognitive Distortions Detected</p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline" className="text-indigo-600 border-indigo-100 bg-indigo-50/30">Catastrophizing</Badge>
                  <Badge variant="outline" className="text-indigo-600 border-indigo-100 bg-indigo-50/30">Overgeneralization</Badge>
                </div>
              </div>

              <div className="p-4 bg-indigo-50/50 rounded-xl border border-indigo-100">
                <div className="flex gap-2 items-start mb-2">
                  <Lightbulb size={16} className="text-indigo-600 mt-0.5" />
                  <p className="text-xs font-bold">Suggested Intervention</p>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Practice 5-4-3-2-1 grounding technique to manage immediate sensory overload
                  detected in facial micro-expressions.
                </p>
              </div>
            </CardContent>
          </Card>
        </BlurFade>

        <div className="space-y-8">
          {[
            {
              title: "CBT Pattern Recognition",
              desc: "Automatically identifies 12+ cognitive distortions like emotional reasoning and all-or-nothing thinking.",
            },
            {
              title: "Behavioral Inference",
              desc: "Tracks session-over-session progress to detect long-term behavioral trends and trigger early warnings.",
            },
            {
              title: "Structured API Output",
              desc: "Built for developers and clinicians. Responses are Pydantic-validated JSON for easy integration.",
            },
          ].map((item, i) => (
            <div key={i} className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
                <CheckCircle className="text-indigo-600" size={20} />
              </div>
              <div>
                <h4 className="font-bold mb-1">{item.title}</h4>
                <p className="text-sm text-slate-500">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
