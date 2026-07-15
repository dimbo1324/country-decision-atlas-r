import type { StorybookConfig } from "@storybook/react-vite";
import tailwindcss from "@tailwindcss/vite";

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(ts|tsx)"],
  addons: ["@storybook/addon-essentials"],
  staticDirs: ["../public"],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  // Without this, theme.css's `@theme`/`@source`/utility classes never get
  // processed by Tailwind - the browser receives them as inert CSS, so no
  // token (`--color-c1`, `h-full`, `text-c3`, ...) actually resolves.
  // apps/web-prototype's own vite.config.ts registers the same plugin the
  // same way for its (non-Storybook) dev server.
  async viteFinal(viteConfig) {
    viteConfig.plugins = viteConfig.plugins || [];
    viteConfig.plugins.push(tailwindcss());
    return viteConfig;
  },
};

export default config;
