import { motion } from "framer-motion";
import { Bot, Info } from "lucide-react";
import VoiceSection from "./VoiceSection";
import TextSection from "./TextSection";
import ResponseCard from "./ResponseCard";
import TTSControls from "./TTSControls";

interface AssistantPanelProps {
  mode: "voice" | "text";
  response: string;
  status: string;
  ttsEnabled: boolean;
  isProcessing: boolean;
  onMicClick: () => void;
  onSendText: (query: string) => void;
  onImageUpload: (file: File) => void;
  onEnableTTS: () => void;
  onStopTTS: () => void;
}

const AssistantPanel = ({
  mode,
  response,
  status,
  ttsEnabled,
  isProcessing,
  onMicClick,
  onSendText,
  onImageUpload,
  onEnableTTS,
  onStopTTS,
}: AssistantPanelProps) => {
  return (
    <motion.div
      className="panel"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
          <Bot className="w-5 h-5 text-primary" />
        </div>
        <h3 className="section-title mb-0">المساعد</h3>
      </div>

      <div className="flex items-start gap-2 p-3 rounded-lg bg-muted/30 border border-white/5 mb-5">
        <Info className="w-4 h-4 text-muted-foreground shrink-0 mt-0.5" />
        <p className="hint-text">
          ملاحظة: الرد الصوتي يتم عبر المتصفح (قد تحتاجي أول مرة تضغطي زر "تفعيل الصوت").
        </p>
      </div>

      {mode === "voice" ? (
        <VoiceSection isListening={isProcessing} onMicClick={onMicClick} />
      ) : (
        <TextSection
          onSend={onSendText}
          onImageUpload={onImageUpload}
          isProcessing={isProcessing}
        />
      )}

      <div className="my-5 border-t border-white/5" />

      <ResponseCard response={response} status={status} />

      {mode === "voice" && (
        <TTSControls
          ttsEnabled={ttsEnabled}
          onEnable={onEnableTTS}
          onStop={onStopTTS}
        />
      )}
    </motion.div>
  );
};

export default AssistantPanel;
