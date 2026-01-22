import { motion } from "framer-motion";
import { Mic } from "lucide-react";

interface VoiceSectionProps {
  isListening: boolean;
  onMicClick: () => void;
}

const VoiceSection = ({ isListening, onMicClick }: VoiceSectionProps) => {
  return (
    <motion.div 
      className="flex justify-center items-center min-h-[220px]"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <button
        onClick={onMicClick}
        disabled={isListening}
        className={`voice-button ${isListening ? "animate-pulse-glow" : ""}`}
      >
        <Mic className="w-12 h-12 mb-2" />
        <span className="text-lg font-bold">
          {isListening ? "أستمع..." : "تحدث الآن"}
        </span>
      </button>
    </motion.div>
  );
};

export default VoiceSection;
