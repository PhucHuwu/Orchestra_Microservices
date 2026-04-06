import { ReactNode } from "react";

type StatePanelProps = {
  title: string;
  description?: string;
  children?: ReactNode;
};

export function StatePanel({ title, description, children }: StatePanelProps) {
  return (
    <div className="card-surface rounded-2xl p-5">
      <h3 className="font-heading text-2xl text-[var(--text-strong)]">{title}</h3>
      {description ? <p className="mt-2 text-sm text-[var(--text-muted)]">{description}</p> : null}
      {children ? <div className="mt-4">{children}</div> : null}
    </div>
  );
}
