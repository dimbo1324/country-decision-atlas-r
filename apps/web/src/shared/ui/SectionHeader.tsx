type SectionHeaderProps = {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: React.ReactNode;
};

export function SectionHeader({
  eyebrow,
  title,
  description,
  actions,
}: SectionHeaderProps) {
  return (
    <header className="sectionHeaderBlock">
      <div className="sectionHeaderMain">
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h2 className="sectionHeaderTitle">{title}</h2>
        {description && <p className="sectionHeaderDesc">{description}</p>}
      </div>
      {actions && <div className="sectionHeaderActions">{actions}</div>}
    </header>
  );
}
