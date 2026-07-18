import type { ComponentPropsWithoutRef } from "react";
import { cn } from "../lib/cn";

/** The card-grid pattern shared by every "my things" list (trips,
 * watchlist, subscriptions): a responsive 1/2/3-column grid of cards.
 * Forwards `data-testid` and the rest of `<div>`'s props directly, since
 * each caller needs its own testid on the grid container. */
export function BoardGrid({
  className,
  ...rest
}: ComponentPropsWithoutRef<"div">) {
  return (
    <div
      className={cn("grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3", className)}
      {...rest}
    />
  );
}
