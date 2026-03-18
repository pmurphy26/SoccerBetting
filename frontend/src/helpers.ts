import { NetworkData } from "./types";

export function computeWeeklyProfit(data: NetworkData[]) {
  // Compute profit per match
  const profitPerMatch = data.map((d) => {
    if (!(d.predicted && d.bookOdds)) {
      return {
        date: new Date(d.matchInfo.matchDate),
        profit: 0,
      };
    }
    const pred = d.predicted.predictedResult;
    const actual = d.finalScore?.matchResult;

    let profit = -1; // default loss

    if (pred === actual) {
      if (pred === 0) profit = d.bookOdds.home - 1;
      else if (pred === 1) profit = d.bookOdds.draw - 1;
      else profit = d.bookOdds.away - 1;
    }

    return {
      date: new Date(d.matchInfo.matchDate),
      profit,
    };
  });

  // Group into 2‑week bins
  const buckets = new Map<string, number>();

  for (const row of profitPerMatch) {
    const year = row.date.getFullYear();
    const week = Math.floor(row.date.getDate() / 14); // 0,1,2 for each month
    const key = `${year}-${row.date.getMonth() + 1}-W${week}`;

    buckets.set(key, (buckets.get(key) || 0) + row.profit);
  }

  return {
    labels: [...buckets.keys()],
    values: [...buckets.values()],
  };
}

export function computeProfitSeries(
  data: NetworkData[],
  grouping: "weekly" | "biweekly" | "monthly"
) {
  // Compute profit per match
  const rows = data.map((d) => {
    if (!(d.predicted && d.bookOdds)) {
      return {
        date: new Date(d.matchInfo.matchDate),
        profit: 0,
      };
    }
    const pred = d.predicted.predictedResult;
    const actual = d.finalScore?.matchResult;

    let profit = -1;
    if (pred === actual) {
      if (pred === 0) profit = d.bookOdds.home - 1;
      else if (pred === 1) profit = d.bookOdds.draw - 1;
      else profit = d.bookOdds.away - 1;
    }

    return {
      date: new Date(d.matchInfo.matchDate),
      profit,
    };
  });

  // Group by chosen time window
  const buckets = new Map<string, number>();
  buckets.set("start", 0);

  for (const r of rows) {
    const d = r.date;
    const year = d.getFullYear();
    const month = d.getMonth() + 1;

    let key = "";

    if (grouping === "weekly") {
      const week = Math.floor(d.getDate() / 7);
      key = `${year}-${month}-W${week}`;
    } else if (grouping === "biweekly") {
      const bi = Math.floor(d.getDate() / 14);
      key = `${year}-${month}-B${bi}`;
    } else {
      key = `${year}-${month}`;
    }

    buckets.set(key, (buckets.get(key) || 0) + r.profit);
  }

  const labels = [...buckets.keys()];
  const values = [...buckets.values()];

  // Compute cumulative profit
  const cumulative: number[] = [];
  let running = 0;
  for (const v of values) {
    running += v;
    cumulative.push(running);
  }

  return { labels, values, cumulative };
}

