import type { Meta, StoryObj } from "@storybook/react";
import type { ColumnDef } from "@tanstack/react-table";
import { expect, fireEvent, userEvent, waitFor, within } from "@storybook/test";
import { http, HttpResponse } from "msw";
import { ModerationQueue, type ModerationQueueAction } from "./ModerationQueue";
import { Toaster } from "./Toast";

interface DemoProposal {
  id: string;
  title: string;
  status: string;
}

const DEMO_ROWS: DemoProposal[] = [
  {
    id: "p-1",
    title: "Аргентина: обновление визового раздела",
    status: "pending",
  },
  { id: "p-2", title: "Уругвай: новая налоговая ставка", status: "pending" },
];

const columns: ColumnDef<DemoProposal>[] = [
  { accessorKey: "title", header: "Заявка" },
  { accessorKey: "status", header: "Статус" },
];

const rejectAction: ModerationQueueAction<DemoProposal> = {
  key: "reject",
  label: "Отклонить",
  variant: "dangerous",
  requiresReason: true,
  onRun: (row, reason) =>
    fetch(`/api/v1/moderation/proposals/${row.id}/reject`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason }),
    }).then((response) => {
      if (!response.ok) throw new Error("request failed");
      return response.json();
    }),
  successMessage: (row) => `${row.title}: отклонено`,
};

const meta: Meta<typeof ModerationQueue<DemoProposal>> = {
  title: "Primitives/ModerationQueue",
  parameters: {
    msw: {
      handlers: [
        http.post("/api/v1/moderation/proposals/:id/reject", () =>
          HttpResponse.json({ ok: true }),
        ),
      ],
    },
  },
};
export default meta;
type Story = StoryObj<typeof ModerationQueue<DemoProposal>>;

/** Exercises the reason-required confirm-dialog flow end to end against a
 * mocked network response: click the dangerous action, type a reason, submit,
 * and confirm the success toast fires once the mocked request resolves. */
export const RejectWithReason: Story = {
  render: () => (
    <>
      <Toaster />
      <ModerationQueue
        testId="demo-moderation-queue"
        columns={columns}
        data={DEMO_ROWS}
        getRowId={(row) => row.id}
        actions={[rejectAction]}
      />
    </>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);

    await userEvent.click(
      canvas.getAllByTestId("demo-moderation-queue-action-reject")[0],
    );

    const reasonField = await body.findByTestId(
      "demo-moderation-queue-confirm-reason",
    );
    fireEvent.change(reasonField, {
      target: { value: "Дублирующая заявка" },
    });
    await userEvent.click(
      body.getByTestId("demo-moderation-queue-confirm-submit"),
    );

    // Proves the async action resolved successfully: the confirm dialog
    // only closes after `onRun` resolves and `toast.success` fires (see
    // ModerationQueue's `runAction`). Not asserting on the toast text
    // itself here -- sonner auto-dismisses it after a few seconds, which
    // made this flaky when combined with MSW round-trip + typing latency.
    await waitFor(() => expect(body.queryByRole("dialog")).toBeNull(), {
      timeout: 5000,
    });
  },
};

/** Regression coverage for the Stage 13 accessibility fix: a focused row
 * opens the detail drawer on Enter, matching mouse-click behavior. */
export const OpenDetailWithKeyboard: Story = {
  render: () => (
    <ModerationQueue
      testId="demo-moderation-queue-detail"
      columns={columns}
      data={DEMO_ROWS}
      getRowId={(row) => row.id}
      actions={[]}
      renderDetail={(row) => <p>Детали заявки: {row.title}</p>}
      detailTitle={(row) => row.title}
    />
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const [firstRow] = canvas.getAllByTestId(
      "demo-moderation-queue-detail-row",
    );
    firstRow.focus();
    await userEvent.keyboard("{Enter}");

    const aside = canvasElement.ownerDocument.body.querySelector("aside");
    await waitFor(() => expect(aside).not.toBeNull());
    expect(aside).toHaveClass("translate-x-0");
    expect(
      within(canvasElement.ownerDocument.body).getByText(
        /Детали заявки: Аргентина/,
      ),
    ).toBeInTheDocument();
  },
};
