export function FieldError({ message }: { message: string | null }) {
  if (!message) return null;
  return <div className="notice notice--error">{message}</div>;
}
