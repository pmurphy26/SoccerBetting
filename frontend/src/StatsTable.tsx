import { useRef, useState } from "react";
import { LABEL_TO_STRING, TEAM_ID_TO_NAME } from "./constants";
import { NetworkData } from "./types";

export function NetworkDataStatsTable({
  networkDataArr,
  profit,
  showMatchInfo,
  showBookOdds,
  showScores,
  showLabels,
  showPredictedOdds,
}: {
  networkDataArr: NetworkData[];
  profit: number;
  showMatchInfo: boolean;
  showBookOdds: boolean;
  showScores: boolean;
  showLabels: boolean;
  showPredictedOdds: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [currentPage, setCurrentPage] = useState<number>(0);
  const [resultsPerPage, setResultsPerPage] = useState<number>(15);

  if (networkDataArr.length > 0) {
    return (
      <div ref={ref}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: "1em",
            padding: "1em",
            border: "1px solid #ccc",
            borderRadius: "6px",
            backgroundColor: "#f9f9f9",
            gap: "0.5em",
          }}
        >
          <h3
            style={{
              textAlign: "left",
              width: "100%",
              margin: 0,
            }}
          >
            Profit: {profit.toFixed(3)}
          </h3>

          <label
            style={{
              display: "flex",
              justifyContent: "flex-end",
              width: "100%",
              alignItems: "center",
            }}
          >
            Results per page:&nbsp;
            <select
              value={resultsPerPage}
              onChange={(e) => {
                setResultsPerPage(Number(e.target.value));
                setCurrentPage(0);
              }}
            >
              {[0, 5, 10, 15, 20, 25].map((val) => (
                <option key={val} value={val}>
                  {val}
                </option>
              ))}
            </select>
          </label>
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #ccc" }}>
              {showMatchInfo && (
                <>
                  <th style={{ padding: "8px" }}>Date</th>
                  <th style={{ padding: "8px" }}>Team 1</th>
                  <th style={{ padding: "8px" }}>Team 2</th>
                </>
              )}
              {showBookOdds && (
                <>
                  <th style={{ padding: "8px" }}>Home</th>
                  <th style={{ padding: "8px" }}>Draw</th>
                  <th style={{ padding: "8px" }}>Away</th>
                </>
              )}
              {showPredictedOdds && (
                <>
                  <th style={{ padding: "8px" }}>Home</th>
                  <th style={{ padding: "8px" }}>Draw</th>
                  <th style={{ padding: "8px" }}>Away</th>
                </>
              )}
              {showScores && (
                <>
                  <th style={{ padding: "8px" }}>Home Score</th>
                  <th style={{ padding: "8px" }}>Away Score</th>
                </>
              )}
              {showLabels && (
                <>
                  <th style={{ padding: "8px" }}>Label</th>
                  <th style={{ padding: "8px" }}>Predicted Label</th>
                  <th style={{ padding: "8px" }}>Correct Guess</th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {networkDataArr
              .slice(
                currentPage * resultsPerPage,
                currentPage * resultsPerPage + resultsPerPage,
              )
              .map((d, i) => (
                <tr key={i} style={{ borderTop: "1px solid #ddd" }}>
                  {showMatchInfo && (
                    <>
                      <td style={{ padding: "8px" }}>
                        {d.matchInfo.matchDate}
                      </td>
                      <td style={{ padding: "8px" }}>
                        {TEAM_ID_TO_NAME[d.matchInfo.team1ID]}
                      </td>
                      <td style={{ padding: "8px" }}>
                        {TEAM_ID_TO_NAME[d.matchInfo.team2ID]}
                      </td>
                    </>
                  )}
                  {showBookOdds && (
                    <>
                      <td style={{ padding: "8px" }}>
                        {d.bookOdds?.home ?? "—"}
                      </td>
                      <td style={{ padding: "8px" }}>
                        {d.bookOdds?.draw ?? "—"}
                      </td>
                      <td style={{ padding: "8px" }}>
                        {d.bookOdds?.away ?? "—"}
                      </td>
                    </>
                  )}
                  {showPredictedOdds && (
                    <>
                      <td style={{ padding: "8px" }}>
                        {(1 / d?.predicted?.home)?.toFixed(2) ?? "—"}
                      </td>
                      <td style={{ padding: "8px" }}>
                        {(1 / d?.predicted?.draw)?.toFixed(2) ?? "—"}
                      </td>
                      <td style={{ padding: "8px" }}>
                        {(1 / d?.predicted?.away)?.toFixed(2) ?? "—"}
                      </td>
                    </>
                  )}
                  {showScores && (
                    <>
                      <td style={{ padding: "8px" }}>
                        {d.finalScore?.home ?? "Not played"}
                      </td>
                      <td style={{ padding: "8px" }}>
                        {d.finalScore?.away ?? "—"}
                      </td>
                    </>
                  )}
                  {showLabels && (
                    <>
                      <td style={{ padding: "8px" }}>
                        {LABEL_TO_STRING[Number(d.finalScore?.matchResult)] ??
                          "—"}
                      </td>
                      <td style={{ padding: "8px" }}>
                        {LABEL_TO_STRING[d.predicted?.predictedResult] ?? "—"}
                      </td>
                      <td style={{ padding: "8px" }}>
                        {String(
                          d.predicted?.predictedResult ==
                            d.finalScore?.matchResult,
                        )}
                      </td>
                    </>
                  )}
                  {showMatchInfo && <td>{String(d?.id ?? "n/a")}</td>}
                </tr>
              ))}
          </tbody>
        </table>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: "1em",
            padding: "1em",
            border: "1px solid #ccc",
            borderRadius: "6px",
            backgroundColor: "#f9f9f9",
            gap: "0.5em",
          }}
        >
          {/* Jump to first */}
          <div
            style={{ width: "20%", display: "flex", justifyContent: "left" }}
          >
            <button
              onClick={() => setCurrentPage(0)}
              style={{ fontWeight: "normal" }}
            >
              &lt;&lt;
            </button>
          </div>

          {/* Left-most: Previous Page */}
          <div
            style={{
              width: "20%",
              display: "flex",
              justifyContent: "center",
            }}
          >
            {currentPage > 0 && (
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                style={{ fontWeight: "normal" }}
              >
                &lt;
              </button>
            )}
          </div>

          {/* Center text */}
          <div style={{ width: "20%", textAlign: "center" }}>
            <h4 style={{ margin: 0 }}>
              Results {currentPage * resultsPerPage} -{" "}
              {Math.min(
                (currentPage + 1) * resultsPerPage,
                networkDataArr.length,
              )}{" "}
              of {networkDataArr.length}
            </h4>
          </div>

          {/* Next page */}
          <div
            style={{ width: "20%", display: "flex", justifyContent: "center" }}
          >
            {(currentPage + 1) * resultsPerPage < networkDataArr.length && (
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                style={{ fontWeight: "normal" }}
              >
                &gt;
              </button>
            )}
          </div>

          {/* Jump to last */}
          <div
            style={{
              width: "20%",
              display: "flex",
              justifyContent: "flex-end",
            }}
          >
            <button
              onClick={() =>
                setCurrentPage(
                  Math.trunc(networkDataArr.length / resultsPerPage),
                )
              }
              style={{ fontWeight: "normal" }}
            >
              &gt;&gt;
            </button>
          </div>
        </div>
      </div>
    );
  } else if (networkDataArr.length === 0) {
    return (
      <div
        ref={ref}
        style={{
          borderTop: "4px solid white",
        }}
      >
        No new data fetched yet
      </div>
    );
  } else {
    return (
      <div
        ref={ref}
        style={{
          borderTop: "4px solid white",
        }}
      >
        Failed to get Filtered Data
      </div>
    );
  }
}
