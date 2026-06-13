import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // In production (Vercel), /api/backend/* is handled by the Python serverless
    // function via vercel.json rewrites — no rewrite needed from Next.js.
    if (process.env.NODE_ENV === "production") {
      return [];
    }

    // In local development, proxy to the FastAPI dev server.
    const backendOrigin =
      process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

    return [
      {
        source: "/api/backend/:path*",
        destination: `${backendOrigin}/:path*`,
      },
    ];
  },
};

export default nextConfig;
