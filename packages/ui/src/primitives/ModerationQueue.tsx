"use client";

import { useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";
import { toast } from "sonner";
import { cn } from "../lib/cn";
import { Button } from "./Button";
import { Dialog, DialogContent } from "./Dialog";
import { Drawer } from "./Drawer";

export interface ModerationQueueAction<T> {
  key: string;
  label: string;
  variant?: "default" | "dangerous";
  /** Only offered when this returns true (or is omitted). */
  isVisible?: (row: T) => boolean;
  /** Shows a reason textarea in the confirm dialog and passes its value. */
  requiresReason?: boolean;
  onRun: (row: T, reason?: string) => Promise<unknown>;
  successMessage?: (row: T) => string;
  errorMessage?: (row: T, error: unknown) => string;
}

interface ModerationQueueProps<T> {
  testId: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  columns: ColumnDef<T, any>[];
  data: T[];
  getRowId: (row: T) => string;
  actions: ModerationQueueAction<T>[];
  renderDetail?: (row: T) => React.ReactNode;
  detailTitle?: (row: T) => React.ReactNode;
  emptyMessage?: string;
}

function extractErrorMessage(error: unknown, fallback: string): string {
  if (
    error &&
    typeof error === "object" &&
    "error" in error &&
    error.error &&
    typeof error.error === "object" &&
    "message" in error.error &&
    typeof (error.error as { message?: unknown }).message === "string"
  ) {
    return (error.error as { message: string }).message;
  }
  return fallback;
}

export function ModerationQueue<T>({
  testId,
  columns,
  data,
  getRowId,
  actions,
  renderDetail,
  detailTitle,
  emptyMessage = "Очередь пуста.",
}: ModerationQueueProps<T>) {
  const [detailRow, setDetailRow] = useState<T | null>(null);
  const [confirmState, setConfirmState] = useState<{
    row: T;
    action: ModerationQueueAction<T>;
  } | null>(null);
  const [reason, setReason] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  const table = useReactTable({
    data,
    columns,
    getRowId,
    getCoreRowModel: getCoreRowModel(),
  });

  async function runAction(
    row: T,
    action: ModerationQueueAction<T>,
    reasonValue?: string,
  ) {
    setIsRunning(true);
    try {
      await action.onRun(row, reasonValue);
      toast.success(action.successMessage?.(row) ?? `${action.label}: готово.`);
      setConfirmState(null);
      setReason("");
    } catch (error: unknown) {
      toast.error(
        action.errorMessage?.(row, error) ??
          extractErrorMessage(error, "Действие не выполнено."),
      );
    } finally {
      setIsRunning(false);
    }
  }

  function handleActionClick(row: T, action: ModerationQueueAction<T>) {
    if (action.variant === "dangerous" || action.requiresReason) {
      setConfirmState({ row, action });
      return;
    }
    void runAction(row, action);
  }

  return (
    <div
      className="flex flex-col gap-3"
      data-testid={testId}
    >
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr
                key={headerGroup.id}
                className="border-warm border-b"
              >
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="font-mono text-c4 px-3 py-2.5 text-left text-[8px] font-normal tracking-[0.2em] uppercase"
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </th>
                ))}
                {actions.length > 0 && (
                  <th className="font-mono text-c4 px-3 py-2.5 text-right text-[8px] font-normal tracking-[0.2em] uppercase">
                    Действия
                  </th>
                )}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + (actions.length > 0 ? 1 : 0)}
                  className="text-c4 px-3 py-6 text-center text-sm"
                  data-testid={`${testId}-empty`}
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row) => {
                const rowActions = actions.filter(
                  (action) => action.isVisible?.(row.original) ?? true,
                );
                const openDetail = () =>
                  renderDetail && setDetailRow(row.original);
                return (
                  <tr
                    key={row.id}
                    className={cn(
                      "border-warm hover:bg-bg3/60 border-b transition-colors duration-200",
                      renderDetail && "cursor-pointer",
                    )}
                    data-testid={`${testId}-row`}
                    {...(renderDetail
                      ? {
                          tabIndex: 0,
                          "aria-label": detailTitle
                            ? `Открыть детали: ${detailTitle(row.original)}`
                            : "Открыть детали",
                          // Not role="button" -- the row also contains real
                          // <button> action elements, and ARIA disallows
                          // interactive content inside a button-role
                          // element. Ignore keydowns that bubble up from
                          // those nested buttons so pressing Enter/Space on
                          // an action doesn't also open the detail drawer.
                          onKeyDown: (event: React.KeyboardEvent) => {
                            if (event.key !== "Enter" && event.key !== " ") {
                              return;
                            }
                            const target = event.target as HTMLElement;
                            if (target.closest("button, a")) {
                              return;
                            }
                            event.preventDefault();
                            openDetail();
                          },
                        }
                      : {})}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className="text-c2 px-3 py-3 text-sm"
                        onClick={openDetail}
                      >
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext(),
                        )}
                      </td>
                    ))}
                    {rowActions.length > 0 && (
                      <td className="px-3 py-3 text-right">
                        <div className="flex flex-wrap justify-end gap-2">
                          {rowActions.map((action) => (
                            <Button
                              key={action.key}
                              type="button"
                              variant={
                                action.variant === "dangerous"
                                  ? "ghost"
                                  : "ghost"
                              }
                              className={cn(
                                action.variant === "dangerous" &&
                                  "text-terra3 border-terra2/60",
                              )}
                              disabled={isRunning}
                              onClick={() =>
                                handleActionClick(row.original, action)
                              }
                              data-testid={`${testId}-action-${action.key}`}
                            >
                              {action.label}
                            </Button>
                          ))}
                        </div>
                      </td>
                    )}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {renderDetail && (
        <Drawer
          open={detailRow !== null}
          onClose={() => setDetailRow(null)}
          title={detailRow && detailTitle ? detailTitle(detailRow) : "Детали"}
        >
          {detailRow && renderDetail(detailRow)}
        </Drawer>
      )}

      <Dialog
        open={confirmState !== null}
        onOpenChange={(open) => {
          if (!open) {
            setConfirmState(null);
            setReason("");
          }
        }}
      >
        {confirmState && (
          <DialogContent
            title={confirmState.action.label}
            description="Подтвердите действие."
          >
            <div className="flex flex-col gap-4">
              {confirmState.action.requiresReason && (
                <textarea
                  className="border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200"
                  rows={3}
                  placeholder="Причина (обязательно)"
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  data-testid={`${testId}-confirm-reason`}
                />
              )}
              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    setConfirmState(null);
                    setReason("");
                  }}
                >
                  Отмена
                </Button>
                <Button
                  type="button"
                  disabled={
                    isRunning ||
                    (confirmState.action.requiresReason &&
                      reason.trim().length === 0)
                  }
                  onClick={() =>
                    void runAction(
                      confirmState.row,
                      confirmState.action,
                      confirmState.action.requiresReason ? reason : undefined,
                    )
                  }
                  data-testid={`${testId}-confirm-submit`}
                >
                  Подтвердить
                </Button>
              </div>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  );
}
