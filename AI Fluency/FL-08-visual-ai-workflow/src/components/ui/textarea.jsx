import { cn } from "@/lib/utils";

export function Textarea({ className, ...props }) {
  return <textarea className={cn("min-h-24 w-full rounded-md border border-slate-700 bg-slate-950 p-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-400", className)} {...props} />;
}
