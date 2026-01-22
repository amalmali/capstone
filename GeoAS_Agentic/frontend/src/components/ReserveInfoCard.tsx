import { motion, AnimatePresence } from "framer-motion";
import { Shield, MapPin, AlertTriangle, CheckCircle } from "lucide-react";

interface ReserveInfo {
  name: string;
  protectionLevel: "high" | "medium" | "low";
  isInside: boolean;
}

interface ReserveInfoCardProps {
  info: ReserveInfo | null;
}

const ReserveInfoCard = ({ info }: ReserveInfoCardProps) => {
  if (!info) return null;

  const levelConfig = {
    high: {
      label: "عالي",
      color: "bg-destructive/10 text-destructive border-destructive/30",
      icon: AlertTriangle,
    },
    medium: {
      label: "متوسط",
      color: "bg-amber-500/10 text-amber-600 border-amber-500/30",
      icon: Shield,
    },
    low: {
      label: "منخفض",
      color: "bg-success/10 text-success border-success/30",
      icon: CheckCircle,
    },
  };

  const level = levelConfig[info.protectionLevel];
  const LevelIcon = level.icon;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -10, scale: 0.95 }}
        transition={{ type: "spring", stiffness: 300, damping: 25 }}
        className={`panel-card border-2 ${info.isInside ? "border-success/40 bg-success/5" : "border-destructive/40 bg-destructive/5"}`}
      >
        <div className="flex items-start gap-4">
          {/* Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1, type: "spring", stiffness: 400 }}
            className={`w-12 h-12 rounded-xl flex items-center justify-center ${info.isInside ? "bg-success/20" : "bg-destructive/20"}`}
          >
            {info.isInside ? (
              <CheckCircle className="w-6 h-6 text-success" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-destructive" />
            )}
          </motion.div>

          {/* Content */}
          <div className="flex-1">
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 }}
              className="flex items-center gap-2 mb-1"
            >
              <MapPin className="w-4 h-4 text-primary" />
              <span className="text-xs text-muted-foreground">
                {info.isInside ? "داخل المحمية" : "خارج المحمية"}
              </span>
            </motion.div>

            <motion.h3
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="text-lg font-bold text-foreground mb-2"
            >
              {info.name}
            </motion.h3>

                        {info.isInside && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.25 }}
                className="flex items-center gap-2"
              >
                <span className="text-xs text-muted-foreground">مستوى الحماية:</span>
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${level.color}`}>
                  <LevelIcon className="w-3.5 h-3.5" />
                  {level.label}
                </span>
              </motion.div>
            )}

          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ReserveInfoCard;
