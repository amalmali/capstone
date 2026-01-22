import { Mic } from "lucide-react";

interface VoiceInputProps {
  isListening: boolean;
  onMicClick: () => void;
}

const VoiceInput = ({ isListening, onMicClick }: VoiceInputProps) => {
  return (
    <div className="flex flex-col items-center py-6">
      <button
        onClick={onMicClick}
        disabled={isListening}
        className={`voice-btn ${isListening ? "listening" : ""}`}
      >
        <Mic className="w-10 h-10 text-primary-foreground mb-1" />
        <span className="text-sm font-semibold text-primary-foreground">
          {isListening ? "أستمع..." : "تحدث الآن"}
        </span>
      </button>
      <p className="text-xs text-muted-foreground mt-4">
        اضغط على الزر وتحدث بوضوح
      </p>
    </div>
  );
};

export default VoiceInput;