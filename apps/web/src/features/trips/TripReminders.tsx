"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { format } from "date-fns";
import { enUS, es, ru } from "date-fns/locale";
import { useTranslations } from "next-intl";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Badge,
  Button,
  Field,
  FieldError,
  toast,
} from "@country-decision-atlas/ui";
import {
  useCancelReminderMutation,
  useCreateReminderMutation,
} from "../../entities/trips/api";
import type { TripReminder } from "../../shared/api/trips";
import { isApiError } from "../../shared/api/http";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";

const DATE_FNS_LOCALE: Record<SupportedLocale, typeof enUS> = {
  en: enUS,
  ru,
  es,
};

const REMINDER_STATUS_LABELS: Record<
  SupportedLocale,
  Record<string, string>
> = {
  en: { scheduled: "Scheduled", sent: "Sent", cancelled: "Cancelled" },
  ru: {
    scheduled: "Запланировано",
    sent: "Отправлено",
    cancelled: "Отменено",
  },
  es: {
    scheduled: "Programado",
    sent: "Enviado",
    cancelled: "Cancelado",
  },
};

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";

function CreateReminderForm({ tripId }: { tripId: string }) {
  const t = useTranslations("tripReminders");
  const createReminder = useCreateReminderMutation(tripId);
  const createReminderSchema = z.object({
    remindAt: z.string().min(1, t("dateTimeRequired")),
  });
  type CreateReminderValues = z.infer<typeof createReminderSchema>;
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateReminderValues>({
    resolver: zodResolver(createReminderSchema),
  });

  async function onSubmit(values: CreateReminderValues) {
    try {
      await createReminder.mutateAsync({
        remind_at: new Date(values.remindAt).toISOString(),
        channel: "telegram",
      });
      reset();
      toast.success(t("reminderCreated"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err)
          ? (err.error?.message ?? t("createError"))
          : t("createError"),
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
          type="datetime-local"
          className={inputClass}
          data-testid="reminder-datetime-input"
          {...register("remindAt")}
        />
        <FieldError>{errors.remindAt?.message}</FieldError>
      </Field>
      <Button
        type="submit"
        disabled={createReminder.isPending}
        data-testid="reminder-create-submit"
      >
        {t("addReminder")}
      </Button>
    </form>
  );
}

export function TripReminders({
  tripId,
  reminders,
}: {
  tripId: string;
  reminders: TripReminder[];
}) {
  const t = useTranslations("tripReminders");
  const locale = useAppLocale();
  const cancelReminder = useCancelReminderMutation(tripId);

  return (
    <div
      className="flex flex-col gap-4"
      data-testid="trip-reminders"
    >
      {reminders.length === 0 ? (
        <p className="text-c3 text-sm">{t("noReminders")}</p>
      ) : (
        <div>
          {reminders.map((reminder) => (
            <div
              key={reminder.id}
              className="border-warm flex items-center gap-3 border-b py-3 last:border-b-0"
              data-testid="reminder-item"
            >
              <span className="text-c2 flex-1 text-sm">
                {format(new Date(reminder.remind_at), "d MMMM yyyy, HH:mm", {
                  locale: DATE_FNS_LOCALE[locale],
                })}
                {reminder.checklist_item_title
                  ? ` · ${reminder.checklist_item_title}`
                  : ""}
              </span>
              <Badge variant="default">
                {REMINDER_STATUS_LABELS[locale][reminder.status] ??
                  reminder.status}
              </Badge>
              {reminder.status === "scheduled" && (
                <Button
                  variant="ghost"
                  onClick={() => cancelReminder.mutate(reminder.id)}
                  data-testid="reminder-cancel-button"
                >
                  {t("cancel")}
                </Button>
              )}
            </div>
          ))}
        </div>
      )}
      <CreateReminderForm tripId={tripId} />
    </div>
  );
}
