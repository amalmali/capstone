import { useState } from "react";
import { motion } from "framer-motion";
import { LogIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SplashScreenProps {
  onFinish: (userId: string) => void;
}

const SplashScreen = ({ onFinish }: SplashScreenProps) => {
  const [inputId, setInputId] = useState("");
  const [showLogin, setShowLogin] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputId.trim()) {
      onFinish(inputId.trim());
    }
  };

  const handleClick = () => {
    if (!showLogin) {
      setShowLogin(true);
    }
  };

  return (
    <motion.div
      className="splash-screen cursor-pointer"
      onClick={handleClick}
      initial={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Main Title - عون */}
        <motion.h1 className="text-7xl md:text-9xl font-black text-white mb-4">
           عون
        </motion.h1>

      {/* Subtitle - نظام المساعدة المكانية */}
        <motion.p className="text-2xl md:text-3xl font-bold text-white/90">
           نظام المساعدة المكانية
        </motion.p>

      {/* Subtitle */}
      <motion.p
        className="splash-subtitle"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.5 }}
      >
        Geospatial Assistance System
      </motion.p>

      {/* Login Form or Hint */}
      {showLogin ? (
        <motion.form
          onSubmit={handleSubmit}
          onClick={(e) => e.stopPropagation()}
          className="mt-12 flex flex-col items-center gap-4 w-full max-w-sm px-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="flex items-center gap-2 text-white/80 mb-2">
            <LogIn className="w-5 h-5" />
            <span className="text-sm">أدخل رقم المعرف للدخول</span>
          </div>
          
          <Input
            type="text"
            placeholder="رقم المعرف (ID)"
            value={inputId}
            onChange={(e) => setInputId(e.target.value)}
            className="bg-white/10 border-white/20 text-white placeholder:text-white/50 text-center text-lg h-12"
            dir="rtl"
            autoFocus
          />
          
          <Button 
            type="submit" 
            disabled={!inputId.trim()}
            className="w-full h-12 bg-white text-primary hover:bg-white/90 font-medium text-base"
          >
            دخول
          </Button>
        </motion.form>
      ) : (
        <motion.p
          className="splash-hint"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.5 }}
        >
          اضغط للمتابعة
        </motion.p>
      )}
    </motion.div>
  );
};

export default SplashScreen;
