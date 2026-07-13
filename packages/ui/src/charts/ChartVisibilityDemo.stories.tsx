import type { Meta, StoryObj } from "@storybook/react";
import { ChartVisibilityProvider } from "./useChartVisibility";
import { SparklineChart } from "./SparklineChart";
import { RadarChart } from "./RadarChart";

function randomSeries(length: number, base: number) {
  return Array.from({ length }, (_, i) => base + Math.sin(i / 2) * 3 + i * 0.4);
}

const axes = [
  "Стабильность",
  "Право",
  "Свобода",
  "Стоимость",
  "ВНЖ",
  "Качество",
];

/** Stand-in for a real chart-heavy page (`apps/web` doesn't have one yet —
 * those land in Stages 5+): a long scrollable list of charts wrapped in one
 * `ChartVisibilityProvider`. Open DevTools' Performance tab and scroll — only
 * the sparkline(s)/radar currently in view should be drawing; the rest sit
 * idle until they scroll into the `rootMargin`-padded viewport. */
function ManyCharts() {
  return (
    <ChartVisibilityProvider>
      <div
        style={{
          height: 480,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: 32,
          padding: 24,
        }}
      >
        {Array.from({ length: 10 }, (_, i) => (
          <div
            key={i}
            style={{ height: 200, flexShrink: 0 }}
          >
            {i % 2 === 0 ? (
              <SparklineChart
                values={randomSeries(14, 30 + i * 4)}
                active
                accent={i % 4 === 0 ? "gold" : "blue"}
                yAxisLabel="Индекс"
                xAxisLabel="Недели"
              />
            ) : (
              <RadarChart
                axes={axes}
                series={[
                  {
                    label: `Страна ${i}`,
                    values: axes.map(() => 40 + ((i * 7) % 50)),
                    accent: i % 3 === 0 ? "sage" : "terra",
                  },
                ]}
                active
              />
            )}
          </div>
        ))}
      </div>
    </ChartVisibilityProvider>
  );
}

const meta: Meta<typeof ManyCharts> = {
  title: "Charts/ChartVisibilityDemo",
  component: ManyCharts,
};
export default meta;
type Story = StoryObj<typeof ManyCharts>;

export const ScrollablePage: Story = {};
