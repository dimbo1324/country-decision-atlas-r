import type { Preview } from "@storybook/react";
import type { ReactNode } from "react";
import { initialize, mswLoader } from "msw-storybook-addon";
import "../src/tokens/theme.css";

initialize();

function ArchiveStage({ children }: { children: ReactNode }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "2.5rem",
        background: "var(--color-bg)",
        color: "var(--color-c1)",
        fontFamily: "var(--font-body)",
      }}
    >
      {children}
    </div>
  );
}

const preview: Preview = {
  parameters: {
    layout: "fullscreen",
    backgrounds: { disable: true },
  },
  loaders: [mswLoader],
  decorators: [
    (Story) => (
      <ArchiveStage>
        <Story />
      </ArchiveStage>
    ),
  ],
};

export default preview;
