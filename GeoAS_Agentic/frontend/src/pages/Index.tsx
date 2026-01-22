import { useState, useCallback } from "react";
import { AnimatePresence } from "framer-motion";
import MapSection from "@/components/MapSection";
import ControlPanel from "@/components/ControlPanel";
import StatusFooter from "@/components/StatusFooter";
import SplashScreen from "@/components/SplashScreen";
import { sendQuery, addPoint, analyzeImage, voiceInteraction } from "@/services/api";

interface ReserveInfo {
  name: string;
  protectionLevel: "high" | "medium" | "low";
  isInside: boolean;
}

const Index = () => {
  const [showSplash, setShowSplash] = useState(true);
  const [mode, setMode] = useState<"voice" | "text" | "violation">("voice");
  const [response, setResponse] = useState("جاهزة 👋");
  const [status, setStatus] = useState("");
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [reserveInfo, setReserveInfo] = useState<ReserveInfo | null>(null);
  const [statusBar, setStatusBar] = useState<{
    status: "success" | "danger" | "neutral";
    message: string;
  }>({ status: "neutral", message: "جاهز..." });
  const [userId, setUserId] = useState<string>("");

  const handleSplashFinish = useCallback((id: string) => {
    setUserId(id);
    setShowSplash(false);
    setStatusBar({
      status: "success",
      message: `✅ تم تسجيل الدخول بـ ID: ${id}`,
    });
  }, []);

  const handleLogout = useCallback(() => {
    setUserId("");
    setShowSplash(true);
    setStatusBar({
      status: "neutral",
      message: "جاهز...",
    });
  }, []);

  // TTS Functions
  const speak = useCallback((text: string) => {
    if (!ttsEnabled || !text) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "ar-SA";
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.error("TTS error:", e);
    }
  }, [ttsEnabled]);

  const handleEnableTTS = useCallback(() => {
    setTtsEnabled(true);
    setStatus("✅ تم تفعيل الصوت بالمتصفح");
    const utterance = new SpeechSynthesisUtterance("تم تفعيل الصوت");
    utterance.lang = "ar-SA";
    window.speechSynthesis.speak(utterance);
  }, []);

  const handleStopTTS = useCallback(() => {
    window.speechSynthesis.cancel();
    setStatus("⏹️ تم إيقاف الصوت");
  }, []);

  // Voice input handler - calls backend voice endpoint
  const handleMicClick = useCallback(async () => {
    setIsProcessing(true);
    setResponse("🎙️ أستمع...");
    setStatus("لو أول مرة، فعّلي الصوت بالمتصفح من زر 🔊");

    try {
      const data = await voiceInteraction(false);
      
      if (data.status === "no_speech") {
        setResponse("ما التقطت صوت. جرّبي مرة ثانية.");
        setStatus("");
      } else {
        const responseText = data.response || "تم";
        setResponse(responseText);
        setStatus("");
        speak(responseText);
      }
    } catch (error) {
      console.error("Voice API error:", error);
      setResponse("❌ صار خطأ أثناء التسجيل.");
      setStatus("تأكدي أن السيرفر شغال.");
    } finally {
      setIsProcessing(false);
    }
  }, [speak]);

  // Text input handler - calls backend voice endpoint with query
  const handleSendText = useCallback(async (query: string) => {
    setIsProcessing(true);
    setResponse("🤖 أفكر...");
    setStatus("");

    try {
      const data = await sendQuery(query, false);
      
      if (data.status === "no_speech") {
        setResponse("ما وصلني سؤال.");
      } else {
        const responseText = data.response || "تم";
        setResponse(responseText);
        speak(responseText);
      }
    } catch (error) {
      console.error("Text API error:", error);
      setResponse("❌ صار خطأ أثناء السؤال.");
      setStatus("تأكدي أن السيرفر شغال.");
    } finally {
      setIsProcessing(false);
    }
  }, [speak]);

  // Image upload handler - calls backend analyze-image endpoint
  const handleImageUpload = useCallback(async (file: File) => {
    setResponse("🧠 جاري تحليل الصورة...");
    setStatus("");

    try {
      const data = await analyzeImage(file);
      
      if (data.status === "error") {
        setResponse("❌ فشل تحليل الصورة.");
        setStatus(data.details || "تأكدي أن سيرفر VLM شغال.");
      } else {
        const resultText = data.violation_type 
          ? `نوع المخالفة: ${data.violation_type}${data.violation_severity ? ` - الخطورة: ${data.violation_severity}` : ""}${data.people_count ? ` - عدد الأشخاص: ${data.people_count}` : ""}`
          : JSON.stringify(data, null, 2);
        setResponse(resultText);
        speak(resultText);
      }
    } catch (error) {
      console.error("Image API error:", error);
      setResponse("❌ فشل تحليل الصورة.");
      setStatus("تأكدي أن السيرفر شغال.");
    }
  }, [speak]);

  // Add point to map handler - calls backend add-point endpoint
  const handleAddPoint = useCallback(async (lat: number, lng: number) => {
    try {
      const data = await addPoint(lat, lng);
      
      const protectionLevel = data.protection_level || "low";
      const zoneName = data.zone_name || "منطقة غير محمية";
      
      // Set reserve info for the card
      setReserveInfo({
        name: zoneName,
        protectionLevel: protectionLevel,
        isInside: data.inside,
      });

      if (data.inside) {
        const levelText = protectionLevel === "high" ? "عالي" : protectionLevel === "medium" ? "متوسط" : "منخفض";
        setStatusBar({
          status: "success",
          message: `🟢 داخل ${zoneName} — مستوى الحماية: ${levelText}`,
        });
      } else {
        setStatusBar({
          status: "danger",
          message: "🔴 خارج نطاق محمي",
        });
      }
    } catch (error) {
      console.error("Add point API error:", error);
      setStatusBar({
        status: "danger",
        message: "❌ فشل إضافة النقطة. تأكدي أن السيرفر شغال.",
      });
    }
  }, []);

  return (
    <AnimatePresence mode="wait">
      {showSplash ? (
        <SplashScreen key="splash" onFinish={handleSplashFinish} />
      ) : (
        <div className="app-layout" key="main">
          {/* Left Side - Map (Fixed) */}
          <MapSection onAddPoint={handleAddPoint} reserveInfo={reserveInfo} />

          {/* Right Side - Controls */}
          <ControlPanel
            mode={mode}
            onModeChange={setMode}
            response={response}
            status={status}
            ttsEnabled={ttsEnabled}
            isProcessing={isProcessing}
            onMicClick={handleMicClick}
            onSendText={handleSendText}
            onImageUpload={handleImageUpload}
            onEnableTTS={handleEnableTTS}
            onStopTTS={handleStopTTS}
            reserveInfo={reserveInfo}
            userId={userId}
            onLogout={handleLogout}
          />

          {/* Status Footer */}
          <StatusFooter status={statusBar.status} message={statusBar.message} />
        </div>
      )}
    </AnimatePresence>
  );
};

export default Index;