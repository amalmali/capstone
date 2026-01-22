import { motion } from "framer-motion";
import { MessageCircle, AlertCircle } from "lucide-react";

interface ResponseCardProps {
  response: string;
  status?: string;
}

const ResponseCard = ({ response, status }: ResponseCardProps) => {
  return (
    <motion.div
      className="response-card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-primary/10 shrink-0">
          <MessageCircle className="w-5 h-5 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-bold text-primary mb-2">الرد:</p>
          <p className="text-foreground leading-relaxed">{response}</p>
          {status && (
            <div className="flex items-center gap-2 mt-3 text-muted-foreground text-sm">
              <AlertCircle className="w-4 h-4" />
              <span>{status}</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ResponseCard;
