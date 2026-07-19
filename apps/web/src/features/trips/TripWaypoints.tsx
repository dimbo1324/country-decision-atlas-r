"use client";

import { useEffect, useState } from "react";
import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical } from "lucide-react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
import { useTranslations } from "next-intl";
import { useForm } from "react-hook-form";
import { z } from "zod";
import {
  Badge,
  Button,
  Field,
  FieldError,
  FieldLabel,
  toast,
} from "@country-decision-atlas/ui";
import { allCountriesQuery } from "../../entities/decision/api";
import {
  useCreateWaypointMutation,
  useDeleteWaypointMutation,
  useReorderWaypointsMutation,
} from "../../entities/trips/api";
import type { TripWaypoint } from "../../shared/api/trips";
import { isApiError } from "../../shared/api/http";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { toApiLocale } from "../../shared/lib/locale";
import { WAYPOINT_KIND_LABELS } from "./trip-labels";

const inputClass =
  "border-warm bg-bg2 text-c1 font-body border px-4 py-2.5 text-sm outline-none focus-visible:border-gold transition-colors duration-200";
const selectClass =
  "border-warm bg-bg2 text-c2 focus-visible:border-gold w-full border px-3 py-2 text-sm outline-none";

function SortableWaypointRow({
  waypoint,
  onDelete,
  isDeleting,
}: {
  waypoint: TripWaypoint;
  onDelete: () => void;
  isDeleting: boolean;
}) {
  const t = useTranslations("tripWaypoints");
  const locale = useAppLocale();
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: waypoint.id });

  return (
    <div
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className="border-warm bg-bg2 flex items-center gap-3 border p-3"
      data-testid="waypoint-row"
    >
      <button
        type="button"
        aria-label={t("dragToReorder")}
        className="text-c4 hover:text-c1 cursor-grab touch-none"
        data-testid="waypoint-drag-handle"
        {...attributes}
        {...listeners}
      >
        <GripVertical
          width={16}
          height={16}
          strokeWidth={1.5}
        />
      </button>
      <div className="flex flex-1 flex-col gap-1">
        <span className="text-c1 text-sm font-semibold">
          {waypoint.country.name}
          {waypoint.city ? ` · ${waypoint.city}` : ""}
        </span>
        <Badge variant="default">
          {WAYPOINT_KIND_LABELS[locale][waypoint.kind] ?? waypoint.kind}
        </Badge>
      </div>
      <Button
        variant="ghost"
        onClick={onDelete}
        disabled={isDeleting}
        data-testid="waypoint-remove-button"
      >
        {t("remove")}
      </Button>
    </div>
  );
}

function AddWaypointForm({ tripId }: { tripId: string }) {
  const t = useTranslations("tripWaypoints");
  const locale = useAppLocale();
  const countries = useQuery(allCountriesQuery(toApiLocale(locale)));
  const createWaypoint = useCreateWaypointMutation(tripId);
  const addWaypointSchema = z.object({
    countrySlug: z.string().min(1, t("countryRequired")),
    city: z.string().optional(),
    kind: z.enum(["transit", "destination", "stopover"]),
  });
  type AddWaypointValues = z.infer<typeof addWaypointSchema>;
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<AddWaypointValues>({
    resolver: zodResolver(addWaypointSchema),
    defaultValues: { kind: "destination" },
  });

  async function onSubmit(values: AddWaypointValues) {
    try {
      await createWaypoint.mutateAsync({
        country_slug: values.countrySlug,
        city: values.city || null,
        kind: values.kind,
      });
      reset({ countrySlug: "", city: "", kind: "destination" });
      toast.success(t("waypointAdded"));
    } catch (err: unknown) {
      toast.error(
        isApiError(err) ? (err.error?.message ?? t("addError")) : t("addError"),
      );
    }
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="grid grid-cols-1 gap-4 sm:grid-cols-[2fr_1fr_1fr_auto] sm:items-end"
      noValidate
    >
      <Field>
        <FieldLabel htmlFor="waypoint-country">{t("country")}</FieldLabel>
        <select
          id="waypoint-country"
          className={selectClass}
          data-testid="waypoint-country-select"
          {...register("countrySlug")}
        >
          <option value="">{t("selectCountry")}</option>
          {countries.data?.items.map((c) => (
            <option
              key={c.slug}
              value={c.slug}
            >
              {c.name}
            </option>
          ))}
        </select>
        <FieldError>{errors.countrySlug?.message}</FieldError>
      </Field>
      <Field>
        <FieldLabel htmlFor="waypoint-city">{t("city")}</FieldLabel>
        <input
          id="waypoint-city"
          type="text"
          className={inputClass}
          {...register("city")}
        />
      </Field>
      <Field>
        <FieldLabel htmlFor="waypoint-kind">{t("kind")}</FieldLabel>
        <select
          id="waypoint-kind"
          className={selectClass}
          {...register("kind")}
        >
          <option value="destination">
            {WAYPOINT_KIND_LABELS[locale].destination}
          </option>
          <option value="transit">
            {WAYPOINT_KIND_LABELS[locale].transit}
          </option>
          <option value="stopover">
            {WAYPOINT_KIND_LABELS[locale].stopover}
          </option>
        </select>
      </Field>
      <Button
        type="submit"
        disabled={createWaypoint.isPending}
        data-testid="waypoint-add-submit"
      >
        {t("add")}
      </Button>
    </form>
  );
}

export function TripWaypoints({
  tripId,
  waypoints,
}: {
  tripId: string;
  waypoints: TripWaypoint[];
}) {
  const t = useTranslations("tripWaypoints");
  const [orderedIds, setOrderedIds] = useState(() =>
    waypoints.map((w) => w.id),
  );
  useEffect(() => {
    setOrderedIds(waypoints.map((w) => w.id));
  }, [waypoints]);

  const deleteWaypoint = useDeleteWaypointMutation(tripId);
  const reorderWaypoints = useReorderWaypointsMutation(tripId);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const byId = new Map(waypoints.map((w) => [w.id, w]));
  const orderedWaypoints = orderedIds
    .map((id) => byId.get(id))
    .filter((w): w is TripWaypoint => w !== undefined);

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = orderedIds.indexOf(String(active.id));
    const newIndex = orderedIds.indexOf(String(over.id));
    const next = arrayMove(orderedIds, oldIndex, newIndex);
    setOrderedIds(next);
    reorderWaypoints.mutate(next);
  }

  return (
    <div
      className="flex flex-col gap-4"
      data-testid="trip-waypoints"
    >
      {orderedWaypoints.length === 0 ? (
        <p className="text-c3 text-sm">{t("routeEmpty")}</p>
      ) : (
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={orderedIds}
            strategy={verticalListSortingStrategy}
          >
            <div className="flex flex-col gap-2">
              {orderedWaypoints.map((waypoint) => (
                <SortableWaypointRow
                  key={waypoint.id}
                  waypoint={waypoint}
                  onDelete={() => deleteWaypoint.mutate(waypoint.id)}
                  isDeleting={deleteWaypoint.isPending}
                />
              ))}
            </div>
          </SortableContext>
        </DndContext>
      )}
      <AddWaypointForm tripId={tripId} />
    </div>
  );
}
