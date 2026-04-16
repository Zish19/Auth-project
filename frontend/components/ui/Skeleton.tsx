import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-xl bg-gradient-to-r from-zinc-800/70 via-zinc-700/30 to-zinc-800/70",
        className,
      )}
      aria-hidden="true"
    />
  );
}
