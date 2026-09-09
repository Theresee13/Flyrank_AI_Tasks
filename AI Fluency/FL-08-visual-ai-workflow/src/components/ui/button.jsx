import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const variants = cva("inline-flex h-9 items-center justify-center gap-2 rounded-md px-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 disabled:pointer-events-none disabled:opacity-50", {
  variants: {
    variant: {
      default: "bg-cyan-400 text-slate-950 hover:bg-cyan-300",
      outline: "border border-slate-700 bg-slate-900 text-slate-100 hover:bg-slate-800",
      ghost: "text-slate-300 hover:bg-slate-800",
      danger: "bg-rose-500 text-white hover:bg-rose-400",
    },
  },
  defaultVariants: { variant: "default" },
});

export function Button({ className, variant, ...props }) {
  return <button className={cn(variants({ variant }), className)} {...props} />;
}
