import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: ReactNode;
  className?: string;
}

export function AppShell({ children, className }: AppShellProps) {
  return (
    <main className={cn("relative z-10 mx-auto min-h-screen w-full max-w-6xl px-6 py-16", className)}>
      {children}
    </main>
  );
}
