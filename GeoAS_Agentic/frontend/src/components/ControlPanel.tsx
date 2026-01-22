import { Globe, Mic, Keyboard, Camera, Info, LogOut, User } from "lucide-react";
import VoiceInput from "./VoiceInput";
import TextInput from "./TextInput";
import ViolationInput from "./ViolationInput";
import ResponseBox from "./ResponseBox";
import TTSButtons from "./TTSButtons";
import ReserveInfoCard from "./ReserveInfoCard";
import { Button } from "@/components/ui/button";

interface ReserveInfo {
  name: string;
  protectionLevel: "high" | "medium" | "low";
  isInside: boolean;
}

interface ControlPanelProps {
  mode: "voice" | "text" | "violation";
  onModeChange: (mode: "voice" | "text" | "violation") => void;
  response: string;
  status: string;
  ttsEnabled: boolean;
  isProcessing: boolean;
  onMicClick: () => void;
  onSendText: (query: string) => void;
  onImageUpload: (file: File) => void;
  onEnableTTS: () => void;
  onStopTTS: () => void;
  reserveInfo: ReserveInfo | null;
  userId: string;
  onLogout: () => void;
}

const ControlPanel = ({
  mode,
  onModeChange,
  response,
  status,
  ttsEnabled,
  isProcessing,
  onMicClick,
  onSendText,
  onImageUpload,
  onEnableTTS,
  onStopTTS,
  reserveInfo,
  userId,
  onLogout
}: ControlPanelProps) => {
  return (
    <section className="control-section pb-20">
      {/* Header */}
      <header className="header-bar sticky top-0 z-10">
        <div className="logo-group">
          <div className="logo-icon">
            <Globe className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="logo-text">نظام المساعدة المكانية</h1>
            <p className="logo-subtitle">Geospatial Assistance System</p>
          </div>
        </div>
        
        {/* User Info & Logout */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 bg-primary/10 rounded-full px-3 py-1.5">
            <User className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary">{userId}</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onLogout}
            className="h-8 w-8 text-muted-foreground hover:text-destructive"
            title="تسجيل الخروج"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </header>

      <div className="p-5 space-y-5">
        {/* Reserve Info Card - Shows when coordinates are entered */}
        <ReserveInfoCard info={reserveInfo} />

        {/* Mode Selector - 3 tabs */}
        <div className="panel-card">
          <div className="mode-tabs three-cols">
            <button onClick={() => onModeChange("voice")} className={`mode-tab ${mode === "voice" ? "active" : ""}`}>
              <Mic className="w-4 h-4" />
              <span>التحدث</span>
            </button>
            <button onClick={() => onModeChange("text")} className={`mode-tab ${mode === "text" ? "active" : ""}`}>
              <Keyboard className="w-4 h-4" />
              <span>الكتابة</span>
            </button>
            <button onClick={() => onModeChange("violation")} className={`mode-tab ${mode === "violation" ? "active" : ""}`}>
              <Camera className="w-4 h-4" />
              <span>توثيق المخالفة</span>
            </button>
          </div>
        </div>

        {/* Hint */}
        <div className="hint-box">
          <Info className="w-4 h-4 text-muted-foreground shrink-0 mt-0.5" />
          <p className="hint-text">
            {mode === "violation" ? "ارفع صورة المخالفة وسيتم تخزينها في قاعدة البيانات." : "ملاحظة: الرد الصوتي يتم عبر المتصفح. قد تحتاج لتفعيل الصوت أول مرة."}
          </p>
        </div>

        {/* Input Section */}
        <div className="panel-card">
          {mode === "voice" ? (
            <VoiceInput isListening={isProcessing} onMicClick={onMicClick} />
          ) : mode === "text" ? (
            <TextInput onSend={onSendText} isProcessing={isProcessing} />
          ) : (
            <ViolationInput onImageUpload={onImageUpload} isProcessing={isProcessing} response={response} />
          )}
        </div>

        {/* Response - only show for voice and text modes */}
        {mode !== "violation" && (
          <div className="panel-card">
            <ResponseBox response={response} status={status} />
          </div>
        )}

        {/* TTS Controls - only for voice mode */}
        {mode === "voice" && (
          <div className="panel-card">
            <TTSButtons ttsEnabled={ttsEnabled} onEnable={onEnableTTS} onStop={onStopTTS} />
          </div>
        )}
      </div>
    </section>
  );
};

export default ControlPanel;