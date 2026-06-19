interface SkeletonProps {
  variant: "text" | "card" | "table-row" | "chart";
  count?: number;
  columns?: number;
}

export function SkeletonLoader({ variant, count = 1, columns = 4 }: SkeletonProps) {
  if (variant === "table-row") {
    return (
      <div className="skeleton-table">
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="skeleton-row">
            {Array.from({ length: columns }).map((_, j) => (
              <div key={j} className="skeleton-cell skeleton-pulse" />
            ))}
          </div>
        ))}
      </div>
    );
  }

  if (variant === "card") {
    return (
      <div className="skeleton-grid">
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="skeleton-card skeleton-pulse" />
        ))}
      </div>
    );
  }

  if (variant === "chart") {
    return <div className="skeleton-chart skeleton-pulse" />;
  }

  return (
    <div className="skeleton-text-group">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-text skeleton-pulse" style={{ width: `${60 + Math.random() * 30}%` }} />
      ))}
    </div>
  );
}
