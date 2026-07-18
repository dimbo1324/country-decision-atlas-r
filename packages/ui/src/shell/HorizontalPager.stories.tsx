import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, waitFor, within } from "@storybook/test";
import { HorizontalPager, type DeckSlide } from "./HorizontalPager";

const slides: DeckSlide[] = [
  {
    id: "countries",
    navLabel: "Страны",
    accent: "gold",
    content: <p data-testid="slide-content-countries">Обзор стран.</p>,
  },
  {
    id: "scenarios",
    navLabel: "Сценарии",
    accent: "blue",
    content: <p data-testid="slide-content-scenarios">Победители сценариев.</p>,
  },
  {
    id: "signals",
    navLabel: "Сигналы",
    accent: "terra",
    content: (
      <p data-testid="slide-content-signals">Последние правовые сигналы.</p>
    ),
  },
];

function ControlledPager() {
  const [index, setIndex] = useState(0);
  return (
    <div style={{ height: 320, position: "relative" }}>
      <HorizontalPager
        slides={slides}
        index={index}
        onIndexChange={setIndex}
      />
    </div>
  );
}

const meta: Meta<typeof HorizontalPager> = {
  title: "Shell/HorizontalPager",
};
export default meta;
type Story = StoryObj<typeof HorizontalPager>;

export const Default: Story = {
  render: () => <ControlledPager />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    const firstSlide = canvas.getByTestId("pager-slide-countries");
    const secondSlide = canvas.getByTestId("pager-slide-scenarios");

    expect(firstSlide).not.toHaveAttribute("inert");
    expect(secondSlide).toHaveAttribute("inert");

    await userEvent.click(canvas.getByTestId("pager-next"));

    await waitFor(() => {
      expect(firstSlide).toHaveAttribute("inert");
      expect(secondSlide).not.toHaveAttribute("inert");
    });

    await userEvent.click(canvas.getByTestId("pager-prev"));

    await waitFor(() => {
      expect(firstSlide).not.toHaveAttribute("inert");
      expect(secondSlide).toHaveAttribute("inert");
    });
  },
};
