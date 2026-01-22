import { motion } from "framer-motion";
import { Send, Camera } from "lucide-react";
import { useState, useRef } from "react";

interface TextSectionProps {
  onSend: (query: string) => void;
  onImageUpload: (file: File) => void;
  isProcessing: boolean;
}

const TextSection = ({ onSend, onImageUpload, isProcessing }: TextSectionProps) => {
  const [query, setQuery] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (query.trim()) {
      onSend(query);
      setQuery("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImageUpload(file);
    }
  };

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="اكتبي سؤالك هنا..."
        className="input-field"
        disabled={isProcessing}
      />

      <div className="flex flex-wrap gap-3 items-center">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="btn-accent flex items-center gap-2"
          disabled={isProcessing}
        >
          <Camera className="w-4 h-4" />
          <span>تحليل الصورة</span>
        </button>
      </div>

      <button
        onClick={handleSend}
        disabled={isProcessing || !query.trim()}
        className="btn-primary-gradient flex items-center gap-2"
      >
        <Send className="w-4 h-4" />
        <span>إرسال</span>
      </button>
    </motion.div>
  );
};

export default TextSection;
