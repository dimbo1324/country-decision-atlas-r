type AIDisclaimerProps = {
  text: string;
};

export function AIDisclaimer({ text }: AIDisclaimerProps) {
  return (
    <p
      className="disclaimer-notice"
      role="note"
      data-testid="ai-disclaimer"
    >
      {text}
    </p>
  );
}
