import { motion } from "framer-motion";
import { Mic, Keyboard } from "lucide-react";

interface ModeSelectorProps {
  mode: "voice" | "text";
  onModeChange: (mode: "voice" | "text") => void;
}

const ModeSelector = ({ mode, onModeChange }: ModeSelectorProps) => {
  return (
    <motion.div 
      className="flex justify-center mb-8"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <div className="mode-selector">
        <button
          onClick={() => onModeChange("voice")}
          className={`mode-btn flex items-center gap-2 ${mode === "voice" ? "active" : ""}`}
        >
          <Mic className="w-4 h-4" />
          <span>التحدث</span>
        </button>
        <button
          onClick={() => onModeChange("text")}
          className={`mode-btn flex items-center gap-2 ${mode === "text" ? "active" : ""}`}
        >
          <Keyboard className="w-4 h-4" />
          <span>الكتابة</span>
        </button>
      </div>
    </motion.div>
  );
};

export default ModeSelector;
