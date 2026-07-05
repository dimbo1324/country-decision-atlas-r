import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/cn";

interface IconProps {
  icon: LucideIcon;
  size?: number;
  className?: string;
}

export function Icon({
  icon: LucideComponent,
  size = 16,
  className,
}: IconProps) {
  return (
    <LucideComponent
      width={size}
      height={size}
      strokeWidth={1.5}
      className={cn("shrink-0", className)}
    />
  );
}

export function IconFrame({
  icon,
  size = 16,
  className,
}: {
  icon: LucideIcon;
  size?: number;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "border-warm inline-flex h-9 w-9 items-center justify-center border transition-colors duration-300",
        className,
      )}
    >
      <Icon
        icon={icon}
        size={size}
      />
    </span>
  );
}
