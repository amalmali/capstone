import { MessageCircle, AlertCircle } from "lucide-react";

interface ResponseBoxProps {
  response: string;
  status?: string;
}

const ResponseBox = ({ response, status }: ResponseBoxProps) => {
  return (
    <div className="response-box">
      <div className="response-label">
        <MessageCircle className="w-3.5 h-3.5" />
        <span>الرد</span>
      </div>
      <p className="response-text">{response}</p>
      {status && (
        <div className="flex items-center gap-1.5 mt-3 text-xs text-muted-foreground">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>{status}</span>
        </div>
      )}
    </div>
  );
};

export default ResponseBox;