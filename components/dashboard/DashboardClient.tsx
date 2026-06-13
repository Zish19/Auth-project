"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { normalizeApiError } from "@/lib/axios";
import { formatTimestamp } from "@/lib/utils";
import { authService } from "@/services/authService";
import type { SessionMeta } from "@/lib/types/auth";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";

export function DashboardClient() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [meta, setMeta] = useState<SessionMeta>({
    fetchedAt: new Date().toISOString(),
    status: "loading",
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    const getSession = async () => {
      try {
        const me = await authService.getCurrentUser();
        setUsername(me.username);
        setMeta({ fetchedAt: new Date().toISOString(), status: "authenticated" });
      } catch (loadError) {
        setMeta({ fetchedAt: new Date().toISOString(), status: "error" });
        setError(normalizeApiError(loadError));
        router.replace("/login");
      }
    };

    void getSession();
  }, [router]);

  const sessionState = useMemo(() => {
    if (meta.status === "loading") {
      return "syncing";
    }

    if (meta.status === "error") {
      return "unauthorized";
    }

    return "active";
  }, [meta.status]);

  const onLogout = async () => {
    setIsLoggingOut(true);
    try {
      await authService.logout();
      router.replace("/login");
    } catch (logoutError) {
      setError(normalizeApiError(logoutError));
    } finally {
      setIsLoggingOut(false);
    }
  };

  if (meta.status === "loading") {
    return (
      <div className="grid gap-4 md:grid-cols-3">
        <Skeleton className="h-36" />
        <Skeleton className="h-36" />
        <Skeleton className="h-36" />
      </div>
    );
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      <header className="space-y-2">
        <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">Session panel</p>
        <h1 className="font-heading text-4xl text-paper">Dashboard</h1>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Username</p>
          <p className="mt-4 text-2xl text-paper">{username}</p>
        </Card>
        <Card>
          <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Session status</p>
          <p className="mt-4 text-2xl capitalize text-emerald-300">{sessionState}</p>
        </Card>
        <Card>
          <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">Fetched at</p>
          <p className="mt-4 text-lg text-paper">{formatTimestamp(meta.fetchedAt)}</p>
        </Card>
      </div>

      {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      <Button className="max-w-48" onClick={onLogout} loading={isLoggingOut}>
        Logout
      </Button>
    </motion.section>
  );
}
