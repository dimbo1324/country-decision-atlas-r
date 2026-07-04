type AIDisclaimerProps = {
  text: string;
};

export function AIDisclaimer({ text }: AIDisclaimerProps) {
  return (
    <p
      className="infoNote"
      data-testid="ai-disclaimer"
    >
      {text}
    </p>
  );
}
