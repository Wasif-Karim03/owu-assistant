import Link from "next/link";
import { GraduationCap } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-owu-grey px-4">
      <div className="w-14 h-14 rounded-2xl bg-owu-red-muted flex items-center justify-center mb-6">
        <GraduationCap className="w-7 h-7 text-owu-red" />
      </div>

      <h1 className="font-heading text-3xl font-semibold text-owu-text mb-2">
        Page not found
      </h1>
      <p className="text-owu-text-muted mb-6">
        The page you&apos;re looking for doesn&apos;t exist.
      </p>

      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm font-medium text-white
                   bg-owu-red hover:bg-owu-red-light rounded-lg px-5 py-2.5
                   transition-colors"
      >
        Go back to the assistant
      </Link>
    </div>
  );
}
