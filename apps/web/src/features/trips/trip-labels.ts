import type { SupportedLocale } from "../../shared/lib/locale";

export const TRIP_STATUS_LABELS: Record<
  SupportedLocale,
  Record<string, string>
> = {
  en: {
    draft: "Draft",
    active: "Active",
    completed: "Completed",
    abandoned: "Cancelled",
  },
  ru: {
    draft: "Черновик",
    active: "Активна",
    completed: "Завершена",
    abandoned: "Отменена",
  },
  es: {
    draft: "Borrador",
    active: "Activo",
    completed: "Completado",
    abandoned: "Cancelado",
  },
};

export const WAYPOINT_KIND_LABELS: Record<
  SupportedLocale,
  Record<string, string>
> = {
  en: {
    transit: "Transit",
    destination: "Destination",
    stopover: "Stopover",
  },
  ru: {
    transit: "Транзит",
    destination: "Назначение",
    stopover: "Остановка",
  },
  es: {
    transit: "Tránsito",
    destination: "Destino",
    stopover: "Escala",
  },
};
