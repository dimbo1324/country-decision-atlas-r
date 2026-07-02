type AIRefusalStateProps = {
  message: string;
};

export function AIRefusalState({ message }: AIRefusalStateProps) {
  return (
    <div className="notice" data-testid="ai-refusal">
      <strong>Недостаточно данных</strong>
      <p>{message}</p>
    </div>
  );
}
