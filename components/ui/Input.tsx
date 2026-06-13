import { cn } from "@/lib/utils";
import type { InputHTMLAttributes } from "react";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-11 w-full rounded-xl border border-white/15 bg-black/40 px-3 text-sm text-paper placeholder:text-zinc-500",
        "focus:border-accent focus:outline-none",
        className,
      )}
      {...props}
    />
  );
}
