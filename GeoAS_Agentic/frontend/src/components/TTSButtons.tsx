import { Volume2, VolumeX } from "lucide-react";

interface TTSButtonsProps {
  ttsEnabled: boolean;
  onEnable: () => void;
  onStop: () => void;
}

const TTSButtons = ({ ttsEnabled, onEnable, onStop }: TTSButtonsProps) => {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <button onClick={onEnable} className="btn-secondary">
        <Volume2 className="w-4 h-4" />
        <span>تفعيل الصوت</span>
      </button>
      <button onClick={onStop} className="btn-secondary">
        <VolumeX className="w-4 h-4" />
        <span>إيقاف الصوت</span>
      </button>
      <span className={`status-badge ${ttsEnabled ? "active" : "inactive"}`}>
        الصوت: {ttsEnabled ? "مفعّل" : "غير مفعّل"}
      </span>
    </div>
  );
};

export default TTSButtons;