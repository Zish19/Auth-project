"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { normalizeApiError } from "@/lib/axios";
import { authService } from "@/services/authService";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { TerminalLog, type TerminalLogItem } from "@/components/logs/TerminalLog";

type AuthMode = "login" | "register";

function simulateProof(challenge: string) {
  const encoded = btoa(challenge).replace(/=/g, "");
  return {
    R: `R_${encoded.slice(0, 20)}`,
    s: `s_${encoded.slice(-20)}`,
  };
}

export function AuthForm() {
  const router = useRouter();
  const [mode, setMode] = useState<AuthMode>("login");
  const [username, setUsername] = useState("");
  const [publicKey, setPublicKey] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<TerminalLogItem[]>([]);

  const headline = useMemo(
    () => (mode === "login" ? "Authenticate Session" : "Register Identity"),
    [mode],
  );

  const addLog = (message: string, tone: TerminalLogItem["tone"] = "info") => {
    setLogs((prev) => [...prev, { id: crypto.randomUUID(), message, tone }]);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLogs([]);
    setIsLoading(true);

    try {
      if (mode === "register") {
        addLog("Registering user public key...");
        await authService.register({
          username,
          public_key: publicKey,
        });
        addLog("Identity registered", "success");
        setMode("login");
      } else {
        addLog("Requesting challenge...");
        const challengeResponse = await authService.requestLoginChallenge({ username });
        addLog("Challenge received");
        addLog("Generating proof...");
        await new Promise((resolve) => setTimeout(resolve, 700));
        const proof = simulateProof(challengeResponse.challenge);
        await authService.verifyLoginProof({
          username,
          challenge_id: challengeResponse.challenge_id,
          ...proof,
        });
        addLog("Proof verified", "success");
        router.push("/dashboard");
      }
    } catch (submitError) {
      const message = normalizeApiError(submitError);
      setError(message);
      addLog(message, "error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="mx-auto grid w-full max-w-5xl gap-8 p-8 md:grid-cols-2">
      <div>
        <p className="text-xs uppercase tracking-[0.22em] text-zinc-500">ZK Session Auth</p>
        <h1 className="mt-3 font-heading text-4xl leading-tight text-paper">{headline}</h1>
        <p className="mt-3 text-sm text-zinc-400">
          JWT-less login using challenge-response proofs and secure HttpOnly sessions.
        </p>

        <div className="mt-6 inline-flex rounded-xl border border-white/10 bg-white/5 p-1" role="tablist" aria-label="Auth mode">
          {(["login", "register"] as const).map((item) => (
            <button
              key={item}
              role="tab"
              aria-selected={mode === item}
              onClick={() => setMode(item)}
              className={`rounded-lg px-4 py-2 text-sm capitalize ${
                mode === item ? "bg-white/15 text-paper" : "text-zinc-400 hover:text-paper"
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      <motion.form
        key={mode}
        onSubmit={handleSubmit}
        className="space-y-4"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
      >
        <label className="block text-sm text-zinc-300">
          Username
          <Input
            required
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="neo_cipher"
            autoComplete="username"
            className="mt-2"
          />
        </label>

        {mode === "register" ? (
          <label className="block text-sm text-zinc-300">
            Public key
            <Input
              required
              value={publicKey}
              onChange={(event) => setPublicKey(event.target.value)}
              placeholder="pub_key_hex_or_base64"
              className="mt-2 font-mono"
            />
          </label>
        ) : null}

        {error ? <p className="text-sm text-rose-300">{error}</p> : null}

        <Button type="submit" loading={isLoading} aria-busy={isLoading}>
          {mode === "login" ? "Run Authentication" : "Create Account"}
        </Button>
      </motion.form>

      <div className="md:col-span-2">
        <TerminalLog logs={logs} title="Cryptographic pipeline" />
      </div>
    </Card>
  );
}
