import type { Meta, StoryObj } from "@storybook/react";
import { Field, FieldError, FieldHint, FieldLabel } from "./Field";

const meta: Meta = {
  title: "Primitives/Field",
};
export default meta;
type Story = StoryObj;

export const WithHint: Story = {
  render: () => (
    <div style={{ maxWidth: 320 }}>
      <Field>
        <FieldLabel htmlFor="email">Email</FieldLabel>
        <input
          id="email"
          type="email"
          style={{
            background: "var(--color-bg2)",
            border: "1px solid rgb(239 230 212 / 0.09)",
            color: "var(--color-c1)",
            padding: "10px 14px",
            fontFamily: "var(--font-body)",
          }}
        />
        <FieldHint>Используется для входа и уведомлений безопасности.</FieldHint>
      </Field>
    </div>
  ),
};

export const WithError: Story = {
  render: () => (
    <div style={{ maxWidth: 320 }}>
      <Field>
        <FieldLabel htmlFor="email-error">Email</FieldLabel>
        <input
          id="email-error"
          type="email"
          defaultValue="not-an-email"
          style={{
            background: "var(--color-bg2)",
            border: "1px solid var(--color-terra2)",
            color: "var(--color-c1)",
            padding: "10px 14px",
            fontFamily: "var(--font-body)",
          }}
        />
        <FieldError>Введите корректный email.</FieldError>
      </Field>
    </div>
  ),
};
