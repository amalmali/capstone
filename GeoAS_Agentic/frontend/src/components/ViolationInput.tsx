import { Camera, Search, ImageIcon } from "lucide-react";
import { useState, useRef } from "react";

interface ViolationInputProps {
  onImageUpload: (file: File) => void;
  isProcessing: boolean;
  response: string;
}

const ViolationInput = ({ onImageUpload, isProcessing, response }: ViolationInputProps) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = () => {
    const file = fileInputRef.current?.files?.[0];
    if (file) {
      onImageUpload(file);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs font-semibold text-foreground mb-2 block">
          ارفع صورة المخالفة
        </label>
        
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
        
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="upload-zone cursor-pointer"
        >
          {selectedImage ? (
            <div className="space-y-2 w-full">
              <img 
                src={selectedImage} 
                alt="معاينة الصورة" 
                className="max-h-40 mx-auto rounded-lg object-contain"
              />
              <p className="text-xs text-muted-foreground text-center truncate">
                {fileName}
              </p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 py-6">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <ImageIcon className="w-6 h-6 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground">اضغط لرفع صورة</p>
              <p className="text-xs text-muted-foreground/70">PNG, JPG, JPEG</p>
            </div>
          )}
        </div>
      </div>

      <button
        onClick={handleAnalyze}
        disabled={isProcessing || !selectedImage}
        className="btn-primary w-full"
      >
        <Search className="w-4 h-4" />
        <span>تحليل الصورة</span>
      </button>

      {response && (
        <div className="response-card mt-4">
          <div className="response-header">
            <Camera className="w-4 h-4 text-primary" />
            <span className="text-xs font-semibold">نتيجة التحليل</span>
          </div>
          <p className="text-sm text-foreground leading-relaxed">{response}</p>
        </div>
      )}
    </div>
  );
};

export default ViolationInput;
