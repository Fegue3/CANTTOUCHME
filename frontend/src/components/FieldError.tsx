// Inline error display used by forms across the app.

export function FieldError({ message }: { message: string | null }) {
  // Hide the error box when there is nothing to show.
  if (!message) return null;
  return <div className="notice notice--error">{message}</div>;
}
