import { AppShell } from "@/components/layout/AppShell";
import { PageTransition } from "@/components/motion/PageTransition";
import { DashboardClient } from "@/components/dashboard/DashboardClient";

export default function DashboardPage() {
  return (
    <AppShell>
      <PageTransition>
        <DashboardClient />
      </PageTransition>
    </AppShell>
  );
}
