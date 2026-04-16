import { AuthForm } from "@/components/auth/AuthForm";
import { AppShell } from "@/components/layout/AppShell";
import { PageTransition } from "@/components/motion/PageTransition";

export default function LoginPage() {
  return (
    <AppShell className="flex items-center">
      <PageTransition>
        <AuthForm />
      </PageTransition>
    </AppShell>
  );
}
