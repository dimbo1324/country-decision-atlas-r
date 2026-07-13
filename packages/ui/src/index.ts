export { cn } from "./lib/cn";
export { ACCENTS, type Accent } from "./lib/accents";
export { readCssVar, withAlpha } from "./lib/color";
export type { Confidence } from "./lib/confidence";

export { useCanvasLoop, lerp } from "./hooks/useCanvasLoop";
export { useReducedMotion } from "./hooks/useReducedMotion";

export { BackgroundTexture } from "./shell/BackgroundTexture";
export { BackgroundFX } from "./shell/BackgroundFX";

export { Card } from "./primitives/Card";
export { Button } from "./primitives/Button";
export { Kicker } from "./primitives/Kicker";
export { Icon, IconFrame } from "./primitives/Icon";
export { Counter } from "./primitives/Counter";
export { MetricCard } from "./primitives/MetricCard";
export { ChartFrame, MetricStat } from "./primitives/ChartFrame";
export { DataTable, type DataTableColumn } from "./primitives/DataTable";
export { Drawer } from "./primitives/Drawer";
export { Accordion, type AccordionItem } from "./primitives/Accordion";
export { Toggle } from "./primitives/Toggle";
export { TimelineList, type TimelineEvent } from "./primitives/TimelineList";
export { SignalTicker } from "./primitives/SignalTicker";

export {
  Dialog,
  DialogTrigger,
  DialogClose,
  DialogContent,
} from "./primitives/Dialog";
export {
  Popover,
  PopoverTrigger,
  PopoverAnchor,
  PopoverContent,
} from "./primitives/Popover";
export {
  TooltipProvider,
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "./primitives/Tooltip";
export { Tabs, TabsList, TabsTrigger, TabsContent } from "./primitives/Tabs";
export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectItem,
} from "./primitives/Select";
export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuGroup,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "./primitives/DropdownMenu";
export { Slider } from "./primitives/Slider";

export { Toaster, toast } from "./primitives/Toast";
export { Field, FieldLabel, FieldHint, FieldError } from "./primitives/Field";
export { RadioCards, type RadioCardOption } from "./primitives/RadioCards";
export { Pagination } from "./primitives/Pagination";
export { Breadcrumbs, type BreadcrumbItem } from "./primitives/Breadcrumbs";

export { Badge, type BadgeVariant } from "./primitives/Badge";
export { EmptyState } from "./primitives/EmptyState";
export { LoadingState } from "./primitives/LoadingState";
export { Skeleton } from "./primitives/Skeleton";
export { ErrorState } from "./primitives/ErrorState";

export type {
  ChartMode,
  ChartDatum,
  DonutSegment,
  HeatmapData,
  RankFlowSeries,
  DriftBoardRow,
  PassportData,
  LegalSignalEvent,
  CriteriaWeight,
} from "./charts/types";
export { accentCssVar } from "./charts/types";
export {
  ChartVisibilityProvider,
  useChartVisible,
} from "./charts/useChartVisibility";
export { RadarChart, type RadarSeries } from "./charts/RadarChart";
export { SparklineChart } from "./charts/SparklineChart";
export { DivergingMeter } from "./charts/DivergingMeter";
export { ProgressRing } from "./charts/ProgressRing";
export { GaugeArc } from "./charts/GaugeArc";
export { DonutChart } from "./charts/DonutChart";
export { Heatmap } from "./charts/Heatmap";
export { RankFlow } from "./charts/RankFlow";
export { BarColumns } from "./charts/BarColumns";
export { DriftBoard } from "./charts/DriftBoard";
export { PassportCard } from "./charts/PassportCard";
export { LegalSignalTimeline } from "./charts/LegalSignalTimeline";
export { CriteriaWeightBars } from "./charts/CriteriaWeightBars";
