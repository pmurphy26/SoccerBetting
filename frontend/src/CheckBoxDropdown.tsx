import { useState, useRef, useEffect } from "react";

export function CheckboxDropdown({
  label,
  options,
  selected,
  onChange,
}: {
  label: string;
  options: { id: number; name: string }[];
  selected: number[];
  onChange: (next: number[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const names: string[] = selected
    .map((id) => options.find((o) => o.id === id))
    .filter(Boolean)
    .map((o) => o!.name);
  // Close dropdown when clicking outside
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const toggle = (id: number) => {
    if (selected.includes(id)) {
      onChange(selected.filter((x) => x !== id));
    } else {
      onChange([...selected, id]);
    }
  };

  return (
    <div ref={ref} style={{ position: "relative", width: "200px" }}>
      <button
        style={{
          all: "unset", // remove ALL default button styling
          cursor: "pointer", // still feels clickable
          color: "inherit", // inherits parent text color
          font: "inherit", // inherits parent font family/size/weight
          lineHeight: "inherit", // matches surrounding text
        }}
        onClick={(e) => {
          e.stopPropagation();

          const selected_options = selected.filter((s) =>
            options.some((o) => o.id == s),
          );

          if (selected_options.length == 0) {
            onChange([...selected, ...options.map((o) => o.id)]);
          } else {
            onChange([]);
          }
        }}
      >
        {label}
      </button>

      <div
        onClick={() => setOpen(!open)}
        style={{
          border: "1px solid #ccc",
          padding: "8px",
          borderRadius: "4px",
          cursor: "pointer",
          background: "#fff",
        }}
      >
        {selected.length === 0
          ? `Select ${label}...`
          : names.length <= 2
            ? names.join(", ")
            : `${names[0]}, ${names[1]}, ...`}
      </div>

      {open && (
        <div
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            width: "100%",
            background: "white",
            border: "1px solid #ccc",
            borderRadius: "4px",
            padding: "8px",
            zIndex: 10,
            maxHeight: "200px",
            overflowY: "auto",
          }}
        >
          {options.map((opt) => (
            <label
              key={opt.id}
              style={{ display: "flex", alignItems: "center", gap: "6px" }}
            >
              <input
                type="checkbox"
                checked={selected.includes(opt.id)}
                onChange={() => toggle(opt.id)}
              />
              {opt.name}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
