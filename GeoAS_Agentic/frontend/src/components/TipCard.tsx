import { motion } from "framer-motion";
import { Lightbulb } from "lucide-react";

const TipCard = () => {
  return (
    <motion.div
      className="max-w-5xl mx-auto mt-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.6 }}
    >
      <div className="response-card flex items-start gap-3">
        <div className="p-2 rounded-lg bg-accent/10 shrink-0">
          <Lightbulb className="w-5 h-5 text-accent" />
        </div>
        <p className="hint-text">
          <strong className="text-accent">نصيحة:</strong> إذا ما نطق الصوت أول مرة، اضغطي{" "}
          <strong> تفعيل الصوت</strong> مرة واحدة.
        </p>
      </div>
    </motion.div>
  );
};

export default TipCard;
