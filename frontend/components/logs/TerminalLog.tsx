"use client";

import { AnimatePresence, motion } from "framer-motion";

export interface TerminalLogItem {
  id: string;
  message: string;
  tone?: "info" | "success" | "error";
}

interface TerminalLogProps {
  title?: string;
  logs: TerminalLogItem[];
}

const toneClasses: Record<NonNullable<TerminalLogItem["tone"]>, string> = {
  info: "text-zinc-300",
  success: "text-emerald-300",
  error: "text-rose-300",
};

export function TerminalLog({ title = "Execution stream", logs }: TerminalLogProps) {
  return (
    <section
      className="rounded-2xl border border-white/10 bg-black/50 p-4 font-mono text-xs"
      aria-live="polite"
      aria-label={title}
    >
      <p className="mb-3 text-[11px] uppercase tracking-[0.2em] text-zinc-500">{title}</p>
      <div className="space-y-2">
        <AnimatePresence initial={false}>
          {logs.map((log) => (
            <motion.p
              key={log.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 8 }}
              transition={{ duration: 0.2 }}
              className={toneClasses[log.tone ?? "info"]}
            >
              <span className="text-accent">$</span> {log.message}
            </motion.p>
          ))}
        </AnimatePresence>
      </div>
    </section>
  );
}
