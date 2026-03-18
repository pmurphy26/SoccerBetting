import { useEffect, useRef, useState } from "react";
import Chart from "chart.js/auto";
import { computeProfitSeries, computeWeeklyProfit } from "./helpers";
import { NetworkData, TimeGrouping } from "./types";

export default function ProfitChart({
  data,
  grouping,
}: {
  data: NetworkData[];
  grouping: "weekly" | "biweekly" | "monthly";
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    //console.log(data[0]);
    const { labels, cumulative } = computeProfitSeries(data, grouping);

    if (chartRef.current) chartRef.current.destroy();
    const datasets = [
      {
        label: "Cumulative Profit",
        data: cumulative,
        borderColor: "#4a90e2",
        backgroundColor: "rgba(74,144,226,0.2)",
        tension: 0.25,
        borderWidth: 2,
        fill: true,
      },
      /*...[0, 1, 2].map((n) => {
        return {
          label: "Cumulative Profit",
          data: cumulative.filter((c, i) => Number(labels[i]) == n),
          borderColor: "#4ae2daff",
          backgroundColor: "rgba(74,144,226,0.2)",
          tension: 0.25,
          borderWidth: 2,
          fill: true,
        };
      }),*/
    ];
    chartRef.current = new Chart(canvasRef.current, {
      type: "line",
      data: {
        labels,
        datasets: datasets,
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true },
        },
      },
    });
  }, [data, grouping]);

  return <canvas ref={canvasRef} style={{ width: "100%", height: "400px" }} />;
}
