"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
}

export function Button({ className, children, loading, disabled, ...props }: ButtonProps) {
  // Destructure out the React animation event handlers that conflict with
  // Framer Motion's own onAnimationStart / onAnimationEnd prop types.
  const {
    onAnimationStart: _onAnimationStart,
    onAnimationEnd: _onAnimationEnd,
    onDragStart: _onDragStart,
    onDragEnd: _onDragEnd,
    onDrag: _onDrag,
    ...safeProps
  } = props as ButtonHTMLAttributes<HTMLButtonElement> & Record<string, unknown>;

  return (
    <motion.button
      whileTap={{ scale: 0.97, opacity: 0.85 }}
      transition={{ duration: 0.12 }}
      className={cn(
        "inline-flex w-full items-center justify-center rounded-xl border border-white/20 bg-white/10 px-4 py-2.5 text-sm font-medium text-paper shadow-glow backdrop-blur-md",
        "hover:bg-white/15 focus:outline-none disabled:cursor-not-allowed disabled:opacity-60",
        className,
      )}
      disabled={loading || disabled}
      {...(safeProps as object)}
    >
      {loading ? "Processing..." : children}
    </motion.button>
  );
}
