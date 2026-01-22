import { motion } from "framer-motion";
import { MapPin, Globe } from "lucide-react";

const Header = () => {
  return (
    <motion.header 
      className="text-center py-8"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="flex items-center justify-center gap-3 mb-3">
        <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
          <Globe className="w-6 h-6 text-primary" />
        </div>
        <h1 className="text-3xl md:text-4xl font-extrabold bg-gradient-to-l from-primary via-primary to-success bg-clip-text text-transparent">
          Geospatial Assistance System
        </h1>
        <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
          <MapPin className="w-6 h-6 text-primary" />
        </div>
      </div>
      <p className="text-muted-foreground text-lg">
        اسألي كتابة أو صوت، والرد يرجع صوتيًا + خريطة المحميات
      </p>
    </motion.header>
  );
};

export default Header;
