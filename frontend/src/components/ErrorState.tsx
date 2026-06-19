import { AlertCircle } from "lucide-react";

interface ErrorStateProps {
  heading: string;
  description: string;
  onRetry: () => void;
}

export function ErrorState({ heading, description, onRetry }: ErrorStateProps) {
  return (
    <div className="error-state">
      <AlertCircle size={48} className="error-state-icon" />
      <h3 className="error-state-heading">{heading}</h3>
      <p className="error-state-description">{description}</p>
      <button className="btn btn-primary" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
}
