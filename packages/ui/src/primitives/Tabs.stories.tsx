import type { Meta, StoryObj } from "@storybook/react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./Tabs";

const meta: Meta<typeof Tabs> = {
  title: "Primitives/Tabs",
};
export default meta;
type Story = StoryObj<typeof Tabs>;

export const Default: Story = {
  render: () => (
    <Tabs defaultValue="overview">
      <TabsList>
        <TabsTrigger value="overview">Обзор</TabsTrigger>
        <TabsTrigger value="cii">CII</TabsTrigger>
        <TabsTrigger value="trust">Доверие</TabsTrigger>
      </TabsList>
      <TabsContent value="overview">Обзор досье страны.</TabsContent>
      <TabsContent value="cii">Разбор индекса CII по компонентам.</TabsContent>
      <TabsContent value="trust">Скор доверия и структура источников.</TabsContent>
    </Tabs>
  ),
};