/**
 * 
 *       {/*<div
         style={{
           display: "flex",
           flexWrap: "wrap",
           gap: "0.5em",
           alignItems: "center",
           marginTop: "1em",
           padding: "1em",
           border: "1px solid #ccc",
           borderRadius: "6px",
           backgroundColor: "#f9f9f9",
         }}
       >

         <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
           <strong>Leages</strong>
 
           <button
             onClick={() => {
               const newArr = !leagueFilter.every((e) => e == true)
                 ? [true, true, true, true]
                 : [false, false, false, false];
               //console.log(newArr);
               setLeagueFilter(newArr);
             }}
           >
             {leagueFilter.every((e) => e == true)
               ? "Deselect All"
               : "Select All"}
           </button>
 

           <div
             style={{
               maxHeight: "200px",
               overflowY: "auto",
               paddingLeft: "4px",
             }}
           >
             {leagueFilter.map((isSelected, idx) => {
               return (
                 <label
                   key={idx}
                   style={{ display: "flex", gap: "6px", marginBottom: "4px" }}
                 >
                   <input
                     type="checkbox"
                     checked={isSelected}
                     onChange={() => {
                       const newArr = [...leagueFilter];
                       newArr[idx] = !newArr[idx];
                       setLeagueFilter(newArr);
                     }}
                   />
                   {DICT_ID_TO_NAME[idx]}
                 </label>
               );
             })}
           </div>
         </div>
 
         <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
           <strong>Team</strong>
 
           <button
             onClick={() => {
               const allIds = Object.keys(leagueFilterDict);
               const allSelected = filters.teamID.length === allIds.length;
 
               setFilters({
                 ...filters,
                 teamID: allSelected ? [] : allIds,
               });
             }}
           >
             {filters.teamID.length === Object.keys(leagueFilterDict).length
               ? "Deselect All"
               : "Select All"}
           </button>
 
           <div
             style={{
               maxHeight: "200px",
               overflowY: "auto",
               paddingLeft: "4px",
             }}
           >
             {Object.entries(leagueFilterDict).map(([id, name]) => {
               const checked = filters.teamID.includes(id);
 
               return (
                 <label
                   key={id}
                   style={{ display: "flex", gap: "6px", marginBottom: "4px" }}
                 >
                   <input
                     type="checkbox"
                     checked={checked}
                     onChange={() => {
                       setFilters({
                         ...filters,
                         teamID: checked
                           ? filters.teamID.filter((x) => x !== id)
                           : [...filters.teamID, id],
                       });
                     }}
                   />
                   {name}
                 </label>
               );
             })}
           </div>
         </div>
 
         <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
           <input
             type="date"
             value={filters.matchStartDate}
             onChange={(e) => {
               console.log(e.target.value == "" ? "empty" : e.target.value);
               setFilters({ ...filters, matchStartDate: e.target.value });
             }}
             placeholder="Start date"
           />
 
           <span>to</span>
 
           <input
             type="date"
             value={filters.matchEndDate}
             onChange={(e) =>
               setFilters({ ...filters, matchEndDate: e.target.value })
             }
             placeholder="End date"
           />
         </div>
 
         <select
           value={filters.matchLabel}
           onChange={(e) =>
             setFilters({ ...filters, matchLabel: e.target.value })
           }
         >
           <option value="">Label</option>
           <option value={0}>Home Win</option>
           <option value={1}>Draw</option>
           <option value={2}>Away Win</option>
         </select>
 
         <input
           type="number"
           placeholder="Min Home Odds"
           value={filters.minHomeOdds}
           onChange={(e) =>
             setFilters({ ...filters, minHomeOdds: e.target.value })
           }
           style={{ width: "120px" }}
         />
 
         <input
           type="number"
           placeholder="Min Draw Odds"
           value={filters.minDrawOdds}
           onChange={(e) =>
             setFilters({ ...filters, minDrawOdds: e.target.value })
           }
           style={{ width: "120px" }}
         />
 
         <input
           type="number"
           placeholder="Min Away Odds"
           value={filters.minAwayOdds}
           onChange={(e) =>
             setFilters({ ...filters, minAwayOdds: e.target.value })
           }
           style={{ width: "120px" }}
         />
 
         <select
           value={filters.completed}
           onChange={(e) =>
             setFilters({ ...filters, completed: e.target.value })
           }
         >
           <option value="">Both</option>
           <option value="Completed">Completed</option>
           <option value="Incomplete">Not Completed</option>
         </select>
 
         <button
           onClick={() =>
             setFilters({
               teamID: [],
               matchStartDate: "",
               matchEndDate: "",
               minHomeOdds: "",
               minDrawOdds: "",
               minAwayOdds: "",
               matchLabel: "",
               completed: "",
             })
           }
         >
           Reset
         </button>
       </div>}
 
 
 */

// Poisson PMF
function poissonPMF(k: number, lambda: number): number {
  return (Math.exp(-lambda) * Math.pow(lambda, k)) / factorial(k);
}

function factorial(n: number): number {
  let result = 1;
  for (let i = 2; i <= n; i++) result *= i;
  return result;
}

export function scoreMatrix(
  lambdaHome: number,
  lambdaAway: number,
  maxGoals: number = 7
): number[][] {
  const P: number[][] = Array.from({ length: maxGoals + 1 }, () =>
    Array(maxGoals + 1).fill(0)
  );

  for (let i = 0; i <= maxGoals; i++) {
    for (let j = 0; j <= maxGoals; j++) {
      P[i][j] = poissonPMF(i, lambdaHome) * poissonPMF(j, lambdaAway);
    }
  }

  return P;
}

export function wdlFromScoreMatrix(P: number[][]): {
  homeWin: number;
  draw: number;
  awayWin: number;
} {
  const n = P.length;

  let homeWin = 0;
  let draw = 0;
  let awayWin = 0;

  for (let i = 0; i < n; i++) {
    draw += P[i][i]; // diagonal

    for (let j = 0; j < n; j++) {
      if (i > j) homeWin += P[i][j]; // lower triangle
      if (i < j) awayWin += P[i][j]; // upper triangle
    }
  }

  return { homeWin, draw, awayWin };
}

export function makePredictionFromOdds(
  odds: { homeWin: number; draw: number; awayWin: number },
  drawThreshold: number = 0.27
) {
  if (odds.draw >= drawThreshold) return 1;
  else if (odds.homeWin > odds.awayWin) return 0;
  else return 2;
}

