import { useState } from "react";

export function CollapsableElem({
  children,
  title,
  expandedSize,
  expandHorizontally,
}: {
  children: React.ReactNode;
  title: String;
  expandedSize: number;
  expandHorizontally: boolean;
}) {
  const [showSideBar, setShowSideBar] = useState<boolean>(true);

  return (
    <div
      style={{
        width: expandHorizontally
          ? showSideBar
            ? `${expandedSize}%`
            : `7.5%`
          : `calc(100% - 2.5em)`,

        backgroundColor: "#f4f4f4",
        padding: "0em 1em",
        border: "1px solid black",
        overflow: "hidden",

        minHeight: 0,
        display: "flex",
        flexDirection: "column",
        paddingBottom: showSideBar ? "8px" : "20px",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          paddingTop: "8px",
        }}
      >
        {showSideBar && <h3 style={{ margin: 0 }}>{title}</h3>}
        <button
          style={{
            marginLeft: "auto",
          }}
          onClick={() => setShowSideBar(!showSideBar)}
        >
          {showSideBar
            ? expandHorizontally
              ? "◀"
              : "▼"
            : expandHorizontally
              ? "▶"
              : "▲"}
        </button>
      </div>

      {showSideBar && (
        <div style={{ marginTop: "1em", overflowY: "auto", flexGrow: 1 }}>
          {children}
        </div>
      )}
    </div>
  );
}
