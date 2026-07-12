import type { Meta, StoryObj } from "@storybook/react";
import { BackgroundFX } from "./BackgroundFX";
import { BackgroundTexture } from "./BackgroundTexture";

const meta: Meta = {
  title: "Shell/Background",
};
export default meta;
type Story = StoryObj;

export const TextureAndFX: Story = {
  render: () => (
    <div style={{ position: "relative", height: "60vh" }}>
      <BackgroundTexture />
      <BackgroundFX />
      <p
        style={{
          position: "relative",
          zIndex: 1,
          color: "var(--color-c2)",
          fontFamily: "var(--font-body)",
        }}
      >
        Paper texture + drifting gold dust, both respecting
        prefers-reduced-motion.
      </p>
    </div>
  ),
};
