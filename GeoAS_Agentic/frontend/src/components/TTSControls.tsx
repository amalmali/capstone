import { Volume2, VolumeX } from "lucide-react";

interface TTSControlsProps {
  ttsEnabled: boolean;
  onEnable: () => void;
  onStop: () => void;
}

const TTSControls = ({ ttsEnabled, onEnable, onStop }: TTSControlsProps) => {
  return (
    <div className="flex flex-wrap items-center gap-3 mt-4">
      <button
        onClick={onEnable}
        className="btn-secondary flex items-center gap-2"
      >
        <Volume2 className="w-4 h-4" />
        <span>تفعيل الصوت</span>
      </button>
      <button
        onClick={onStop}
        className="btn-secondary flex items-center gap-2"
      >
        <VolumeX className="w-4 h-4" />
        <span>إيقاف الصوت</span>
      </button>
      <span className={`status-badge ${ttsEnabled ? "text-success" : "text-muted-foreground"}`}>
        TTS: {ttsEnabled ? "مفعّل" : "غير مفعّل"}
      </span>
    </div>
  );
};

export default TTSControls;
