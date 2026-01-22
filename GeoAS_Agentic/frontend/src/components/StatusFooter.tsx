import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, Info } from "lucide-react";
interface StatusFooterProps {
  status: "success" | "danger" | "neutral";
  message: string;
}
const StatusFooter = ({
  status,
  message
}: StatusFooterProps) => {
  const Icon = status === "success" ? CheckCircle2 : status === "danger" ? XCircle : Info;
  return <AnimatePresence>
      
    </AnimatePresence>;
};
export default StatusFooter;