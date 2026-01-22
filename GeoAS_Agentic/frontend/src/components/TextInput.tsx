import { Send } from "lucide-react";
import { useState } from "react";

interface TextInputProps {
  onSend: (query: string) => void;
  isProcessing: boolean;
}

const TextInput = ({ onSend, isProcessing }: TextInputProps) => {
  const [query, setQuery] = useState("");

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

  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-semibold text-foreground mb-2 block">
          اكتب سؤالك
        </label>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="مثال: هل هذه النقطة داخل محمية؟"
          className="input-modern"
          disabled={isProcessing}
        />
      </div>

      <button
        onClick={handleSend}
        disabled={isProcessing || !query.trim()}
        className="btn-primary w-full"
      >
        <Send className="w-4 h-4" />
        <span>إرسال</span>
      </button>
    </div>
  );
};

export default TextInput;