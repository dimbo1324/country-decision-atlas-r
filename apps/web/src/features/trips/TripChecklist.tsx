"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button, Field, FieldError, toast } from "@country-decision-atlas/ui";
import {
  useCreateChecklistItemMutation,
  useDeleteChecklistItemMutation,
  useImportChecklistMutation,
  useUpdateChecklistItemMutation,
} from "../../entities/trips/api";
import type { TripChecklistItem } from "../../shared/api/trips";
import { isApiError } from "../../shared/api/http";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

function ChecklistItemRow({
  item,
  tripId,
}: {
  item: TripChecklistItem;
  tripId: string;
}) {
  const updateItem = useUpdateChecklistItemMutation(tripId);
  const deleteItem = useDeleteChecklistItemMutation(tripId);
  const done = item.status === "done";

  return (
    <div
      className="border-warm flex items-center gap-3 border-b py-3 last:border-b-0"
      data-testid="checklist-item"
    >
      <input
        type="checkbox"
        className="accent-gold"
        checked={done}
        onChange={(event) =>
          updateItem.mutate({
            itemId: item.id,
            payload: { status: event.target.checked ? "done" : "todo" },
          })
        }
        data-testid="checklist-item-checkbox"
      />
      <span
        className={
          done
            ? "text-c4 flex-1 text-sm line-through"
            : "text-c2 flex-1 text-sm"
        }
      >
        {item.title}
      </span>
      <Button
        variant="ghost"
        onClick={() => deleteItem.mutate(item.id)}
        data-testid="checklist-item-remove-button"
      >
        Удалить
      </Button>
    </div>
  );
}

const addChecklistItemSchema = z.object({
  title: z.string().min(1, "Введите название пункта"),
});
type AddChecklistItemValues = z.infer<typeof addChecklistItemSchema>;

function AddChecklistItemForm({ tripId }: { tripId: string }) {
  const createItem = useCreateChecklistItemMutation(tripId);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AddChecklistItemValues>({
    resolver: zodResolver(addChecklistItemSchema),
  });

  async function onSubmit(values: AddChecklistItemValues) {
    try {
      await createItem.mutateAsync({ title: values.title, status: "todo" });
      reset();
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось добавить пункт.")
          : "Не удалось добавить пункт.",
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex items-end gap-3"
      noValidate
    >
      <Field className="flex-1">
        <input
          type="text"
          placeholder="Новый пункт чек-листа"
          className={inputClass}
          data-testid="checklist-item-input"
          {...register("title")}
        />
        <FieldError>{errors.title?.message}</FieldError>
      </Field>
      <Button
        type="submit"
        disabled={createItem.isPending}
        data-testid="checklist-item-add-submit"
      >
        Добавить
      </Button>
    </form>
  );
}

const importChecklistSchema = z.object({
  routeId: z.string().min(1, "Введите ID маршрута легализации"),
});
type ImportChecklistValues = z.infer<typeof importChecklistSchema>;

function ImportChecklistForm({ tripId }: { tripId: string }) {
  const importChecklist = useImportChecklistMutation(tripId);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ImportChecklistValues>({
    resolver: zodResolver(importChecklistSchema),
  });

  async function onSubmit(values: ImportChecklistValues) {
    try {
      await importChecklist.mutateAsync(values.routeId);
      reset();
      toast.success("Шаблон чек-листа импортирован.");
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? "Не удалось импортировать шаблон.")
          : "Не удалось импортировать шаблон.",
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex items-end gap-3"
      noValidate
    >
      <Field className="flex-1">
        <input
          type="text"
          placeholder="ID маршрута легализации для импорта шаблона"
          className={inputClass}
          data-testid="checklist-import-route-id-input"
          {...register("routeId")}
        />
        <FieldError>{errors.routeId?.message}</FieldError>
      </Field>
      <Button
        type="submit"
        variant="ghost"
        disabled={importChecklist.isPending}
        data-testid="checklist-import-submit"
      >
        Импортировать
      </Button>
    </form>
  );
}

export function TripChecklist({
  tripId,
  items,
}: {
  tripId: string;
  items: TripChecklistItem[];
}) {
  return (
    <div
      className="flex flex-col gap-4"
      data-testid="trip-checklist"
    >
      {items.length === 0 ? (
        <p className="text-c3 text-sm">Чек-лист пуст.</p>
      ) : (
        <div>
          {items
            .slice()
            .sort((a, b) => a.position - b.position)
            .map((item) => (
              <ChecklistItemRow
                key={item.id}
                item={item}
                tripId={tripId}
              />
            ))}
        </div>
      )}
      <AddChecklistItemForm tripId={tripId} />
      <ImportChecklistForm tripId={tripId} />
    </div>
  );
}
