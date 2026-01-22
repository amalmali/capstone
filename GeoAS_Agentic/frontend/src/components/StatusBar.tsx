import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, Info } from "lucide-react";

interface StatusBarProps {
  status: "success" | "danger" | "neutral";
  message: string;
}

const StatusBar = ({ status, message }: StatusBarProps) => {
  const Icon = status === "success" ? CheckCircle2 : status === "danger" ? XCircle : Info;

  return (
    <AnimatePresence>
      <motion.div
        className={`status-bar ${status}`}
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        exit={{ y: 100 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-center gap-3">
          <Icon className="w-5 h-5" />
          <span>{message}</span>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default StatusBar;