export function filterNetworkData(
  networkDatasToFilter: NetworkData[],
  newProfit: number,
  di: Record<string, string>,
  filters: {
    teamID: string[];
    matchStartDate: string;
    matchEndDate: string;
    minHomeOdds: string;
    minDrawOdds: string;
    minAwayOdds: string;
    matchLabel: string;
    completed: string;
    useGoodBetsOnly: boolean;
  },
  goodBetFilters: {
    minBetOdds: number;
    drawThreshold: number;
    badGap: number;
  }
) {
  const filteredData = networkDatasToFilter
    .filter((d) => {
      const filterRes = passFilter(d, newProfit, di, filters, goodBetFilters);
      newProfit = filterRes.profit;
      return filterRes.res;
    })
    .sort((a, b) => {
      // Most recent first
      return (
        new Date(a.matchInfo.matchDate).getTime() -
        new Date(b.matchInfo.matchDate).getTime()
      );
    });
  return { data: filteredData, profit: newProfit };
}

function passFilter(
  d: NetworkData,
  newProfit: number,
  di: Record<string, string>,
  filters: {
    teamID: string[];
    matchStartDate: string;
    matchEndDate: string;
    minHomeOdds: string;
    minDrawOdds: string;
    minAwayOdds: string;
    matchLabel: string;
    completed: string;
    useGoodBetsOnly: boolean;
  },
  goodBetFilters: {
    minBetOdds: number;
    drawThreshold: number;
    badGap: number;
  }
) {
  const completedBool = filters.completed === "Incomplete" ? false : true;
  if (!(filters.completed == "") && !(d.matchInfo.completed == completedBool))
    return { res: false, profit: newProfit };

  if (
    !(d.matchInfo.team1ID.toString() in di) &&
    !(d.matchInfo.team2ID.toString() in di)
  )
    return { res: false, profit: newProfit };

  if (
    filters.teamID.length > 0 &&
    !filters.teamID.includes(d.matchInfo.team1ID.toString()) &&
    !filters.teamID.includes(d.matchInfo.team2ID.toString())
  )
    return { res: false, profit: newProfit };

  if (
    !(
      filters.matchStartDate == "" ||
      dateEquality(filters.matchStartDate, d.matchInfo.matchDate) <= 0
    )
  )
    return { res: false, profit: newProfit };

  if (
    !(
      filters.matchEndDate == "" ||
      dateEquality(filters.matchEndDate, d.matchInfo.matchDate) >= 0
    )
  ) {
    return { res: false, profit: newProfit };
  }

  if (
    filters.matchLabel &&
    d.finalScore &&
    d.finalScore?.matchResult !== parseInt(filters.matchLabel, 10)
  )
    return { res: false, profit: newProfit };

  if (d.bookOdds) {
    if (filters.minHomeOdds && d.bookOdds?.home < Number(filters.minHomeOdds))
      return { res: false, profit: newProfit };

    if (filters.minDrawOdds && d.bookOdds?.draw < Number(filters.minDrawOdds))
      return { res: false, profit: newProfit };

    if (filters.minAwayOdds && d.bookOdds?.away < Number(filters.minAwayOdds))
      return { res: false, profit: newProfit };

    if (filters.useGoodBetsOnly && !isGoodBet(d, goodBetFilters)) {
      return { res: false, profit: newProfit };
    }

    if (d.predicted) {
      newProfit +=
        (d.predicted.predictedResult == d.finalScore?.matchResult
          ? d.predicted.predictedResult == 0
            ? d.bookOdds.home
            : d.predicted.predictedResult == 1
            ? d.bookOdds.draw
            : d.bookOdds.away
          : 0) - 1;
    }
  }
  return { res: true, profit: newProfit };
}

function dateEquality(date1: string, date2: string) {
  if (date1 == "") {
    return -1;
  }
  if (date2 == "") {
    return 1;
  }
  return new Date(date1) > new Date(date2)
    ? 1
    : new Date(date1) < new Date(date2)
    ? -1
    : 0;
}

function isGoodBet(
  possibleBet: NetworkData,
  goodBetFilters: {
    minBetOdds: number;
    drawThreshold: number;
    badGap: number;
  }
): boolean {
  if (!(possibleBet.predicted && possibleBet.bookOdds)) {
    return false;
  }
  const pred = possibleBet.predicted.predictedResult;
  const s =
    possibleBet.bookOdds.home +
    possibleBet.bookOdds.away +
    possibleBet.bookOdds.draw;
  let bo = 0;
  let po = 0;
  if (pred == 0) {
    bo = s - possibleBet.bookOdds.home / s;
    po = possibleBet.predicted.home;
    if (possibleBet.bookOdds.home < goodBetFilters.minBetOdds) {
      return false;
    }
  } else if (pred == 1) {
    bo = s - possibleBet.bookOdds.draw / s;
    po = possibleBet.predicted.draw;
    if (possibleBet.bookOdds.draw < goodBetFilters.minBetOdds) {
      return false;
    }
  } else {
    bo = s - possibleBet.bookOdds.away / s;
    po = possibleBet.predicted.away;
    if (possibleBet.bookOdds.away < goodBetFilters.minBetOdds) {
      return false;
    }
  }
  if (Math.abs(1 / bo - po) >= goodBetFilters.badGap) return false;
  return true;
}

export function getMaxID(data: NetworkData[]): number {
  return Math.max(...data.map((d) => d.id));
}
